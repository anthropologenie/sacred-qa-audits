"""Smriti Agent - Memory and pattern recognition agent.

This agent specializes in retrieving historical context, recognizing patterns,
and tracing lineages from past decisions and experiences.
"""

from typing import Any, Dict, List

from agents.base_agent import BaseAgent


class SmritiAgent(BaseAgent):
    """Agent focused on memory and pattern recognition.

    Smriti activates when historical context, pattern recognition, or
    lineage tracing is relevant. It helps learn from the past and
    recognize recurring patterns.

    Circuits:
        - history_retrieval: Accesses historical context
        - pattern_recognition: Identifies recurring patterns
        - lineage_trace: Traces decision ancestry
    """

    MEMORY_WORDS = {
        "remember",
        "history",
        "past",
        "previous",
        "before",
        "earlier",
        "pattern",
        "recurring",
    }
    LEARNING_WORDS = {
        "lesson",
        "lessons",
        "experience",
        "precedent",
        "similar",
        "analogy",
    }

    def __init__(self) -> None:
        """Initialize the Smriti agent with default name."""
        super().__init__(name="smriti")

    def _compute_activation(
        self, query: str, context: Dict[str, Any]
    ) -> float:
        """Compute activation based on historical and pattern indicators.

        Args:
            query: The question or task to evaluate
            context: Additional contextual information

        Returns:
            Activation strength:
                - 0.90: Explicit pattern/recurring language
                - 0.80: History/past/lessons explicitly mentioned
                - 0.15: No history indicators
        """
        query_lower = query.lower()

        # Check for explicit pattern/history language
        has_pattern = "pattern" in query_lower or "recurring" in query_lower
        if has_pattern:
            return 0.90

        # Check for strong historical keywords
        strong_history = [
            "history",
            "past",
            "previous",
            "lessons",
            "precedent",
        ]
        has_strong_history = any(
            word in query_lower for word in strong_history
        )
        if has_strong_history:
            base_activation = 0.80
            # Boost if context has historical data
            if context.get("history") or context.get("previous_decisions"):
                decision_history = context.get("history", [])
                if len(decision_history) > 0:
                    base_activation = min(0.90, base_activation + 0.10)
            return base_activation

        # Check for learning from experience
        has_learning = any(
            word in query_lower for word in self.LEARNING_WORDS
        )
        if has_learning:
            return 0.75

        # Generic historical words like "before", "earlier" are too common
        # Only activate if explicitly asking about history
        if "remember" in query_lower:
            return 0.70

        # Check if context includes substantial historical data
        decision_history = context.get("history", [])
        if len(decision_history) > 3:
            # Significant history available, mild activation
            return 0.40

        # No history indicators
        return 0.15

    def _deliberate(
        self, query: str, context: Dict[str, Any], circuits: List[str]
    ) -> str:
        """Generate historical analysis and pattern recognition response.

        Args:
            query: The question or task to process
            context: Additional contextual information
            circuits: List of circuits that have been activated

        Returns:
            Historical and pattern analysis
        """
        query_lower = query.lower()

        # Append history retrieval circuit
        circuits.append("history_retrieval")

        # Check for pattern recognition needs
        if any(
            word in query_lower
            for word in ["pattern", "recurring", "similar", "like"]
        ):
            circuits.append("pattern_recognition")

        # Check for lineage tracing needs
        if any(
            word in query_lower
            for word in ["lineage", "ancestry", "origin", "trace"]
        ):
            circuits.append("lineage_trace")

        # Generate response
        response_parts = [
            "📜 Memory & Pattern Analysis:",
            "",
        ]

        # Add historical context if available
        history = context.get("history", [])
        if history:
            response_parts.extend(
                [
                    "Historical Context:",
                    f"  • {len(history)} previous decision(s) found",
                    "  • Extracting relevant patterns...",
                    "",
                ]
            )

        # Add pattern recognition if relevant
        if "pattern_recognition" in circuits:
            response_parts.extend(
                [
                    "🔍 Pattern Recognition:",
                    "  • Identifying recurring themes",
                    "  • Detecting decision cycles",
                    "  • Recognizing success/failure patterns",
                    "",
                ]
            )

        # Add lineage trace if relevant
        if "lineage_trace" in circuits:
            response_parts.extend(
                [
                    "🌳 Lineage Trace:",
                    "  • Root decision context",
                    "  • Evolutionary path",
                    "  • Current position in lineage",
                    "",
                ]
            )

        # Add lessons learned section
        response_parts.extend(
            [
                "📚 Lessons from History:",
                "  • What worked before?",
                "  • What failed and why?",
                "  • How does this compare?",
                "",
            ]
        )

        response_parts.append(
            "🧠 Smriti's Teaching: "
            "Those who forget history are doomed to repeat it. "
            "Learn from patterns, but don't be imprisoned by them."
        )

        return "\n".join(response_parts)

    def _extract_context(
        self, query: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract memory and pattern-relevant context.

        Args:
            query: The question or task being processed
            context: Full contextual information

        Returns:
            Dictionary of historical context
        """
        query_lower = query.lower()

        extracted = {
            "has_memory_language": any(
                word in query_lower for word in self.MEMORY_WORDS
            ),
            "has_learning_language": any(
                word in query_lower for word in self.LEARNING_WORDS
            ),
        }

        # Extract historical data if present
        if "history" in context:
            extracted["history"] = context["history"]

        # Extract previous decisions
        if "previous_decisions" in context:
            extracted["previous_decisions"] = context["previous_decisions"]

        # Extract patterns if already identified
        if "known_patterns" in context:
            extracted["known_patterns"] = context["known_patterns"]

        # Extract lineage information
        if "lineage_path" in context:
            extracted["lineage_path"] = context["lineage_path"]

        # Extract decision ancestry
        if "parent_decision" in context or "root_decision" in context:
            extracted["decision_ancestry"] = {
                "parent": context.get("parent_decision"),
                "root": context.get("root_decision"),
            }

        return extracted
