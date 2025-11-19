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

        INTEGRATION-AWARE: If context contains career trajectory or application
        history, Parva activates strongly to model probabilistic consequences
        based on actual outcomes.

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
        strength = 0.0

        # INTEGRATION: Check for career trajectory data
        if "parva_trajectory" in context or "parva_timeline" in context:
            strength += 0.4  # Strong activation for consequence modeling

        # If integration context triggered activation, return early
        if strength >= 0.7:
            return min(strength, 1.0)

        # EXISTING LOGIC: Keyword-based activation
        # Check for explicit consequence/effect questions
        if any(
            word in query_lower
            for word in ["consequence", "consequences", "effect", "effects"]
        ):
            return max(0.85, strength)

        # Check for "what happens" temporal questions
        if "what happens" in query_lower or "what will happen" in query_lower:
            return max(0.80, strength)

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
            return max(0.80, strength)

        # Check for deployment/implementation questions (have temporal consequences)
        if "deploy" in query_lower or "implement" in query_lower:
            # Deployment and implementation have significant temporal consequences
            return max(0.75, strength)

        # Count temporal and causal indicators
        temporal_count = sum(
            1 for word in self.TEMPORAL_WORDS if word in query_lower
        )
        causality_count = sum(
            1 for word in self.CAUSALITY_WORDS if word in query_lower
        )

        # Only activate significantly if both temporal and causal present
        if temporal_count >= 2 and causality_count >= 1:
            return max(0.75, strength)
        elif temporal_count >= 1 or causality_count >= 1:
            # Some indicators but not strong
            return max(0.15, strength)

        # No temporal/causal content
        return max(0.15, strength)

    def _deliberate(
        self, query: str, context: Dict[str, Any], circuits: List[str]
    ) -> str:
        """Generate temporal-causal analysis response.

        INTEGRATION-AWARE: If context contains career trajectory data,
        performs probabilistic consequence modeling using actual application
        outcomes and statistics.

        Args:
            query: The question or task to process
            context: Additional contextual information
            circuits: List of circuits that have been activated

        Returns:
            Temporal causality analysis specific to the query
        """
        # INTEGRATION: Check for career trajectory data
        if "parva_trajectory" in context or "parva_timeline" in context:
            circuits.append("integration_consequence_modeling")
            return self._perform_probabilistic_consequence_modeling(
                query,
                context.get("parva_trajectory", []),
                context.get("parva_timeline", {}),
                context.get("job_requirements", []),
                circuits,
            )

        # EXISTING LOGIC: Generic consequence analysis
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

    def _perform_probabilistic_consequence_modeling(
        self,
        query: str,
        trajectory: List[Dict[str, Any]],
        timeline: Dict[str, Any],
        job_requirements: List[str],
        circuits: List[str],
    ) -> str:
        """Perform probabilistic consequence modeling using career trajectory data.

        This method uses actual application outcomes to model the probable
        consequences of different career path choices.

        Args:
            query: The question being asked
            trajectory: List of career milestones/applications
            timeline: Timeline statistics
            job_requirements: Requirements for the job being considered
            circuits: Active circuits list (modified in place)

        Returns:
            Detailed probabilistic consequence analysis
        """
        circuits.append("probabilistic_timeline_modeling")

        response_parts = ["Consequence analysis from your application history:\n"]

        # Analyze recent trajectory
        if trajectory:
            recent_trajectory = self._analyze_recent_trajectory(trajectory)
            if recent_trajectory:
                response_parts.append("Current trajectory (past 6 months):")
                response_parts.extend(recent_trajectory)
                response_parts.append("")

        # Model consequences of applying to current role
        if job_requirements:
            current_path = self._model_current_path_consequences(
                trajectory, job_requirements, query
            )
            if current_path:
                response_parts.append(
                    "If you apply to this role (based on similar past applications):"
                )
                response_parts.extend(current_path)
                response_parts.append("")

        # Model alternative path
        alternative_path = self._model_alternative_path(
            trajectory, job_requirements
        )
        if alternative_path:
            response_parts.append("Alternative path (higher probability):")
            response_parts.extend(alternative_path)
            response_parts.append("")

        # Compare expected outcomes
        comparison = self._compare_path_outcomes(
            trajectory, job_requirements
        )
        if comparison:
            response_parts.append("Expected outcome comparison:")
            response_parts.extend(comparison)
            response_parts.append("")

        # Generate recommendation
        recommendation = self._generate_path_recommendation(
            trajectory, job_requirements
        )
        if recommendation:
            response_parts.append("Recommendation:")
            response_parts.append(recommendation)

        return "\n".join(response_parts)

    def _analyze_recent_trajectory(
        self, trajectory: List[Dict[str, Any]]
    ) -> List[str]:
        """Analyze recent application trajectory (past 6 months).

        Args:
            trajectory: List of career milestones

        Returns:
            List of trajectory observations
        """
        observations = []

        # Group by month and analyze patterns
        from collections import defaultdict
        from datetime import datetime, timedelta

        # Parse dates and group by month
        six_months_ago = datetime.now() - timedelta(days=180)
        monthly_stats = defaultdict(
            lambda: {
                "applied": 0,
                "callbacks": 0,
                "companies": [],
                "roles": [],
            }
        )

        for milestone in trajectory:
            # Parse date
            date_str = milestone.get("discovered_date") or milestone.get(
                "applied_date"
            )
            if not date_str:
                continue

            try:
                date = datetime.strptime(date_str, "%Y-%m-%d")
                if date < six_months_ago:
                    continue

                month_key = date.strftime("%b")
                company = milestone.get("company", "Unknown")
                role = milestone.get("role", "")
                status = milestone.get("status", "Lead")

                monthly_stats[month_key]["applied"] += 1
                monthly_stats[month_key]["companies"].append(company)
                monthly_stats[month_key]["roles"].append(role)

                # Count callbacks (anything beyond Applied/Lead)
                if status not in ["Lead", "Applied", "Rejected", "Ghosted"]:
                    monthly_stats[month_key]["callbacks"] += 1

            except (ValueError, TypeError):
                continue

        # Generate observations from monthly stats
        for month in ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]:
            stats = monthly_stats.get(month)
            if stats and stats["applied"] > 0:
                # Analyze company types
                companies = stats["companies"]
                big_tech = sum(
                    1
                    for c in companies
                    if c in ["Google", "Amazon", "Microsoft", "Meta", "Apple"]
                )

                callback_rate = (
                    f"{stats['callbacks']} callbacks"
                    if stats["callbacks"] > 0
                    else "0 callbacks"
                )

                if big_tech > 0:
                    observations.append(
                        f"  - {month}: Applied to {stats['applied']} jobs "
                        f"({big_tech} Big Tech) → {callback_rate}"
                    )
                else:
                    # Analyze role types
                    etl_roles = sum(
                        1 for r in stats["roles"] if "etl" in r.lower()
                    )
                    if etl_roles > 0:
                        observations.append(
                            f"  - {month}: Focused on ETL roles "
                            f"({stats['callbacks']} callbacks from {stats['applied']} applications)"
                        )
                    else:
                        observations.append(
                            f"  - {month}: Applied to {stats['applied']} startups → {callback_rate}"
                        )

        return observations[:6]  # Limit to 6 months

    def _model_current_path_consequences(
        self,
        trajectory: List[Dict[str, Any]],
        job_requirements: List[str],
        query: str,
    ) -> List[str]:
        """Model probable consequences of current path.

        Args:
            trajectory: Application history
            job_requirements: Requirements for role being considered
            query: Query string to extract role type

        Returns:
            List of timeline consequences
        """
        # Determine role type from requirements
        role_type = self._infer_role_type(job_requirements, query)

        # Calculate probabilities from similar past applications
        similar_apps = self._find_similar_applications(
            trajectory, role_type
        )

        if not similar_apps:
            return [
                "  T+0: 2 hours invested in application",
                "  T+1 week: Probability unknown (no similar past applications)",
                "  T+2 weeks: Outcome unclear",
            ]

        # Calculate statistics
        total = len(similar_apps)
        callbacks = sum(
            1
            for app in similar_apps
            if app.get("status")
            not in ["Lead", "Applied", "Rejected", "Ghosted"]
        )
        interviews = sum(
            1
            for app in similar_apps
            if app.get("status") in ["Technical", "Manager", "Interview"]
        )

        callback_prob = (callbacks / total) * 100 if total > 0 else 0
        interview_prob = (interviews / total) * 100 if total > 0 else 0
        no_response_prob = 100 - callback_prob

        consequences = [
            f"  T+0: 2 hours invested in application",
            f"  T+1 week: {no_response_prob:.0f}% probability no response "
            f"(based on {total} similar past applications)",
            f"  T+2 weeks: {callback_prob:.0f}% probability callback",
            f"  T+1 month: {interview_prob:.0f}% probability interview",
        ]

        return consequences

    def _model_alternative_path(
        self, trajectory: List[Dict[str, Any]], job_requirements: List[str]
    ) -> List[str]:
        """Model alternative career path with better odds.

        Args:
            trajectory: Application history
            job_requirements: Current role requirements

        Returns:
            List of alternative path consequences
        """
        # Find highest success rate role type
        role_stats = self._calculate_role_type_statistics(trajectory)

        if not role_stats:
            return []

        # Find best alternative
        best_role_type = None
        best_callback_rate = 0

        for role_type, stats in role_stats.items():
            if stats["total"] >= 2:  # Need at least 2 samples
                callback_rate = (
                    stats["callbacks"] / stats["total"]
                    if stats["total"] > 0
                    else 0
                )
                if callback_rate > best_callback_rate:
                    best_callback_rate = callback_rate
                    best_role_type = role_type

        if not best_role_type or best_callback_rate == 0:
            return []

        stats = role_stats[best_role_type]
        callback_prob = (best_callback_rate * 100)
        interview_prob = (
            (stats["interviews"] / stats["total"] * 100)
            if stats["total"] > 0
            else 0
        )

        return [
            f"  Apply to {best_role_type.upper()}-focused role",
            f"  T+0: 2 hours invested",
            f"  T+1 week: {callback_prob:.0f}% probability callback "
            f"(based on {stats['total']} similar past applications)",
            f"  T+2 weeks: {interview_prob:.0f}% probability interview",
        ]

    def _compare_path_outcomes(
        self, trajectory: List[Dict[str, Any]], job_requirements: List[str]
    ) -> List[str]:
        """Compare expected outcomes of different paths.

        Args:
            trajectory: Application history
            job_requirements: Current role requirements

        Returns:
            List of comparison metrics
        """
        # Get current path stats
        role_type = self._infer_role_type(job_requirements, "")
        similar_apps = self._find_similar_applications(trajectory, role_type)

        if not similar_apps:
            return []

        current_interviews = sum(
            1
            for app in similar_apps
            if app.get("status") in ["Technical", "Manager", "Interview"]
        )
        current_interview_rate = (
            current_interviews / len(similar_apps)
            if len(similar_apps) > 0
            else 0
        )

        # Get alternative path stats
        role_stats = self._calculate_role_type_statistics(trajectory)
        best_role_type = None
        best_interview_rate = 0

        for rt, stats in role_stats.items():
            if stats["total"] >= 2:
                interview_rate = (
                    stats["interviews"] / stats["total"]
                    if stats["total"] > 0
                    else 0
                )
                if interview_rate > best_interview_rate:
                    best_interview_rate = interview_rate
                    best_role_type = rt

        if not best_role_type:
            return []

        # Calculate expected interviews over 3 months
        current_expected = current_interview_rate * 10  # Assume 10 apps
        alt_expected = best_interview_rate * 10

        roi_multiplier = (
            alt_expected / current_expected if current_expected > 0 else 0
        )

        comparisons = [
            f"  - {role_type.capitalize()} path: 3 months → {current_expected:.1f} interviews expected",
            f"  - {best_role_type.upper()} path: 3 months → {alt_expected:.1f} interviews expected",
        ]

        return comparisons

    def _generate_path_recommendation(
        self, trajectory: List[Dict[str, Any]], job_requirements: List[str]
    ) -> str:
        """Generate path recommendation based on trajectory analysis.

        Args:
            trajectory: Application history
            job_requirements: Current role requirements

        Returns:
            Recommendation string
        """
        # Calculate best path ROI
        role_type = self._infer_role_type(job_requirements, "")
        role_stats = self._calculate_role_type_statistics(trajectory)

        best_role_type = None
        best_roi = 0
        current_roi = 0

        for rt, stats in role_stats.items():
            if stats["total"] >= 2:
                roi = (
                    stats["callbacks"] / stats["total"]
                    if stats["total"] > 0
                    else 0
                )
                if rt.lower() == role_type.lower():
                    current_roi = roi
                if roi > best_roi:
                    best_roi = roi
                    best_role_type = rt

        if not best_role_type or best_roi == 0:
            return "Insufficient data for recommendation. Apply and gather data."

        if best_roi > current_roi * 1.5:
            roi_multiplier = best_roi / current_roi if current_roi > 0 else 0
            return (
                f"{best_role_type.upper()} path has {roi_multiplier:.1f}x better ROI "
                f"based on your trajectory. Prioritize {best_role_type}-focused roles."
            )
        else:
            return "Current path shows reasonable success rate. Proceed with application."

    def _infer_role_type(
        self, job_requirements: List[str], query: str
    ) -> str:
        """Infer role type from requirements and query.

        Args:
            job_requirements: List of requirements
            query: Query string

        Returns:
            Inferred role type
        """
        combined = " ".join(job_requirements).lower() + " " + query.lower()

        if "big data" in combined or "hadoop" in combined or "spark" in combined:
            return "big data"
        elif "etl" in combined or "data engineer" in combined:
            return "etl"
        elif "data warehouse" in combined or "dwh" in combined:
            return "dwh"
        elif "analyst" in combined:
            return "analyst"
        else:
            return "general"

    def _find_similar_applications(
        self, trajectory: List[Dict[str, Any]], role_type: str
    ) -> List[Dict[str, Any]]:
        """Find similar applications from trajectory.

        Args:
            trajectory: Application history
            role_type: Type of role to match

        Returns:
            List of similar applications
        """
        similar = []

        for app in trajectory:
            role = app.get("role", "").lower()

            # Match by role type
            if role_type == "big data" and any(
                keyword in role for keyword in ["big data", "hadoop", "spark"]
            ):
                similar.append(app)
            elif role_type == "etl" and any(
                keyword in role for keyword in ["etl", "data engineer"]
            ):
                similar.append(app)
            elif role_type == "dwh" and any(
                keyword in role for keyword in ["warehouse", "dwh"]
            ):
                similar.append(app)
            elif role_type == "analyst" and "analyst" in role:
                similar.append(app)
            elif role_type == "general":
                # Include all for general category
                similar.append(app)

        return similar

    def _calculate_role_type_statistics(
        self, trajectory: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, int]]:
        """Calculate statistics by role type.

        Args:
            trajectory: Application history

        Returns:
            Dictionary mapping role types to their statistics
        """
        role_stats = {}

        for role_type in ["etl", "big data", "dwh", "analyst"]:
            similar_apps = self._find_similar_applications(
                trajectory, role_type
            )

            if similar_apps:
                callbacks = sum(
                    1
                    for app in similar_apps
                    if app.get("status")
                    not in ["Lead", "Applied", "Rejected", "Ghosted"]
                )
                interviews = sum(
                    1
                    for app in similar_apps
                    if app.get("status")
                    in ["Technical", "Manager", "Interview"]
                )

                role_stats[role_type] = {
                    "total": len(similar_apps),
                    "callbacks": callbacks,
                    "interviews": interviews,
                }

        return role_stats

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
