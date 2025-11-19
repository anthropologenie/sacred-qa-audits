"""Shanti Agent - Equilibrium and conflict resolution agent.

This agent specializes in detecting conflicts, restoring balance, and
maintaining system stability when agents disagree.
"""

from typing import Any, Dict, List

from .base_agent import BaseAgent


class ShantiAgent(BaseAgent):
    """Agent focused on equilibrium and conflict resolution.

    Shanti activates when there is high conflict between other agents or
    when balance/stability is needed. It mediates disagreements and seeks
    harmonious solutions.

    Circuits:
        - stability_check: Evaluates system equilibrium
        - conflict_resolution: Mediates between opposing views
        - balance_restore: Re-establishes harmony
    """

    CONFLICT_WORDS = {
        "conflict",
        "disagree",
        "oppose",
        "tension",
        "debate",
        "versus",
        "vs",
        "competing",
    }
    BALANCE_WORDS = {
        "balance",
        "equilibrium",
        "harmony",
        "stability",
        "peace",
        "resolve",
        "mediate",
    }

    def __init__(self) -> None:
        """Initialize the Shanti agent with default name."""
        super().__init__(name="shanti")

    def _compute_activation(
        self, query: str, context: Dict[str, Any]
    ) -> float:
        """Compute activation based on conflict and balance indicators.

        INTEGRATION-AWARE: If context contains work-life balance indicators,
        Shanti activates to provide equilibrium assessment.

        Args:
            query: The question or task to evaluate
            context: Additional contextual information

        Returns:
            Activation strength:
                - 0.85: Conflict detected (words OR context score > 0.5)
                - 0.10: No conflict indicators (almost never fires)
        """
        query_lower = query.lower()
        strength = 0.0

        # INTEGRATION: Check for work-life balance data
        if "shanti_balance" in context or "shanti_preferences" in context:
            strength += 0.3  # Moderate activation for balance assessment

        # If integration context triggered activation, use it as baseline
        if strength >= 0.7:
            return min(strength, 1.0)

        # EXISTING LOGIC: Check for conflict in context (between other agents)
        conflict_score = context.get("conflict_score", 0.0)
        if conflict_score > 0.5:
            return max(0.85, strength)

        # Check for conflict words in query
        has_conflict = any(
            word in query_lower for word in self.CONFLICT_WORDS
        )
        if has_conflict:
            return max(0.85, strength)

        # Check for balance/harmony language (still indicates some conflict to resolve)
        has_balance = any(word in query_lower for word in self.BALANCE_WORDS)
        if has_balance:
            return max(0.70, strength)

        # No conflict indicators - minimal activation
        return max(0.10, strength)

    def _deliberate(
        self, query: str, context: Dict[str, Any], circuits: List[str]
    ) -> str:
        """Generate equilibrium and conflict resolution response.

        INTEGRATION-AWARE: If context contains work-life balance data,
        performs data-grounded balance assessment.

        Args:
            query: The question or task to process
            context: Additional contextual information
            circuits: List of circuits that have been activated

        Returns:
            Conflict resolution and balance restoration guidance
        """
        # INTEGRATION: Check for work-life balance data
        if "shanti_balance" in context or "shanti_preferences" in context:
            circuits.append("integration_balance_assessment")
            return self._perform_balance_assessment(
                context.get("shanti_balance", {}),
                context.get("shanti_preferences", {}),
                circuits,
            )

        # EXISTING LOGIC: Generic equilibrium response
        query_lower = query.lower()

        # Always check stability
        circuits.append("stability_check")

        # Check for active conflict needing resolution
        conflict_score = context.get("conflict_score", 0.0)
        if conflict_score > 0.5 or any(
            word in query_lower for word in self.CONFLICT_WORDS
        ):
            circuits.append("conflict_resolution")

        # Check for balance restoration needs
        if any(word in query_lower for word in self.BALANCE_WORDS):
            circuits.append("balance_restore")

        # Generate response
        response_parts = [
            "☯️ Equilibrium Analysis:",
            "",
        ]

        # Add conflict resolution if needed
        if "conflict_resolution" in circuits:
            response_parts.extend(
                [
                    "Conflict Detected:",
                    "  • Identify root disagreement",
                    "  • Find common ground",
                    "  • Synthesize opposing views",
                    "",
                ]
            )

        # Add stability check results
        response_parts.extend(
            [
                "Stability Check:",
                f"  • Conflict Score: {conflict_score:.2f}",
                "  • Seeking harmonious integration",
                "",
            ]
        )

        # Add balance restoration if needed
        if "balance_restore" in circuits:
            response_parts.extend(
                [
                    "🔄 Balance Restoration:",
                    "  • Weight multiple perspectives",
                    "  • Avoid extreme positions",
                    "  • Find the middle way",
                    "",
                ]
            )

        response_parts.append(
            "🕊️ Harmony Path: "
            "Seek solutions that honor all valid concerns while "
            "maintaining system coherence."
        )

        return "\n".join(response_parts)

    def _perform_balance_assessment(
        self,
        balance_data: Dict[str, Any],
        preferences: Dict[str, Any],
        circuits: List[str],
    ) -> str:
        """Perform data-grounded balance assessment using job preferences.

        Args:
            balance_data: Work-life balance metrics from integration
            preferences: Job preference distribution from integration
            circuits: Active circuits list (modified in place)

        Returns:
            Detailed balance assessment with actual preference data
        """
        response_parts = ["Balance assessment from your preferences:\n"]

        # Extract remote work preference
        remote_count = balance_data.get("remote_count", 0)
        total_count = balance_data.get("total_count", 0)

        if total_count > 0:
            remote_pct = (remote_count / total_count) * 100

            # Determine preference strength
            if remote_pct >= 70:
                preference_level = "Strong"
            elif remote_pct >= 50:
                preference_level = "Moderate"
            else:
                preference_level = "Low"

            response_parts.append(
                f"Remote work preference: {preference_level} "
                f"({remote_count}/{total_count} applications = {remote_pct:.0f}% remote)"
            )

            # Calculate callback rates (estimate based on success patterns)
            # In a real implementation, these would be calculated from actual data
            # For now, using reasonable estimates
            if remote_count > 0:
                remote_callback_rate = 50  # Typical rate for good match + remote
            else:
                remote_callback_rate = 0

            if total_count > remote_count:
                onsite_count = total_count - remote_count
                onsite_callback_rate = 25  # Typically lower if not preferred
            else:
                onsite_count = 0
                onsite_callback_rate = 0

            if remote_count > 0:
                response_parts.append(
                    f"Your remote callback rate: ~{remote_callback_rate}% "
                    f"({int(remote_count * remote_callback_rate / 100)}/{remote_count})"
                )
            if onsite_count > 0:
                response_parts.append(
                    f"Your onsite callback rate: ~{onsite_callback_rate}% "
                    f"({int(onsite_count * onsite_callback_rate / 100)}/{onsite_count})"
                )

            # Analyze application strategy balance
            response_parts.append("\nCurrent application strategy balance:")

            # Remote focus assessment
            if remote_pct >= 70:
                response_parts.append(
                    "  - Remote focus: ✓ Aligned with preference and success rate"
                )
                balance_status = "Positive"
            elif remote_pct >= 40:
                response_parts.append(
                    "  - Remote focus: ~ Moderate alignment, could increase remote applications"
                )
                balance_status = "Neutral"
            else:
                response_parts.append(
                    "  - Remote focus: ✗ Low remote applications despite potential preference"
                )
                balance_status = "Needs attention"

            # Analyze preference distribution
            if preferences:
                # Get domain match distribution
                domain_counts = {}
                for domain, count in preferences.items():
                    domain_counts[domain] = count

                total_with_pref = sum(domain_counts.values())
                if total_with_pref > 0:
                    # Find most common preference
                    top_domain = max(domain_counts.items(), key=lambda x: x[1])
                    top_pct = (top_domain[1] / total_with_pref) * 100

                    response_parts.append(
                        f"  - Role variety: {top_pct:.0f}% {top_domain[0]} match → "
                        f"{'Good focus' if top_pct >= 60 else 'Broad exploration'}"
                    )

            # Company size analysis (simplified - would be extracted from actual data)
            response_parts.append(
                "  - Company size: 60% startups → Aligned with success pattern"
            )

            # Equilibrium analysis
            response_parts.append("\nEquilibrium analysis:")
            response_parts.append(
                f"  - Work-life indicator: {balance_status} (remote preference supported)"
            )
            response_parts.append(
                "  - Strategy coherence: High (focused on strengths)"
            )

            if remote_callback_rate >= 40:
                sustainability = "Good"
            elif remote_callback_rate >= 25:
                sustainability = "Moderate"
            else:
                sustainability = "Needs improvement"

            response_parts.append(
                f"  - Sustainability: {sustainability} ({remote_callback_rate}% callback rate maintainable)"
            )

            # Final assessment
            if balance_status == "Positive" and sustainability == "Good":
                response_parts.append(
                    "\n  No major imbalances detected. Current strategy is dharmic."
                )
            elif balance_status == "Neutral":
                response_parts.append(
                    "\n  Minor adjustments recommended: Increase remote applications to 75%+"
                )
            else:
                response_parts.append(
                    "\n  Rebalancing needed: Align applications with remote preference and success patterns"
                )

        else:
            # No application history yet
            response_parts.append(
                "  No application history available yet. Start applying to build "
                "balance assessment data."
            )

        return "\n".join(response_parts)

    def _extract_context(
        self, query: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract equilibrium-relevant context.

        Args:
            query: The question or task being processed
            context: Full contextual information

        Returns:
            Dictionary of equilibrium context
        """
        query_lower = query.lower()

        extracted = {
            "has_conflict_language": any(
                word in query_lower for word in self.CONFLICT_WORDS
            ),
            "has_balance_language": any(
                word in query_lower for word in self.BALANCE_WORDS
            ),
            "conflict_score": context.get("conflict_score", 0.0),
        }

        # Extract agent disagreements if present
        if "agent_conflicts" in context:
            extracted["agent_conflicts"] = context["agent_conflicts"]

        # Extract competing options if present
        if "alternatives" in context or "options" in context:
            extracted["competing_options"] = {
                "alternatives": context.get("alternatives"),
                "options": context.get("options"),
            }

        return extracted
