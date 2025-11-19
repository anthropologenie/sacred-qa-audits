"""Rudi Agent - Transformation and adaptation agent.

This agent specializes in identifying when adaptation, learning, or
transformation is needed in the system.
"""

from typing import Any, Dict, List

from .base_agent import BaseAgent


class RudiAgent(BaseAgent):
    """Agent focused on transformation and adaptive learning.

    Rudi activates when the system needs to adapt, learn from experience,
    or undergo transformation. It identifies opportunities for evolution
    and triggers mutation pathways.

    Circuits:
        - adaptation_pathway: Charts course for system evolution
        - learning_update: Integrates new knowledge
        - mutation_trigger: Initiates transformative changes
    """

    ADAPTATION_WORDS = {
        "adapt",
        "change",
        "evolve",
        "transform",
        "shift",
        "modify",
        "adjust",
        "update",
    }
    LEARNING_WORDS = {
        "learn",
        "improve",
        "refine",
        "iterate",
        "feedback",
        "lesson",
        "experience",
    }

    def __init__(self) -> None:
        """Initialize the Rudi agent with default name."""
        super().__init__(name="rudi")

    def _compute_activation(
        self, query: str, context: Dict[str, Any]
    ) -> float:
        """Compute activation based on adaptation and learning indicators.

        INTEGRATION-AWARE: If context contains learning progress data,
        Rudi activates strongly to provide transformation analysis.

        Args:
            query: The question or task to evaluate
            context: Additional contextual information

        Returns:
            Activation strength:
                - 0.90: Strong transformation/mutation language
                - 0.80: Adaptation/evolution/change focus
                - 0.15: No transformation indicators
        """
        query_lower = query.lower()
        strength = 0.0

        # INTEGRATION: Check for learning/growth data
        if "rudi_learning" in context or "rudi_growth" in context:
            strength += 0.4  # Strong activation for transformation analysis

        # If integration context triggered high activation, return early
        if strength >= 0.7:
            return min(strength, 1.0)

        # EXISTING LOGIC: Keyword-based activation
        # Check for transformation/mutation language
        has_transformation = any(
            word in query_lower
            for word in ["transform", "mutation", "revolution", "radical"]
        )
        if has_transformation:
            return max(0.90, strength)

        # Check for strong adaptation keywords
        strong_adaptation_words = ["adapt", "evolve", "transform"]
        has_strong_adaptation = any(
            word in query_lower for word in strong_adaptation_words
        )
        if has_strong_adaptation:
            return max(0.80, strength)

        # Check for learning/improvement in context of system evolution
        if "learn" in query_lower or "evolve" in query_lower:
            return max(0.80, strength)

        # Generic change words are too common - lower activation
        generic_change = any(
            word in query_lower
            for word in ["change", "modify", "adjust", "update"]
        )
        if generic_change:
            # Only activate if it's about system change, not data change
            if any(
                word in query_lower
                for word in ["system", "architecture", "approach", "strategy"]
            ):
                return max(0.70, strength)
            return max(0.15, strength)

        # No transformation indicators
        return max(0.15, strength)

    def _deliberate(
        self, query: str, context: Dict[str, Any], circuits: List[str]
    ) -> str:
        """Generate transformation and adaptation response.

        INTEGRATION-AWARE: If context contains learning progress data,
        performs data-grounded transformation analysis.

        Args:
            query: The question or task to process
            context: Additional contextual information
            circuits: List of circuits that have been activated

        Returns:
            Transformation and learning guidance
        """
        # INTEGRATION: Check for learning progress data
        if "rudi_learning" in context:
            circuits.append("integration_transformation_analysis")
            return self._perform_transformation_analysis(
                context.get("rudi_learning", {}),
                context.get("rudi_growth", {}),
                circuits,
            )

        # EXISTING LOGIC: Generic transformation response
        query_lower = query.lower()

        # Append adaptation pathway circuit
        circuits.append("adaptation_pathway")

        # Check for learning/feedback needs
        if any(word in query_lower for word in self.LEARNING_WORDS):
            circuits.append("learning_update")

        # Check for transformation/mutation needs
        if any(
            word in query_lower
            for word in ["transform", "radical", "revolution", "mutation"]
        ):
            circuits.append("mutation_trigger")

        # Generate response
        response_parts = [
            "🦋 Transformation Analysis:",
            "",
        ]

        # Add mutation trigger if relevant
        if "mutation_trigger" in circuits:
            response_parts.extend(
                [
                    "⚡ Mutation Trigger Detected:",
                    "  • Identify transformation catalyst",
                    "  • Map transition pathway",
                    "  • Prepare for discontinuous change",
                    "",
                ]
            )

        # Add learning update if relevant
        if "learning_update" in circuits:
            response_parts.extend(
                [
                    "📚 Learning Integration:",
                    "  • Extract lessons from experience",
                    "  • Update internal models",
                    "  • Apply feedback loops",
                    "",
                ]
            )

        # Always include adaptation pathway
        response_parts.extend(
            [
                "🔄 Adaptation Pathway:",
                "  1. Recognize need for change",
                "  2. Design transformation steps",
                "  3. Execute adaptive evolution",
                "  4. Integrate learnings",
                "",
            ]
        )

        response_parts.append(
            "🌱 Evolution Principle: "
            "Systems must adapt to survive. Embrace continuous learning "
            "and transformative growth."
        )

        return "\n".join(response_parts)

    def _perform_transformation_analysis(
        self,
        learning_data: Dict[str, Any],
        growth_data: Dict[str, Any],
        circuits: List[str],
    ) -> str:
        """Perform data-grounded transformation analysis using real learning data.

        Args:
            learning_data: Learning progress metrics from integration
            growth_data: Growth potential analysis from integration
            circuits: Active circuits list (modified in place)

        Returns:
            Detailed transformation analysis with real data
        """
        response_parts = ["Transformation analysis from your learning history:\n"]

        # Get metrics
        total_sessions = learning_data.get("total_sessions", 0)
        total_minutes = learning_data.get("total_minutes", 0)
        avg_improvement = learning_data.get("avg_improvement", 0.0)

        if total_sessions > 0:
            response_parts.append(f"Current trajectory ({total_sessions} learning sessions):")

            # Calculate confidence trends by category from growth data
            if growth_data:
                trends = []
                for category, details in growth_data.items():
                    session_count = details.get("session_count", 0)
                    current_confidence = details.get("current_confidence")

                    if session_count > 0 and current_confidence:
                        # Estimate progress (simplified - in reality would track over time)
                        estimated_start = max(1.0, current_confidence - avg_improvement)
                        progress = current_confidence - estimated_start

                        # Estimate timeframe (rough approximation)
                        if total_sessions >= 10:
                            months = 3
                        elif total_sessions >= 5:
                            months = 2
                        else:
                            months = 1

                        trends.append({
                            "category": category,
                            "start": estimated_start,
                            "current": current_confidence,
                            "progress": progress,
                            "months": months,
                        })

                # Sort by progress (highest first)
                trends.sort(key=lambda x: x["progress"], reverse=True)

                # Show top 3 trends
                for trend in trends[:3]:
                    response_parts.append(
                        f"  - {trend['category']}: Confidence {trend['start']:.1f} → "
                        f"{trend['current']:.1f} (progress: +{trend['progress']:.1f} in "
                        f"{trend['months']} month{'s' if trend['months'] > 1 else ''})"
                    )

                response_parts.append("\nGrowth potential analysis:")

                if trends:
                    # Identify highest momentum
                    top_trend = trends[0]
                    response_parts.append(
                        f"  - {top_trend['category']}: High momentum "
                        f"(+{top_trend['progress']:.1f} in {top_trend['months']} months)"
                    )

                    # Recommend next focus
                    if top_trend["current"] < 3.5:
                        response_parts.append(
                            f"  - Recommended focus: Continue {top_trend['category']}, "
                            f"target 3.5/5 proficiency"
                        )

                        # Calculate expected timeline
                        gap = 3.5 - top_trend["current"]
                        months_rate = top_trend["progress"] / top_trend["months"]
                        if months_rate > 0:
                            months_to_target = gap / months_rate
                            response_parts.append(
                                f"  - Expected readiness: 3.5/5 in {months_to_target:.0f} "
                                f"months with consistent practice"
                            )
                    else:
                        response_parts.append(
                            f"  - Recommended focus: Build on {top_trend['category']} strength, "
                            f"add advanced topics"
                        )

                    # Transformation pathway
                    response_parts.append("\nTransformation pathway:")
                    response_parts.append(
                        f"  1. Complete {top_trend['category']} fundamentals "
                        f"({max(1, int(months_to_target)) if 'months_to_target' in locals() else 2} months)"
                    )
                    response_parts.append(
                        "  2. Target intermediate roles (3/5 requirement)"
                    )
                    response_parts.append(
                        f"  3. Build portfolio with real {top_trend['category'].lower()} projects"
                    )

                    # Growth ROI estimate
                    if avg_improvement > 0.5:
                        roi = "Short-term (1-3 months to job-ready)"
                    elif avg_improvement > 0.3:
                        roi = "Medium-term (3-6 months to job-ready)"
                    else:
                        roi = "Long-term (6+ months to job-ready)"

                    response_parts.append(f"\n  Growth ROI: {roi}")

            else:
                # No growth data, show basic stats
                hours = total_minutes / 60
                response_parts.append(
                    f"  - Total learning time: {hours:.1f} hours"
                )
                response_parts.append(
                    f"  - Average improvement per session: +{avg_improvement:.1f} confidence points"
                )
                response_parts.append(
                    "\n  Transformation pathway: Continue consistent learning practice"
                )

        else:
            # No learning sessions yet
            response_parts.append(
                "  No learning sessions tracked yet. Start tracking your progress to "
                "enable data-driven transformation analysis."
            )

        return "\n".join(response_parts)

    def _extract_context(
        self, query: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract transformation-relevant context.

        Args:
            query: The question or task being processed
            context: Full contextual information

        Returns:
            Dictionary of transformation context
        """
        query_lower = query.lower()

        extracted = {
            "has_adaptation_language": any(
                word in query_lower for word in self.ADAPTATION_WORDS
            ),
            "has_learning_language": any(
                word in query_lower for word in self.LEARNING_WORDS
            ),
        }

        # Extract feedback/lessons if present
        if "feedback" in context or "lessons" in context:
            extracted["learning_context"] = {
                "feedback": context.get("feedback"),
                "lessons": context.get("lessons"),
            }

        # Extract previous state for transformation comparison
        if "previous_state" in context or "current_state" in context:
            extracted["state_transition"] = {
                "previous": context.get("previous_state"),
                "current": context.get("current_state"),
            }

        return extracted
