"""Krudi Agent - Reality grounding and embodied constraints agent.

This agent specializes in grounding speculative or decision-oriented queries
in reality, embodied constraints, and sovereignty principles.
"""

from typing import Any, Dict, List

from agents.base_agent import BaseAgent


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
                - 0.85: Implementation questions (needs reality checks)
                - 0.75: Decision questions with should/can (needs grounding)
                - 0.15: Simple factual queries (minimal intervention)
        """
        query_lower = query.lower()

        # Check for simple factual queries (low word count, no decision words)
        word_count = len(query_lower.split())
        has_decision = any(word in query_lower for word in self.DECISION_WORDS)
        has_speculation = any(
            word in query_lower for word in self.SPECULATION_WORDS
        )

        # Simple factual queries - minimal grounding needed
        if word_count < 10 and not has_decision and not has_speculation:
            return 0.15

        # Implementation questions need strong reality checks
        if "implement" in query_lower or "build" in query_lower:
            if has_speculation:
                return 0.95
            return 0.85

        # Decision questions with should/can
        if "should" in query_lower or "can we" in query_lower:
            if has_speculation:
                return 0.95
            return 0.75

        # Speculation without decision
        if has_speculation:
            return 0.60

        # General query - minimal grounding
        return 0.15

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

        # Check if this is a factual query that needs no grounding
        if self._is_factual_query(query_lower):
            return ""

        # Always append reality anchor circuit
        circuits.append("reality_anchor")

        # Check for embodied implementation concerns
        if "build" in query_lower or "deploy" in query_lower:
            circuits.append("embodied_grounding")

        # Check for sovereignty and community concerns
        if "community" in query_lower or "krecosystem" in query_lower:
            circuits.append("sovereignty_alignment")

        # Extract what's being proposed
        proposal = self._extract_proposal(query_lower)
        if not proposal:
            return ""

        # Generate specific reality constraints
        return self._generate_grounding(query_lower, proposal, circuits)

    def _is_factual_query(self, query_lower: str) -> bool:
        """Check if query is factual and needs no grounding.

        Args:
            query_lower: Lowercased query string

        Returns:
            True if factual query, False otherwise
        """
        factual_patterns = [
            "what is",
            "what are",
            "who is",
            "who are",
            "when is",
            "when was",
            "where is",
            "where are",
            "how does",
            "how do",
            "explain",
            "define",
        ]

        # Check if it's asking for facts/definitions
        if any(pattern in query_lower for pattern in factual_patterns):
            # But not if it's also asking for decision/action
            if not any(
                word in query_lower
                for word in ["should", "implement", "build", "deploy"]
            ):
                return True

        return False

    def _extract_proposal(self, query_lower: str) -> str:
        """Extract what's being proposed in the query.

        Args:
            query_lower: Lowercased query string

        Returns:
            Extracted proposal or empty string
        """
        # Look for decision/action proposals
        if "should we" in query_lower or "should i" in query_lower:
            # Extract what comes after "should we/i"
            for phrase in ["should we ", "should i "]:
                if phrase in query_lower:
                    rest = query_lower.split(phrase, 1)[1]
                    # Take first meaningful chunk (up to ? or first 50 chars)
                    proposal = rest.split("?")[0].strip()[:50]
                    return proposal

        # Look for "let's", "we could", etc.
        proposal_phrases = ["let's ", "we could ", "we might ", "consider "]
        for phrase in proposal_phrases:
            if phrase in query_lower:
                rest = query_lower.split(phrase, 1)[1]
                proposal = rest.split("?")[0].strip()[:50]
                return proposal

        # Look for build/deploy/implement statements
        if any(
            word in query_lower for word in ["build", "deploy", "implement"]
        ):
            return "implementation"

        return ""

    def _generate_grounding(
        self, query_lower: str, proposal: str, circuits: List[str]
    ) -> str:
        """Generate specific grounding for the proposal.

        Args:
            query_lower: Lowercased query string
            proposal: The extracted proposal
            circuits: Active circuits

        Returns:
            Specific reality grounding
        """
        # Deployment grounding
        if "deploy" in query_lower:
            if "auth" in query_lower or "authentication" in query_lower:
                return "Reality check: Requires staging test, rollback plan, monitoring setup, off-hours deployment window. Ensure 2+ engineers on-call."
            elif "database" in query_lower or "db" in query_lower:
                return "Reality check: Requires backup, migration test, rollback procedure, maintenance window. Test on production-like data volume first."
            else:
                return "Reality check: Requires testing in staging, rollback plan, monitoring alerts, deployment window. Coordinate with on-call team."

        # Build/implementation grounding
        if "build" in query_lower or "implement" in query_lower:
            # Check for unrealistic scale
            if any(
                word in query_lower
                for word in [
                    "quantum",
                    "ai system",
                    "blockchain",
                    "distributed ledger",
                ]
            ):
                if "quantum" in query_lower:
                    return "Reality constraint: Quantum computing requires specialized facilities, cryogenic equipment ($10M+), PhD-level expertise. Not viable for typical organization."
                elif "ai system" in query_lower and "large" in query_lower:
                    return "Reality constraint: Large AI systems require GPU clusters ($100K+), ML expertise, massive datasets, months of training. Start with smaller, focused model."
                else:
                    return "Reality constraint: Significant infrastructure, specialized expertise, and capital investment required. Evaluate cost-benefit carefully."

            # Check for scope warnings
            if any(
                word in query_lower
                for word in ["enterprise", "large-scale", "massive"]
            ):
                return "Reality constraint: Enterprise-scale requires dedicated infrastructure, operations team, security compliance, ongoing maintenance. Start with MVP to validate."

            # Generic build grounding
            return "Reality check: Requires scoping, resource allocation, timeline estimation, testing plan. Define minimal viable version first."

        # Sovereignty/community grounding
        if "sovereignty_alignment" in circuits:
            if "modify" in query_lower or "change" in query_lower:
                return "Sovereignty consideration: Local modification enables autonomy but requires governance framework to maintain network coherence. Balance needed."
            elif "control" in query_lower or "decide" in query_lower:
                return "Sovereignty consideration: Distributed control preserves autonomy but increases coordination complexity. Define decision boundaries clearly."
            else:
                return "Sovereignty consideration: Balance community autonomy with system coherence. Establish governance mechanisms."

        # Speculative proposals
        if any(
            word in query_lower
            for word in ["maybe", "theoretically", "could", "might"]
        ):
            return "Reality anchor: Move from speculation to concrete steps. What's the minimal viable test? What resources are actually available?"

        # Generic grounding for decisions
        if "should" in query_lower:
            return "Reality check: Evaluate actual resources, timeline constraints, and team capacity. Define success criteria and rollback plan."

        return "Reality anchor: Ground in concrete steps, measurable outcomes, actual resource availability."

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
