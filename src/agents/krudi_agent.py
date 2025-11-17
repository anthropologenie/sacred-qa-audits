"""Krudi Agent - Reality grounding and embodied constraints agent.

This agent specializes in grounding speculative or decision-oriented queries
in reality, embodied constraints, and sovereignty principles.
"""

from typing import Any, Dict, List

from .base_agent import BaseAgent


class KrudiAgent(BaseAgent):
    """Agent focused on reality grounding and embodied constraints.

    Krudi activates strongly when queries involve speculation combined with
    decision-making, ensuring that plans remain grounded in reality,
    embodied constraints, and community sovereignty.

    Activation priorities:
        - Highest (0.95): Speculative decision-making (needs strong grounding)
        - High (0.75): Pure decision-making (needs reality checks)
        - Medium (0.60): Pure speculation (needs anchoring)
        - Low (0.40): General queries (minimal grounding needed)
    """

    DECISION_WORDS = {"should", "implement", "build"}
    SPECULATION_WORDS = {"maybe", "theoretically", "could", "might", "possibly"}

    def __init__(self) -> None:
        """Initialize the Krudi agent with default name."""
        super().__init__(name="krudi")

    def _compute_activation(
        self, query: str, context: Dict[str, Any]
    ) -> float:
        """Compute activation based on decision and speculation indicators.

        Krudi activates most strongly when speculation meets decision-making,
        as these queries most need reality grounding.

        Args:
            query: The question or task to evaluate
            context: Additional contextual information

        Returns:
            Activation strength:
                - 0.95: Decision + Speculation (maximum grounding needed)
                - 0.75: Decision only (reality checks needed)
                - 0.60: Speculation only (anchoring needed)
                - 0.40: Neither (minimal intervention)
        """
        query_lower = query.lower()

        # Check for decision words
        has_decision = any(word in query_lower for word in self.DECISION_WORDS)

        # Check for speculation words
        has_speculation = any(
            word in query_lower for word in self.SPECULATION_WORDS
        )

        # Compute activation strength based on combination
        if has_decision and has_speculation:
            # Speculative decision-making - needs strongest grounding
            return 0.95
        elif has_decision:
            # Pure decision - needs reality checks
            return 0.75
        elif has_speculation:
            # Pure speculation - needs anchoring
            return 0.60
        else:
            # General query - minimal grounding
            return 0.40

    def _deliberate(
        self, query: str, context: Dict[str, Any], circuits: List[str]
    ) -> str:
        """Generate grounding-focused response with reality constraints.

        Applies reality anchoring and checks for embodied and sovereignty
        constraints based on query content.

        Args:
            query: The question or task to process
            context: Additional contextual information
            circuits: List of circuits that have been activated

        Returns:
            Grounding-focused response emphasizing reality constraints
        """
        query_lower = query.lower()

        # Always append reality anchor circuit
        circuits.append("reality_anchor")

        # Check for embodied implementation concerns
        if "build" in query_lower or "deploy" in query_lower:
            circuits.append("embodied_grounding")

        # Check for sovereignty and community concerns
        if "community" in query_lower or "krecosystem" in query_lower:
            circuits.append("sovereignty_alignment")

        # Perform reality constraint analysis
        constraints = self._analyze_reality_constraints(query, context)

        # Generate grounding-focused response
        response_parts = [
            "🌍 Reality Grounding Analysis:",
            "",
        ]

        # Add constraint warnings if any
        if constraints:
            response_parts.append("Embodied Constraints Detected:")
            for constraint in constraints:
                response_parts.append(f"  • {constraint}")
            response_parts.append("")

        # Add circuit-specific guidance
        if "embodied_grounding" in circuits:
            response_parts.append(
                "⚡ Embodied Implementation Check: "
                "Consider physical/material resources, "
                "infrastructure requirements, and deployment complexity."
            )
            response_parts.append("")

        if "sovereignty_alignment" in circuits:
            response_parts.append(
                "🏛️ Sovereignty Alignment: "
                "Ensure community autonomy, distributed governance, "
                "and preservation of local decision-making power."
            )
            response_parts.append("")

        # Add general reality anchor
        response_parts.append(
            "⚓ Reality Anchor: "
            "Ground this in concrete steps, measurable outcomes, "
            "and actual resource availability. "
            "What is the minimal viable implementation?"
        )

        return "\n".join(response_parts)

    def _analyze_reality_constraints(
        self, query: str, context: Dict[str, Any]
    ) -> List[str]:
        """Analyze and identify reality constraints in the query.

        Args:
            query: The question or task being analyzed
            context: Additional contextual information

        Returns:
            List of identified reality constraints
        """
        constraints = []
        query_lower = query.lower()

        # Check for resource constraints
        if any(
            word in query_lower
            for word in ["scale", "large", "complex", "enterprise"]
        ):
            constraints.append(
                "Scale complexity: Large-scale implementations require "
                "infrastructure, maintenance, and operational overhead"
            )

        # Check for time constraints
        if any(
            word in query_lower for word in ["quickly", "fast", "immediate"]
        ):
            constraints.append(
                "Time pressure: Rapid deployment may sacrifice quality, "
                "testing, and community alignment"
            )

        # Check for theoretical/abstract elements
        if any(
            word in query_lower
            for word in ["theoretical", "abstract", "ideal", "perfect"]
        ):
            constraints.append(
                "Abstraction gap: Theoretical models must be translated "
                "into concrete, implementable steps"
            )

        # Check for dependency complexity
        if any(
            word in query_lower
            for word in ["integrate", "connect", "combine", "merge"]
        ):
            constraints.append(
                "Integration complexity: Dependencies introduce "
                "maintenance burden and potential failure points"
            )

        return constraints

    def _extract_context(
        self, query: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract reality-grounding relevant context.

        Focuses on extracting information about constraints, resources,
        and embodied factors.

        Args:
            query: The question or task being processed
            context: Full contextual information

        Returns:
            Dictionary of grounding-relevant context
        """
        extracted = {
            "query_length": len(query),
            "has_decision_language": any(
                word in query.lower() for word in self.DECISION_WORDS
            ),
            "has_speculation_language": any(
                word in query.lower() for word in self.SPECULATION_WORDS
            ),
        }

        # Extract resource-related context if present
        if "resources" in context:
            extracted["resources"] = context["resources"]

        # Extract timeline context if present
        if "timeline" in context:
            extracted["timeline"] = context["timeline"]

        # Extract scope context if present
        if "scope" in context:
            extracted["scope"] = context["scope"]

        # Extract community context if present
        if "community" in context or "stakeholders" in context:
            extracted["community_context"] = {
                "community": context.get("community"),
                "stakeholders": context.get("stakeholders"),
            }

        return extracted
