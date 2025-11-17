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

        Args:
            query: The question or task to evaluate
            context: Additional contextual information

        Returns:
            Activation strength:
                - 0.90: Strong need for adaptation/transformation
                - 0.75: Learning or improvement focus
                - 0.55: Change or modification suggested
                - 0.35: Stable/static context
        """
        query_lower = query.lower()

        # Check for transformation/mutation language
        has_transformation = any(
            word in query_lower
            for word in ["transform", "mutation", "revolution", "radical"]
        )
        if has_transformation:
            return 0.90

        # Check for learning language
        has_learning = any(
            word in query_lower for word in self.LEARNING_WORDS
        )
        if has_learning:
            return 0.75

        # Check for adaptation language
        has_adaptation = any(
            word in query_lower for word in self.ADAPTATION_WORDS
        )
        if has_adaptation:
            return 0.55

        return 0.35

    def _deliberate(
        self, query: str, context: Dict[str, Any], circuits: List[str]
    ) -> str:
        """Generate transformation and adaptation response.

        Args:
            query: The question or task to process
            context: Additional contextual information
            circuits: List of circuits that have been activated

        Returns:
            Transformation and learning guidance
        """
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
