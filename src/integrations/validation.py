"""Parliament Validation - Accuracy tracking and threshold calibration.

This module provides tools to measure Parliament's historical accuracy and
suggest activation threshold adjustments for continuous improvement.

The ParliamentValidator analyzes logged decisions against real outcomes to:
1. Calculate accuracy metrics (overall, by agent, by confidence level)
2. Generate human-readable accuracy reports
3. Suggest threshold adjustments to improve calibration
"""

import json
from typing import Any, Dict, List, Optional

from .jobs_db_integration import JobsDBIntegration


class ParliamentValidator:
    """Validates Parliament accuracy and suggests calibration adjustments.

    This class analyzes historical Parliament decisions logged in the database
    and compares them against real-world outcomes to measure accuracy and
    suggest improvements.

    Attributes:
        db: JobsDBIntegration instance for database access
    """

    def __init__(self, db_integration: JobsDBIntegration):
        """Initialize the validator.

        Args:
            db_integration: JobsDBIntegration instance (must be connected)
        """
        self.db = db_integration

        if not self.db.connected:
            raise ConnectionError(
                "JobsDBIntegration must be connected before validation"
            )

    def calculate_accuracy_metrics(self) -> Dict[str, Any]:
        """Calculate Parliament's historical accuracy metrics.

        Analyzes logged decisions with known outcomes to compute:
        - Overall accuracy rates
        - Accuracy by confidence level (high/medium/low)
        - Accuracy by recommendation type (apply/skip)
        - Per-agent accuracy and activation patterns

        Returns:
            Dictionary with structure:
            {
                'total_decisions': int,
                'decisions_with_outcomes': int,
                'accuracy': {
                    'recommendation_followed': float,  # % of times user followed advice
                    'callback_prediction': float,      # % of times callback prediction was correct
                    'overall_accuracy': float          # Combined accuracy metric
                },
                'by_recommendation': {
                    'apply': {'count': int, 'success_rate': float},
                    'skip': {'count': int, 'correct_rate': float}
                },
                'by_confidence': {
                    'high': {'count': int, 'accuracy': float, 'avg_outcome': float},
                    'medium': {'count': int, 'accuracy': float, 'avg_outcome': float},
                    'low': {'count': int, 'accuracy': float, 'avg_outcome': float}
                },
                'by_agent': {
                    'krudi': {'accuracy': float, 'sample_size': int, 'activation_rate': float},
                    'smriti': {'accuracy': float, 'sample_size': int, 'activation_rate': float},
                    ...
                }
            }
        """
        cursor = self.db.cursor

        # Get all decisions
        cursor.execute(
            """
            SELECT id, agents_active, confidence, applied, callback,
                   interview, offer, outcome_date
            FROM parliament_decisions
            """
        )
        all_decisions = cursor.fetchall()

        total_decisions = len(all_decisions)

        # Filter decisions with outcomes
        decisions_with_outcomes = [
            d for d in all_decisions if d[7] is not None  # outcome_date
        ]

        decisions_with_outcomes_count = len(decisions_with_outcomes)

        if decisions_with_outcomes_count == 0:
            return {
                'total_decisions': total_decisions,
                'decisions_with_outcomes': 0,
                'note': 'No decisions with outcomes yet. Use "log" command to record outcomes.'
            }

        # Initialize metrics
        metrics = {
            'total_decisions': total_decisions,
            'decisions_with_outcomes': decisions_with_outcomes_count,
            'accuracy': {},
            'by_recommendation': {
                'apply': {'count': 0, 'success_count': 0, 'success_rate': 0.0},
                'skip': {'count': 0, 'correct_count': 0, 'correct_rate': 0.0}
            },
            'by_confidence': {
                'high': {'count': 0, 'accurate': 0, 'accuracy': 0.0, 'total_outcome_score': 0},
                'medium': {'count': 0, 'accurate': 0, 'accuracy': 0.0, 'total_outcome_score': 0},
                'low': {'count': 0, 'accurate': 0, 'accuracy': 0.0, 'total_outcome_score': 0}
            },
            'by_agent': {}
        }

        recommendation_followed_count = 0
        callback_predictions_correct = 0
        total_accuracy_score = 0.0

        # Analyze each decision with outcome
        for decision in decisions_with_outcomes:
            (decision_id, agents_json, confidence, applied, callback,
             interview, offer, outcome_date) = decision

            # Parse agents
            try:
                agents = json.loads(agents_json) if agents_json else []
            except json.JSONDecodeError:
                agents = []

            # Categorize by confidence level
            if confidence >= 0.7:
                conf_level = 'high'
                recommendation = 'apply'
            elif confidence >= 0.5:
                conf_level = 'medium'
                recommendation = 'apply'
            else:
                conf_level = 'low'
                recommendation = 'skip'

            metrics['by_confidence'][conf_level]['count'] += 1

            # Calculate outcome score (0-3: no response, callback, interview, offer)
            outcome_score = (
                (1 if callback else 0) +
                (1 if interview else 0) +
                (1 if offer else 0)
            )
            metrics['by_confidence'][conf_level]['total_outcome_score'] += outcome_score

            # Track if user followed recommendation
            if recommendation == 'apply' and applied:
                recommendation_followed_count += 1
            elif recommendation == 'skip' and not applied:
                recommendation_followed_count += 1

            # Track recommendation outcomes
            if recommendation == 'apply':
                metrics['by_recommendation']['apply']['count'] += 1
                if applied and (callback or interview or offer):
                    metrics['by_recommendation']['apply']['success_count'] += 1
            else:  # skip
                metrics['by_recommendation']['skip']['count'] += 1
                if not applied or not (callback or interview or offer):
                    metrics['by_recommendation']['skip']['correct_count'] += 1

            # Predict callback based on confidence
            positive_outcome = callback or interview or offer
            predicted_callback = confidence >= 0.7

            if predicted_callback == positive_outcome:
                callback_predictions_correct += 1
                metrics['by_confidence'][conf_level]['accurate'] += 1

            # Calculate decision accuracy score (0-1)
            decision_accuracy = self._calculate_decision_accuracy(
                confidence, applied, callback, interview, offer
            )
            total_accuracy_score += decision_accuracy

            # Track by agent
            for agent_name in agents:
                if agent_name not in metrics['by_agent']:
                    metrics['by_agent'][agent_name] = {
                        'activations': 0,
                        'accurate': 0,
                        'total_confidence': 0.0,
                        'total_outcome_score': 0
                    }

                metrics['by_agent'][agent_name]['activations'] += 1
                metrics['by_agent'][agent_name]['total_confidence'] += confidence
                metrics['by_agent'][agent_name]['total_outcome_score'] += outcome_score

                if predicted_callback == positive_outcome:
                    metrics['by_agent'][agent_name]['accurate'] += 1

        # Calculate percentages
        metrics['accuracy']['recommendation_followed'] = (
            recommendation_followed_count / decisions_with_outcomes_count
        )
        metrics['accuracy']['callback_prediction'] = (
            callback_predictions_correct / decisions_with_outcomes_count
        )
        metrics['accuracy']['overall_accuracy'] = (
            total_accuracy_score / decisions_with_outcomes_count
        )

        # Calculate recommendation success rates
        apply_count = metrics['by_recommendation']['apply']['count']
        if apply_count > 0:
            metrics['by_recommendation']['apply']['success_rate'] = (
                metrics['by_recommendation']['apply']['success_count'] / apply_count
            )

        skip_count = metrics['by_recommendation']['skip']['count']
        if skip_count > 0:
            metrics['by_recommendation']['skip']['correct_rate'] = (
                metrics['by_recommendation']['skip']['correct_count'] / skip_count
            )

        # Calculate confidence level accuracies
        for level in ['high', 'medium', 'low']:
            count = metrics['by_confidence'][level]['count']
            if count > 0:
                metrics['by_confidence'][level]['accuracy'] = (
                    metrics['by_confidence'][level]['accurate'] / count
                )
                metrics['by_confidence'][level]['avg_outcome'] = (
                    metrics['by_confidence'][level]['total_outcome_score'] / count
                )

        # Calculate agent accuracies and activation rates
        for agent_name, data in metrics['by_agent'].items():
            activations = data['activations']
            if activations > 0:
                data['accuracy'] = data['accurate'] / activations
                data['avg_confidence'] = data['total_confidence'] / activations
                data['avg_outcome'] = data['total_outcome_score'] / activations
                data['activation_rate'] = activations / decisions_with_outcomes_count

            # Clean up intermediate calculation fields
            data['sample_size'] = activations
            del data['total_confidence']
            del data['total_outcome_score']
            del data['accurate']

        return metrics

    def generate_accuracy_report(self) -> str:
        """Generate human-readable accuracy report.

        Creates a formatted text report summarizing Parliament's accuracy
        metrics in a clear, actionable format.

        Returns:
            Multi-line string containing the formatted report
        """
        metrics = self.calculate_accuracy_metrics()

        if 'note' in metrics:
            return f"""
PARLIAMENT ACCURACY REPORT
═══════════════════════════════════════════════

{metrics['note']}

Total Decisions: {metrics['total_decisions']}
With Known Outcomes: {metrics['decisions_with_outcomes']}
"""

        # Build report
        report = f"""
PARLIAMENT ACCURACY REPORT
═══════════════════════════════════════════════

Total Decisions: {metrics['total_decisions']}
With Known Outcomes: {metrics['decisions_with_outcomes']}

Overall Accuracy: {metrics['accuracy']['overall_accuracy']:.1%}
  • Recommendation Followed: {metrics['accuracy']['recommendation_followed']:.1%}
  • Callback Prediction: {metrics['accuracy']['callback_prediction']:.1%}

═══════════════════════════════════════════════
BY RECOMMENDATION TYPE
═══════════════════════════════════════════════
"""

        # Apply recommendations
        apply_count = metrics['by_recommendation']['apply']['count']
        apply_rate = metrics['by_recommendation']['apply']['success_rate']
        report += f"\nAPPLY recommendations: {apply_count}\n"
        report += f"  Success rate: {apply_rate:.1%}"
        if apply_count > 0:
            report += f" (led to callback/interview/offer)\n"
        else:
            report += "\n"

        # Skip recommendations
        skip_count = metrics['by_recommendation']['skip']['count']
        skip_rate = metrics['by_recommendation']['skip']['correct_rate']
        report += f"\nSKIP recommendations: {skip_count}\n"
        report += f"  Correct rate: {skip_rate:.1%}"
        if skip_count > 0:
            report += f" (avoided poor outcomes)\n"
        else:
            report += "\n"

        # By confidence level
        report += f"""
═══════════════════════════════════════════════
BY CONFIDENCE LEVEL
═══════════════════════════════════════════════
"""

        for level in ['high', 'medium', 'low']:
            data = metrics['by_confidence'][level]
            if data['count'] > 0:
                report += f"\n{level.upper()} (confidence "
                if level == 'high':
                    report += "≥70%)"
                elif level == 'medium':
                    report += "50-70%)"
                else:
                    report += "<50%)"

                report += f"\n  Count: {data['count']}"
                report += f"\n  Accuracy: {data['accuracy']:.1%}"
                report += f"\n  Avg Outcome: {data['avg_outcome']:.2f}/3.0"
                report += "\n"

        # Agent accuracy
        report += f"""
═══════════════════════════════════════════════
AGENT ACCURACY
═══════════════════════════════════════════════
"""

        # Sort agents by accuracy (descending)
        sorted_agents = sorted(
            metrics['by_agent'].items(),
            key=lambda x: x[1]['accuracy'],
            reverse=True
        )

        agent_names_full = {
            'krudi': 'Krudi (Reality)',
            'smriti': 'Smriti (Memory)',
            'parva': 'Parva (Causality)',
            'rudi': 'Rudi (Transformation)',
            'maya': 'Maya (Simulation)',
            'shanti': 'Shanti (Equilibrium)',
            'kshana': 'Kshana (Synthesis)'
        }

        for agent_name, data in sorted_agents:
            full_name = agent_names_full.get(agent_name, agent_name.capitalize())
            sample_size = data['sample_size']
            accuracy = data['accuracy']
            activation_rate = data['activation_rate']

            report += f"\n{full_name}:"
            report += f"\n  Accuracy: {accuracy:.1%}"
            report += f"\n  Sample Size: {sample_size} activations"
            report += f"\n  Activation Rate: {activation_rate:.1%}"
            report += f"\n  Avg Outcome: {data['avg_outcome']:.2f}/3.0"
            report += "\n"

        # Calibration status
        report += f"""
═══════════════════════════════════════════════
CALIBRATION STATUS
═══════════════════════════════════════════════
"""

        calibration_notes = self._assess_calibration(metrics)
        report += "\n" + "\n".join(calibration_notes) + "\n"

        return report

    def suggest_threshold_adjustments(self) -> Dict[str, float]:
        """Analyze accuracy and suggest activation threshold adjustments.

        Examines each agent's accuracy, activation rate, and outcome correlation
        to suggest threshold changes:
        - If agent is too pessimistic (high accuracy, low activation): increase threshold
        - If agent is too optimistic (low accuracy, high activation): decrease threshold
        - Adjustments are in the range [-0.15, +0.15] for stability

        Returns:
            Dictionary mapping agent names to suggested threshold adjustments:
            {'krudi': +0.05, 'smriti': -0.10, ...}
        """
        metrics = self.calculate_accuracy_metrics()

        if 'note' in metrics:
            return {'note': metrics['note']}

        adjustments = {}

        for agent_name, data in metrics['by_agent'].items():
            accuracy = data['accuracy']
            activation_rate = data['activation_rate']
            sample_size = data['sample_size']

            # Skip if sample size too small
            if sample_size < 3:
                adjustments[agent_name] = 0.0
                continue

            # Calculate suggested adjustment
            # Base adjustment on deviation from ideal 70% accuracy
            accuracy_deviation = accuracy - 0.70

            # Base adjustment on activation rate (ideal ~60% for good sparsity)
            activation_deviation = activation_rate - 0.60

            # Combine signals:
            # - If too accurate but rarely activates → lower threshold (activate more)
            # - If inaccurate but frequently activates → raise threshold (activate less)

            adjustment = 0.0

            if accuracy > 0.75 and activation_rate < 0.40:
                # Too conservative - lower threshold to activate more
                adjustment = -0.10
            elif accuracy > 0.80 and activation_rate < 0.50:
                # Very conservative - encourage more participation
                adjustment = -0.15
            elif accuracy < 0.60 and activation_rate > 0.70:
                # Over-eager and inaccurate - raise threshold
                adjustment = +0.15
            elif accuracy < 0.65 and activation_rate > 0.60:
                # Somewhat over-eager - moderate increase
                adjustment = +0.10
            elif accuracy < 0.70 and activation_rate > 0.50:
                # Slightly over-eager - small increase
                adjustment = +0.05
            elif accuracy > 0.70 and activation_rate < 0.50:
                # Accurate but too quiet - small decrease
                adjustment = -0.05

            # Cap adjustments at +/- 0.15 for stability
            adjustment = max(-0.15, min(0.15, adjustment))

            adjustments[agent_name] = adjustment

        return adjustments

    def _calculate_decision_accuracy(
        self,
        confidence: float,
        applied: bool,
        callback: bool,
        interview: bool,
        offer: bool
    ) -> float:
        """Calculate accuracy score for a single decision.

        Measures how well the Parliament's confidence matched the outcome:
        - High confidence → positive outcome = accurate (1.0)
        - Low confidence → negative outcome = accurate (1.0)
        - Mismatches = inaccurate (0.0 to 0.5 depending on severity)

        Args:
            confidence: Parliament confidence (0-1)
            applied: Whether user applied
            callback: Whether got callback
            interview: Whether got interview
            offer: Whether got offer

        Returns:
            Accuracy score from 0.0 to 1.0
        """
        # Calculate outcome score (0-3)
        outcome_score = (
            (1 if callback else 0) +
            (1 if interview else 0) +
            (1 if offer else 0)
        )

        # Normalize to 0-1
        normalized_outcome = outcome_score / 3.0

        # Compare confidence to outcome
        # Perfect match = 1.0, complete mismatch = 0.0
        accuracy = 1.0 - abs(confidence - normalized_outcome)

        return accuracy

    def _assess_calibration(self, metrics: Dict[str, Any]) -> List[str]:
        """Assess calibration status and generate recommendations.

        Args:
            metrics: Accuracy metrics from calculate_accuracy_metrics()

        Returns:
            List of calibration assessment strings
        """
        notes = []

        overall_accuracy = metrics['accuracy']['overall_accuracy']

        if overall_accuracy >= 0.75:
            notes.append("✓ Well-calibrated (accuracy ≥75%)")
        elif overall_accuracy >= 0.65:
            notes.append("⚠ Moderately calibrated (accuracy 65-75%)")
            notes.append("  Consider threshold adjustments to improve accuracy")
        else:
            notes.append("✗ Needs calibration (accuracy <65%)")
            notes.append("  Recommend running 'calibrate' command for threshold suggestions")

        # Check confidence calibration
        high_conf = metrics['by_confidence']['high']
        low_conf = metrics['by_confidence']['low']

        if high_conf['count'] > 0 and high_conf['avg_outcome'] >= 2.0:
            notes.append("✓ High-confidence decisions lead to good outcomes")
        elif high_conf['count'] > 0 and high_conf['avg_outcome'] < 1.5:
            notes.append("⚠ High-confidence decisions underperforming")
            notes.append("  Agents may be over-confident - consider raising thresholds")

        if low_conf['count'] > 0 and low_conf['avg_outcome'] <= 1.0:
            notes.append("✓ Low-confidence decisions correctly identify poor fits")
        elif low_conf['count'] > 0 and low_conf['avg_outcome'] > 1.5:
            notes.append("⚠ Low-confidence decisions missing opportunities")
            notes.append("  Agents may be too pessimistic - consider lowering thresholds")

        # Check agent diversity
        activation_rates = [
            data['activation_rate']
            for data in metrics['by_agent'].values()
        ]

        if activation_rates:
            avg_activation = sum(activation_rates) / len(activation_rates)
            if avg_activation > 0.80:
                notes.append("⚠ Agents activating too frequently (low sparsity)")
                notes.append("  Consider raising activation thresholds globally")
            elif avg_activation < 0.30:
                notes.append("⚠ Agents activating too rarely (high sparsity)")
                notes.append("  Consider lowering activation thresholds globally")

        return notes
