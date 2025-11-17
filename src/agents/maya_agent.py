"""Maya Agent - Simulation and forward modeling agent.

This agent specializes in simulating possible futures, generating scenarios,
and exploring the possibility space before decisions are made.
"""

from typing import Any, Dict, List

from .base_agent import BaseAgent


class MayaAgent(BaseAgent):
    """Agent focused on simulation and forward modeling.

    Maya activates when forward modeling, scenario generation, or
    possibility exploration is needed. It helps visualize potential
    futures before committing to decisions.

    Circuits:
        - forward_model: Projects outcomes into the future
        - scenario_generation: Creates alternative futures
        - possibility_space: Maps the space of potential outcomes
    """

    SIMULATION_WORDS = {
        "simulate",
        "model",
        "predict",
        "forecast",
        "scenario",
        "what if",
        "imagine",
        "envision",
    }
    FUTURE_WORDS = {
        "future",
        "will",
        "would",
        "outcome",
        "result",
        "potential",
        "possible",
        "probable",
    }

    def __init__(self) -> None:
        """Initialize the Maya agent with default name."""
        super().__init__(name="maya")

    def _compute_activation(
        self, query: str, context: Dict[str, Any]
    ) -> float:
        """Compute activation based on simulation and future modeling needs.

        Args:
            query: The question or task to evaluate
            context: Additional contextual information

        Returns:
            Activation strength:
                - 0.90: Strong simulation/modeling request
                - 0.75: Scenario or what-if exploration
                - 0.60: Future outcome consideration
                - 0.35: Present-focused query
        """
        query_lower = query.lower()

        # Check for explicit simulation language
        has_simulation = any(
            word in query_lower for word in self.SIMULATION_WORDS
        )
        if has_simulation:
            return 0.90

        # Check for what-if or scenario language
        if "what if" in query_lower or "scenario" in query_lower:
            return 0.75

        # Check for future/outcome language
        has_future = any(word in query_lower for word in self.FUTURE_WORDS)
        if has_future:
            return 0.60

        return 0.35

    def _deliberate(
        self, query: str, context: Dict[str, Any], circuits: List[str]
    ) -> str:
        """Generate simulation and scenario modeling response.

        Args:
            query: The question or task to process
            context: Additional contextual information
            circuits: List of circuits that have been activated

        Returns:
            Forward modeling and scenario analysis
        """
        query_lower = query.lower()

        # Append forward model circuit
        circuits.append("forward_model")

        # Check for scenario generation needs
        if any(
            word in query_lower
            for word in ["scenario", "alternative", "option", "what if"]
        ):
            circuits.append("scenario_generation")

        # Check for possibility space exploration
        if any(
            word in query_lower
            for word in ["possible", "potential", "space", "explore"]
        ):
            circuits.append("possibility_space")

        # Generate response
        response_parts = [
            "🔮 Simulation & Forward Modeling:",
            "",
        ]

        # Add scenario generation if relevant
        if "scenario_generation" in circuits:
            response_parts.extend(
                [
                    "📊 Scenario Generation:",
                    "  • Scenario A: Optimistic path",
                    "  • Scenario B: Conservative path",
                    "  • Scenario C: Adaptive path",
                    "",
                ]
            )

        # Add possibility space mapping
        if "possibility_space" in circuits:
            response_parts.extend(
                [
                    "🌌 Possibility Space:",
                    "  • High probability outcomes",
                    "  • Edge cases and outliers",
                    "  • Emergent possibilities",
                    "",
                ]
            )

        # Always include forward model
        response_parts.extend(
            [
                "⏭️ Forward Model:",
                "  1. Current state → Decision",
                "  2. Decision → Immediate effects",
                "  3. Effects → System evolution",
                "  4. Evolution → Future states",
                "",
            ]
        )

        response_parts.append(
            "🎭 Maya's Wisdom: "
            "All futures are simulations until actualized. "
            "Model multiple paths before choosing."
        )

        return "\n".join(response_parts)

    def _extract_context(
        self, query: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract simulation-relevant context.

        Args:
            query: The question or task being processed
            context: Full contextual information

        Returns:
            Dictionary of simulation context
        """
        query_lower = query.lower()

        extracted = {
            "has_simulation_language": any(
                word in query_lower for word in self.SIMULATION_WORDS
            ),
            "has_future_language": any(
                word in query_lower for word in self.FUTURE_WORDS
            ),
        }

        # Extract current state for modeling
        if "current_state" in context or "baseline" in context:
            extracted["modeling_baseline"] = {
                "current_state": context.get("current_state"),
                "baseline": context.get("baseline"),
            }

        # Extract constraints for scenario generation
        if "constraints" in context or "boundaries" in context:
            extracted["scenario_constraints"] = {
                "constraints": context.get("constraints"),
                "boundaries": context.get("boundaries"),
            }

        # Extract number of scenarios requested
        if "num_scenarios" in context:
            extracted["num_scenarios"] = context["num_scenarios"]

        return extracted
