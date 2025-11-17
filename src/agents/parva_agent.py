"""Parva Agent - Temporal causality and consequence modeling agent.

This agent specializes in analyzing temporal relationships, causal chains,
and downstream consequences of decisions.
"""

from typing import Any, Dict, List

from .base_agent import BaseAgent


class ParvaAgent(BaseAgent):
    """Agent focused on temporal causality and consequence modeling.

    Parva activates when queries involve time-based reasoning, causal
    relationships, or consequence analysis. It helps trace ripple effects
    and understand temporal flows.

    Circuits:
        - consequence_modeling: Maps out downstream effects
        - ripple_analysis: Traces cascading impacts
        - temporal_flow: Analyzes time-based sequences
    """

    TEMPORAL_WORDS = {
        "after",
        "before",
        "when",
        "then",
        "next",
        "later",
        "eventually",
        "timeline",
        "sequence",
    }
    CAUSALITY_WORDS = {
        "because",
        "cause",
        "effect",
        "result",
        "consequence",
        "impact",
        "lead",
        "trigger",
    }

    def __init__(self) -> None:
        """Initialize the Parva agent with default name."""
        super().__init__(name="parva")

    def _compute_activation(
        self, query: str, context: Dict[str, Any]
    ) -> float:
        """Compute activation based on temporal and causal indicators.

        Args:
            query: The question or task to evaluate
            context: Additional contextual information

        Returns:
            Activation strength based on temporal/causal content:
                - 0.90: High temporal + causal language
                - 0.75: Strong temporal or causal focus
                - 0.50: Some temporal/causal elements
                - 0.30: Minimal temporal/causal content
        """
        query_lower = query.lower()

        # Count temporal and causal indicators
        temporal_count = sum(
            1 for word in self.TEMPORAL_WORDS if word in query_lower
        )
        causality_count = sum(
            1 for word in self.CAUSALITY_WORDS if word in query_lower
        )

        # Compute activation based on presence and density
        if temporal_count >= 2 and causality_count >= 1:
            return 0.90
        elif temporal_count >= 2 or causality_count >= 2:
            return 0.75
        elif temporal_count >= 1 or causality_count >= 1:
            return 0.50
        else:
            return 0.30

    def _deliberate(
        self, query: str, context: Dict[str, Any], circuits: List[str]
    ) -> str:
        """Generate temporal-causal analysis response.

        Args:
            query: The question or task to process
            context: Additional contextual information
            circuits: List of circuits that have been activated

        Returns:
            Temporal causality analysis
        """
        query_lower = query.lower()

        # Append consequence modeling circuit
        circuits.append("consequence_modeling")

        # Check for ripple/cascading effects
        if any(
            word in query_lower
            for word in ["impact", "effect", "consequence", "ripple"]
        ):
            circuits.append("ripple_analysis")

        # Check for temporal sequencing
        if any(
            word in query_lower
            for word in ["sequence", "timeline", "order", "flow"]
        ):
            circuits.append("temporal_flow")

        # Generate response
        response_parts = [
            "⏳ Temporal Causality Analysis:",
            "",
            "Consequence Chain:",
        ]

        # Add temporal flow if relevant
        if "temporal_flow" in circuits:
            response_parts.extend(
                [
                    "  → Immediate effects (T+0)",
                    "  → Short-term consequences (T+1)",
                    "  → Long-term ripples (T+n)",
                    "",
                ]
            )

        # Add ripple analysis if relevant
        if "ripple_analysis" in circuits:
            response_parts.extend(
                [
                    "Ripple Effects:",
                    "  • Direct stakeholder impacts",
                    "  • Cascading system changes",
                    "  • Emergent downstream patterns",
                    "",
                ]
            )

        response_parts.append(
            "🔗 Causal Link: Consider the full temporal chain from "
            "decision → action → immediate result → downstream consequence."
        )

        return "\n".join(response_parts)

    def _extract_context(
        self, query: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract temporal-causal relevant context.

        Args:
            query: The question or task being processed
            context: Full contextual information

        Returns:
            Dictionary of temporal-causal context
        """
        query_lower = query.lower()

        extracted = {
            "has_temporal_language": any(
                word in query_lower for word in self.TEMPORAL_WORDS
            ),
            "has_causal_language": any(
                word in query_lower for word in self.CAUSALITY_WORDS
            ),
        }

        # Extract timeline if present
        if "timeline" in context:
            extracted["timeline"] = context["timeline"]

        # Extract historical context if present
        if "history" in context or "previous" in context:
            extracted["historical_context"] = {
                "history": context.get("history"),
                "previous": context.get("previous"),
            }

        return extracted
