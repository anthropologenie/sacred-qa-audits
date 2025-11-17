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
        "or",
        "alternative",
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

        Args:
            query: The question or task to evaluate
            context: Additional contextual information

        Returns:
            Activation strength:
                - 0.95: High conflict detected in context
                - 0.80: Conflict language in query
                - 0.60: Balance/harmony language present
                - 0.25: No conflict or balance indicators
        """
        query_lower = query.lower()

        # Check for conflict in context (between other agents)
        conflict_score = context.get("conflict_score", 0.0)
        if conflict_score > 0.7:
            return 0.95

        # Check for conflict words in query
        has_conflict = any(
            word in query_lower for word in self.CONFLICT_WORDS
        )
        if has_conflict:
            return 0.80

        # Check for balance/harmony language
        has_balance = any(word in query_lower for word in self.BALANCE_WORDS)
        if has_balance:
            return 0.60

        return 0.25

    def _deliberate(
        self, query: str, context: Dict[str, Any], circuits: List[str]
    ) -> str:
        """Generate equilibrium and conflict resolution response.

        Args:
            query: The question or task to process
            context: Additional contextual information
            circuits: List of circuits that have been activated

        Returns:
            Conflict resolution and balance restoration guidance
        """
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
