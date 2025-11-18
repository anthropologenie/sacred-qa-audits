"""Parva Agent - Temporal causality and consequence modeling agent.

This agent specializes in analyzing temporal relationships, causal chains,
and downstream consequences of decisions.
"""

from typing import Any, Dict, List

from agents.base_agent import BaseAgent


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
                - 0.85: Consequences/effects explicitly mentioned
                - 0.80: "What happens if/after/when" questions
                - 0.15: No temporal/causal words
        """
        query_lower = query.lower()

        # Check for explicit consequence/effect questions
        if any(
            word in query_lower
            for word in ["consequence", "consequences", "effect", "effects"]
        ):
            return 0.85

        # Check for "what happens" temporal questions
        if "what happens" in query_lower or "what will happen" in query_lower:
            return 0.80

        # Check for temporal question patterns
        temporal_question_patterns = [
            "what if",
            "what after",
            "what when",
            "happens if",
            "happens after",
            "happens when",
        ]
        if any(pattern in query_lower for pattern in temporal_question_patterns):
            return 0.80

        # Check for deployment/implementation questions (have temporal consequences)
        if "deploy" in query_lower or "implement" in query_lower:
            # Deployment and implementation have significant temporal consequences
            return 0.75

        # Count temporal and causal indicators
        temporal_count = sum(
            1 for word in self.TEMPORAL_WORDS if word in query_lower
        )
        causality_count = sum(
            1 for word in self.CAUSALITY_WORDS if word in query_lower
        )

        # Only activate significantly if both temporal and causal present
        if temporal_count >= 2 and causality_count >= 1:
            return 0.75
        elif temporal_count >= 1 or causality_count >= 1:
            # Some indicators but not strong
            return 0.15

        # No temporal/causal content
        return 0.15

    def _deliberate(
        self, query: str, context: Dict[str, Any], circuits: List[str]
    ) -> str:
        """Generate temporal-causal analysis response.

        Args:
            query: The question or task to process
            context: Additional contextual information
            circuits: List of circuits that have been activated

        Returns:
            Temporal causality analysis specific to the query
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

        # Extract action/decision from query
        action = self._extract_action(query_lower)
        if not action:
            # No meaningful action to analyze
            return ""

        # Generate specific consequence analysis
        consequences = self._analyze_consequences(query_lower, action)

        if not consequences:
            return ""

        return consequences

    def _extract_action(self, query_lower: str) -> str:
        """Extract the main action or decision from query.

        Args:
            query_lower: Lowercased query string

        Returns:
            Extracted action or empty string
        """
        # Look for action verbs and their objects
        action_patterns = [
            ("deploy", ["deploy", "deployment", "deploying"]),
            ("implement", ["implement", "implementing", "implementation"]),
            ("build", ["build", "building"]),
            ("increase", ["increase", "increasing", "raise", "raising"]),
            ("decrease", ["decrease", "decreasing", "reduce", "reducing"]),
            ("change", ["change", "changing", "modify", "modifying"]),
            ("remove", ["remove", "removing", "delete", "deleting"]),
            ("add", ["add", "adding", "create", "creating"]),
            ("migrate", ["migrate", "migrating", "migration"]),
            ("upgrade", ["upgrade", "upgrading", "update", "updating"]),
        ]

        for action_key, patterns in action_patterns:
            if any(pattern in query_lower for pattern in patterns):
                return action_key

        return ""

    def _analyze_consequences(self, query_lower: str, action: str) -> str:
        """Analyze and generate specific consequences for the action.

        Args:
            query_lower: Lowercased query string
            action: The extracted action

        Returns:
            Specific consequence analysis
        """
        # Extract domain/subject from query
        consequences = []

        # Deployment consequences
        if action == "deploy":
            if "auth" in query_lower or "authentication" in query_lower:
                return "Deployment consequences: Active sessions invalidated → Users logged out → Re-authentication required → Support requests spike. Monitor authentication flows for 24-48 hours post-deployment."
            elif "database" in query_lower or "db" in query_lower:
                return "Database deployment: Migration runs → Table locks → Read/write blocked → Service degradation during migration. Plan maintenance window and rollback strategy."
            elif "api" in query_lower:
                return "API deployment: Version change → Client compatibility issues → Deprecated endpoints → Breaking changes for old clients. Ensure backward compatibility or coordinate client updates."
            else:
                return "Deployment consequences: Service restart → Brief downtime → Active connections dropped → Cache invalidation → Performance dip during warm-up."

        # Rate limit changes
        if ("rate" in query_lower or "limit" in query_lower) and action in ["increase", "decrease", "change"]:
            if action == "increase":
                return "Rate limit increase: More concurrent requests allowed → Higher database/backend load → Potential resource exhaustion under peak traffic → May expose capacity bottlenecks. Monitor system resources closely."
            else:
                return "Rate limit decrease: Stricter throttling → More requests rejected → User friction increases → May drive users to workarounds. Monitor rejection rates and user complaints."

        # Implementation/build consequences
        if action in ["implement", "build"]:
            if "feature" in query_lower or "functionality" in query_lower:
                return "Implementation timeline: Development → Testing → Deployment → User adoption lag → Feedback collection → Iteration cycle. Expect 2-3 iteration rounds before stability."
            elif "system" in query_lower:
                return "System implementation: Architecture decisions → Integration points created → Dependencies introduced → Maintenance burden increases. Document thoroughly for future maintainers."
            else:
                return "Build consequences: Code written → Tests required → Documentation needed → Deployment planned → Monitoring added. Each phase adds time and complexity."

        # Migration consequences
        if action == "migrate":
            if "database" in query_lower:
                return "Database migration: Schema changes → Data transformation → Potential data loss risk → Rollback complexity increases. Test thoroughly in staging environment."
            else:
                return "Migration consequences: System transition → Dual-state period → Data synchronization needed → Rollback window limited. Plan for gradual cutover."

        # Addition/removal consequences
        if action == "add":
            return "Addition consequences: New component → Integration required → Testing surface expands → Maintenance burden increases. Consider long-term support costs."

        if action == "remove":
            return "Removal consequences: Existing dependencies break → Users lose functionality → Possible data loss → Migration path required. Check for downstream dependencies first."

        # Generic action consequences
        return f"Change consequences: Current state altered → System behavior modified → Users affected → Monitoring required. Test thoroughly before production rollout."

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
