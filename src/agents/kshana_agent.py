"""Kshana Agent - Presence, synthesis, and decision collapse agent.

This agent represents the moment of decision - the collapse of possibility
into actuality. It synthesizes all agent responses into a final decision.
"""

from typing import Any, Dict, List, Tuple

from ..circuits.activation_tracker import CircuitActivation
from .base_agent import BaseAgent


class KshanaAgent(BaseAgent):
    """Agent focused on presence, synthesis, and decision collapse.

    Kshana ALWAYS activates as the final synthesis step. It represents
    the present moment where all possibilities collapse into a single
    decision. It integrates all agent perspectives into coherent action.

    Special behavior: Unlike other agents, Kshana has a synthesis method
    that takes all agent responses and produces the final decision.

    Circuits:
        - synthesis: Integrates multiple perspectives
        - decision_collapse: Collapses possibilities into decision
        - presence_anchor: Grounds in the present moment
    """

    def __init__(self) -> None:
        """Initialize the Kshana agent with default name."""
        super().__init__(name="kshana")
        # Kshana always activates, so set threshold to 0
        self.activation_threshold = 0.0

    def _compute_activation(
        self, query: str, context: Dict[str, Any]
    ) -> float:
        """Compute activation - Kshana ALWAYS activates.

        Args:
            query: The question or task to evaluate
            context: Additional contextual information

        Returns:
            Always returns 1.0 (maximum activation)
        """
        # Kshana always activates at full strength
        return 1.0

    def _deliberate(
        self, query: str, context: Dict[str, Any], circuits: List[str]
    ) -> str:
        """Generate synthesis and decision collapse response.

        Args:
            query: The question or task to process
            context: Additional contextual information
            circuits: List of circuits that have been activated

        Returns:
            Synthesis and decision guidance
        """
        # Append all Kshana circuits
        circuits.extend(["synthesis", "decision_collapse", "presence_anchor"])

        # Generate basic response (often overridden by synthesize method)
        response_parts = [
            "🎯 Decision Synthesis:",
            "",
            "Collapsing possibility space into actionable decision...",
            "",
            "Present Moment Anchoring:",
            "  • All agent perspectives integrated",
            "  • Decision point reached",
            "  • Action pathway clarified",
        ]

        return "\n".join(response_parts)

    def synthesize(
        self,
        agent_responses: Dict[str, str],
        trace: Any,  # ParliamentDecisionTrace
    ) -> Tuple[str, CircuitActivation]:
        """Synthesize all agent responses into final decision.

        This is the primary method for Kshana. It takes all agent responses
        and creates a unified, coherent decision.

        Args:
            agent_responses: Dictionary mapping agent names to their responses
            trace: ParliamentDecisionTrace containing full decision context

        Returns:
            Tuple of (synthesized_decision, activation_trace)
        """
        circuits = ["synthesis", "decision_collapse", "presence_anchor"]

        # Filter out empty responses
        active_responses = {
            name: resp for name, resp in agent_responses.items() if resp
        }

        # Build synthesis response
        response_parts = [
            "═══════════════════════════════════════════",
            "🎯 KSHANA SYNTHESIS - Decision Collapse",
            "═══════════════════════════════════════════",
            "",
            f"Query: {trace.query}",
            f"Kshana Index: {trace.kshana_index}",
            f"Active Agents: {len(active_responses)}/{len(agent_responses)}",
            f"Sparsity: {trace.sparsity_ratio:.2%}",
            "",
            "─────────────────────────────────────────",
            "AGENT PERSPECTIVES:",
            "─────────────────────────────────────────",
        ]

        # Add each agent's perspective
        for agent_name in trace.activation_sequence:
            if agent_name in active_responses:
                activation = trace.activations.get(agent_name)
                strength = (
                    activation.activation_strength if activation else 0.0
                )
                response_parts.extend(
                    [
                        "",
                        f"[{agent_name.upper()}] "
                        f"(activation: {strength:.2f})",
                        active_responses[agent_name],
                    ]
                )

        # Add decision collapse section
        response_parts.extend(
            [
                "",
                "─────────────────────────────────────────",
                "⚡ DECISION COLLAPSE:",
                "─────────────────────────────────────────",
                "",
                self._collapse_decision(active_responses, trace),
                "",
                "═══════════════════════════════════════════",
                f"Decision #{trace.decision_id[:8]}... | "
                f"Confidence: {trace.confidence:.2%} | "
                f"Dharmic Alignment: {trace.dharmic_alignment:.2%}",
                "═══════════════════════════════════════════",
            ]
        )

        final_response = "\n".join(response_parts)

        # Create activation trace
        activation = CircuitActivation(
            agent_name=self.name,
            activation_strength=1.0,
            circuits_fired=circuits,
            context={
                "active_agents": list(active_responses.keys()),
                "total_agents": len(agent_responses),
                "synthesis_mode": "full_parliament",
            },
        )

        return final_response, activation

    def _collapse_decision(
        self, active_responses: Dict[str, str], trace: Any
    ) -> str:
        """Collapse multiple perspectives into single decision.

        Args:
            active_responses: Dictionary of agent responses
            trace: Decision trace with context

        Returns:
            Collapsed decision text
        """
        # Simple synthesis logic - can be enhanced with more sophisticated methods
        decision_parts = [
            "Integrating all perspectives into coherent action path...",
            "",
            "Recommended Decision:",
        ]

        # Identify key themes from activated agents
        if "krudi" in active_responses:
            decision_parts.append(
                "  • Ground in reality and embodied constraints"
            )
        if "parva" in active_responses:
            decision_parts.append("  • Consider temporal consequences")
        if "shanti" in active_responses:
            decision_parts.append("  • Maintain balance and harmony")
        if "rudi" in active_responses:
            decision_parts.append("  • Allow for adaptation and learning")
        if "maya" in active_responses:
            decision_parts.append("  • Model scenarios before acting")
        if "smriti" in active_responses:
            decision_parts.append("  • Learn from historical patterns")

        decision_parts.extend(
            [
                "",
                "🎯 Present Moment Action: Proceed with awareness of all "
                "perspectives, grounded in reality, aligned with dharma.",
            ]
        )

        return "\n".join(decision_parts)

    def _extract_context(
        self, query: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract synthesis-relevant context.

        Args:
            query: The question or task being processed
            context: Full contextual information

        Returns:
            Dictionary of synthesis context
        """
        extracted = {
            "synthesis_mode": "kshana_collapse",
            "always_active": True,
        }

        # Extract all agent-related context
        if "agent_responses" in context:
            extracted["agent_responses"] = context["agent_responses"]

        if "activation_sequence" in context:
            extracted["activation_sequence"] = context["activation_sequence"]

        # Extract decision metadata
        if "kshana_index" in context:
            extracted["kshana_index"] = context["kshana_index"]

        return extracted
