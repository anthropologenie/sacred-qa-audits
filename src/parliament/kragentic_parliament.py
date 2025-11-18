"""Kragentic Parliament - Coordinated multi-agent decision-making system.

This module implements the parliamentary governance layer where multiple
specialized agents deliberate on queries and synthesize collective decisions.
"""

from typing import Any, Dict, List, Tuple
import statistics

from agents.base_agent import BaseAgent
from agents.krudi_agent import KrudiAgent
from agents.parva_agent import ParvaAgent
from agents.shanti_agent import ShantiAgent
from agents.rudi_agent import RudiAgent
from agents.kshana_agent import KshanaAgent
from agents.maya_agent import MayaAgent
from agents.smriti_agent import SmritiAgent
from circuits.activation_tracker import (
    CircuitActivation,
    ParliamentDecisionTrace,
)


class KragenticParliament:
    """Parliamentary governance system for coordinated multi-agent decisions.

    The Kragentic Parliament orchestrates seven specialized agents:
        - Krudi: Reality grounding and embodied constraints
        - Parva: Temporal causality and consequences
        - Shanti: Equilibrium and conflict resolution
        - Rudi: Transformation and adaptation
        - Kshana: Presence and synthesis (final decision collapse)
        - Maya: Simulation and forward modeling
        - Smriti: Memory and pattern recognition

    The parliament manages the activation flow, tracks decision lineages,
    measures dharmic alignment, and maintains decision history.

    Attributes:
        agents: Dictionary of all agents in the parliament
        kshana_counter: Counter for decision moments (kshana indices)
        decision_history: List of all previous decision traces
    """

    def __init__(self) -> None:
        """Initialize the Kragentic Parliament with all seven agents."""
        # Initialize all agents
        self.agents: Dict[str, BaseAgent] = {
            "krudi": KrudiAgent(),
            "parva": ParvaAgent(),
            "shanti": ShantiAgent(),
            "rudi": RudiAgent(),
            "kshana": KshanaAgent(),
            "maya": MayaAgent(),
            "smriti": SmritiAgent(),
        }

        # Initialize kshana counter (decision moment counter)
        self.kshana_counter: int = 0

        # Initialize decision history
        self.decision_history: List[ParliamentDecisionTrace] = []

    def deliberate(
        self, query: str, context: Dict[str, Any] | None = None
    ) -> Tuple[str, ParliamentDecisionTrace]:
        """Conduct parliamentary deliberation on a query.

        This is the main entry point for the parliament. It orchestrates
        the entire decision-making process:
            1. Create decision trace
            2. Activate all agents
            3. Record activations
            4. Measure conflict and compute context
            5. Synthesize final decision via Kshana
            6. Compute dharmic alignment
            7. Detect patterns
            8. Extract lineage
            9. Store in history

        Args:
            query: The question or task to deliberate on
            context: Optional contextual information

        Returns:
            Tuple of (final_decision, decision_trace)
        """
        # Initialize context if None
        if context is None:
            context = {}

        # Increment kshana counter
        self.kshana_counter += 1

        # Create decision trace
        trace = ParliamentDecisionTrace(
            kshana_index=self.kshana_counter,
            query=query,
        )

        # Phase 1: Activate all non-Kshana agents
        agent_responses: Dict[str, str] = {}
        other_agents = [
            name for name in self.agents.keys() if name != "kshana"
        ]

        for agent_name in other_agents:
            agent = self.agents[agent_name]

            # Add decision history to context for Smriti
            enhanced_context = {
                **context,
                "history": self.decision_history[-5:]
                if self.decision_history
                else [],
            }

            # Process query through agent
            response, activation = agent.process(query, enhanced_context)

            # Store response and activation
            agent_responses[agent_name] = response
            trace.add_activation(activation)

        # Phase 2: Measure conflict and enhance context for Shanti
        conflict_score = self._measure_conflict(trace)
        context["conflict_score"] = conflict_score

        # Re-process Shanti if conflict is high and it didn't activate
        shanti_activation = trace.activations.get("shanti")
        if (
            conflict_score > 0.5
            and shanti_activation
            and shanti_activation.activation_strength
            < self.agents["shanti"].activation_threshold
        ):
            # Force Shanti to re-evaluate with conflict context
            response, activation = self.agents["shanti"].process(
                query, context
            )
            agent_responses["shanti"] = response
            # Update activation in trace
            trace.activations["shanti"] = activation
            if "shanti" not in trace.activation_sequence:
                trace.activation_sequence.append("shanti")

        # Phase 3: Compute sparsity ratio
        total_agents = len(other_agents)
        trace.compute_sparsity(total_agents)

        # Phase 4: Kshana synthesis (final decision collapse)
        kshana_agent = self.agents["kshana"]
        final_decision, kshana_activation = kshana_agent.synthesize(
            agent_responses, trace
        )
        trace.add_activation(kshana_activation)
        trace.decision = final_decision
        trace.agent_responses = agent_responses

        # Phase 5: Compute confidence based on activation coherence
        trace.confidence = self._compute_confidence(trace)

        # Phase 6: Compute dharmic alignment
        trace.dharmic_alignment = self._compute_dharmic_alignment(trace)

        # Phase 7: Detect patterns
        trace.pattern_flags = self._detect_patterns(trace)

        # Phase 8: Extract lineage
        trace.lineage_path = self._extract_lineage(trace)

        # Phase 9: Store in history
        self.decision_history.append(trace)

        return final_decision, trace

    def _compute_confidence(self, trace: ParliamentDecisionTrace) -> float:
        """Compute confidence score based on activation coherence.

        Args:
            trace: The decision trace to analyze

        Returns:
            Confidence score between 0.0 and 1.0
        """
        # Get activation strengths of active agents
        strengths = [
            act.activation_strength
            for act in trace.activations.values()
            if act.activation_strength
            >= self.agents[act.agent_name].activation_threshold
        ]

        if not strengths:
            return 0.5  # Neutral confidence if no agents activated

        # High mean activation = high confidence
        mean_strength = statistics.mean(strengths)

        # Low variance = high coherence = higher confidence
        if len(strengths) > 1:
            variance = statistics.variance(strengths)
            coherence = 1.0 - min(variance, 1.0)
        else:
            coherence = 1.0

        # Combine mean activation and coherence
        confidence = (mean_strength * 0.6) + (coherence * 0.4)

        return min(max(confidence, 0.0), 1.0)

    def _compute_dharmic_alignment(
        self, trace: ParliamentDecisionTrace
    ) -> float:
        """Compute dharmic alignment score based on proper activation order.

        Dharmic alignment measures whether the parliament followed proper
        principles:
            - Grounding before speculation (Krudi before Maya)
            - Synthesis at the end (Kshana last)
            - Conflict resolution when needed (Shanti when conflict high)

        Args:
            trace: The decision trace to analyze

        Returns:
            Dharmic alignment score between 0.0 and 1.0
        """
        alignment_score = 0.0
        checks_performed = 0

        # Check 1: Kshana should activate last (always true by design)
        if "kshana" in trace.activation_sequence:
            if trace.activation_sequence[-1] == "kshana":
                alignment_score += 1.0
            checks_performed += 1

        # Check 2: If both Krudi and Maya activated, Krudi should come first
        # (grounding before simulation)
        krudi_activation = trace.activations.get("krudi")
        maya_activation = trace.activations.get("maya")

        if (
            krudi_activation
            and maya_activation
            and krudi_activation.activation_strength
            >= self.agents["krudi"].activation_threshold
            and maya_activation.activation_strength
            >= self.agents["maya"].activation_threshold
        ):
            krudi_idx = trace.activation_sequence.index("krudi")
            maya_idx = trace.activation_sequence.index("maya")
            if krudi_idx < maya_idx:
                alignment_score += 1.0
            checks_performed += 1

        # Check 3: If conflict is high, Shanti should activate
        conflict_score = self._measure_conflict(trace)
        if conflict_score > 0.6:
            shanti_activation = trace.activations.get("shanti")
            if (
                shanti_activation
                and shanti_activation.activation_strength
                >= self.agents["shanti"].activation_threshold
            ):
                alignment_score += 1.0
            checks_performed += 1

        # Check 4: If transformation (Rudi) activates, memory (Smriti)
        # should provide context
        rudi_activation = trace.activations.get("rudi")
        smriti_activation = trace.activations.get("smriti")

        if (
            rudi_activation
            and rudi_activation.activation_strength
            >= self.agents["rudi"].activation_threshold
        ):
            if (
                smriti_activation
                and smriti_activation.activation_strength
                >= self.agents["smriti"].activation_threshold
            ):
                alignment_score += 1.0
            else:
                # Rudi without Smriti - slight penalty but not zero
                alignment_score += 0.5
            checks_performed += 1

        # Normalize by number of checks
        if checks_performed > 0:
            return alignment_score / checks_performed
        else:
            return 0.75  # Default reasonable alignment

    def _detect_patterns(
        self, trace: ParliamentDecisionTrace
    ) -> List[str]:
        """Detect problematic or notable patterns in the decision.

        Args:
            trace: The decision trace to analyze

        Returns:
            List of pattern flags
        """
        flags: List[str] = []

        # Flag 1: Sparsity too low (too many agents active)
        if trace.sparsity_ratio < 0.3:
            flags.append(
                "LOW_SPARSITY: Many agents activated - "
                "decision may be overly complex"
            )

        # Flag 2: Sparsity too high (too few agents active)
        if trace.sparsity_ratio > 0.8:
            flags.append(
                "HIGH_SPARSITY: Few agents activated - "
                "decision may lack perspective"
            )

        # Flag 3: Maya active without Krudi (simulation without grounding)
        maya_activation = trace.activations.get("maya")
        krudi_activation = trace.activations.get("krudi")

        if (
            maya_activation
            and maya_activation.activation_strength
            >= self.agents["maya"].activation_threshold
        ):
            if (
                not krudi_activation
                or krudi_activation.activation_strength
                < self.agents["krudi"].activation_threshold
            ):
                flags.append(
                    "UNGROUNDED_SIMULATION: Maya active without Krudi - "
                    "simulation may lack reality grounding"
                )

        # Flag 4: Rudi active without Smriti (transformation without memory)
        rudi_activation = trace.activations.get("rudi")
        smriti_activation = trace.activations.get("smriti")

        if (
            rudi_activation
            and rudi_activation.activation_strength
            >= self.agents["rudi"].activation_threshold
        ):
            if (
                not smriti_activation
                or smriti_activation.activation_strength
                < self.agents["smriti"].activation_threshold
            ):
                flags.append(
                    "AHISTORICAL_TRANSFORMATION: Rudi active without Smriti - "
                    "transformation may ignore historical lessons"
                )

        # Flag 5: High conflict without Shanti
        conflict_score = self._measure_conflict(trace)
        shanti_activation = trace.activations.get("shanti")

        if conflict_score > 0.6:
            if (
                not shanti_activation
                or shanti_activation.activation_strength
                < self.agents["shanti"].activation_threshold
            ):
                flags.append(
                    "UNRESOLVED_CONFLICT: High agent conflict without Shanti - "
                    "decision may be unstable"
                )

        # Flag 6: Very high total activation (overactive parliament)
        if trace.total_activation > 5.0:
            flags.append(
                "OVERACTIVATION: Very high total activation - "
                "parliament may be overengaged"
            )

        return flags

    def _measure_conflict(self, trace: ParliamentDecisionTrace) -> float:
        """Measure conflict level based on variance in activation strengths.

        High variance indicates disagreement among agents about the query's
        relevance to their domains.

        Args:
            trace: The decision trace to analyze

        Returns:
            Conflict score between 0.0 and 1.0
        """
        # Get activation strengths (excluding kshana)
        strengths = [
            act.activation_strength
            for name, act in trace.activations.items()
            if name != "kshana"
        ]

        if len(strengths) < 2:
            return 0.0

        # Calculate variance
        variance = statistics.variance(strengths)

        # Normalize variance to 0-1 range
        # Variance of uniform [0,1] is 1/12 ≈ 0.083
        # Max variance occurs at extremes, roughly 0.25
        conflict_score = min(variance / 0.25, 1.0)

        return conflict_score

    def _extract_lineage(
        self, trace: ParliamentDecisionTrace
    ) -> List[str]:
        """Extract lineage of fired circuits from highly activated agents.

        Args:
            trace: The decision trace to analyze

        Returns:
            List of circuit paths in format 'agent.circuit'
        """
        lineage: List[str] = []

        # For each agent with activation > 0.5, list their fired circuits
        for agent_name, activation in trace.activations.items():
            if activation.activation_strength > 0.5:
                for circuit in activation.circuits_fired:
                    lineage.append(f"{agent_name}.{circuit}")

        return lineage

    def get_decision_history(
        self, limit: int | None = None
    ) -> List[ParliamentDecisionTrace]:
        """Retrieve decision history.

        Args:
            limit: Optional limit on number of recent decisions to return

        Returns:
            List of decision traces (most recent first)
        """
        if limit is None:
            return list(reversed(self.decision_history))
        else:
            return list(reversed(self.decision_history[-limit:]))

    def get_agent_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics about agent activation patterns.

        Returns:
            Dictionary mapping agent names to their statistics
        """
        stats: Dict[str, Dict[str, Any]] = {}

        for agent_name in self.agents.keys():
            activations = [
                trace.activations.get(agent_name)
                for trace in self.decision_history
                if trace.activations.get(agent_name) is not None
            ]

            if not activations:
                stats[agent_name] = {
                    "total_activations": 0,
                    "mean_strength": 0.0,
                    "activation_rate": 0.0,
                }
                continue

            strengths = [act.activation_strength for act in activations]
            threshold = self.agents[agent_name].activation_threshold
            above_threshold = sum(
                1 for s in strengths if s >= threshold
            )

            stats[agent_name] = {
                "total_activations": len(activations),
                "active_count": above_threshold,
                "mean_strength": statistics.mean(strengths),
                "activation_rate": (
                    above_threshold / len(self.decision_history)
                    if self.decision_history
                    else 0.0
                ),
            }

        return stats

    def __repr__(self) -> str:
        """Return string representation of the parliament."""
        return (
            f"KragenticParliament("
            f"agents={len(self.agents)}, "
            f"kshana_counter={self.kshana_counter}, "
            f"history_size={len(self.decision_history)})"
        )
