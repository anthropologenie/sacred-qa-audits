"""Smriti Agent - Memory and pattern recognition agent.

This agent specializes in retrieving historical context, recognizing patterns,
and tracing lineages from past decisions and experiences.
"""

from typing import Any, Dict, List

from .base_agent import BaseAgent


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

        INTEGRATION-AWARE: If context contains interview_history or
        application_history, Smriti activates strongly to provide factual
        pattern analysis from real data.

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
        strength = 0.0

        # INTEGRATION: Check for real historical data from jobs database
        if "smriti_history" in context or "smriti_patterns" in context:
            strength += 0.4  # Strong activation for factual pattern analysis

        # INTEGRATION: Check for company-specific history
        if "smriti_companies" in context:
            # Extract company name from query if present
            company_mentioned = self._extract_company_from_query(
                query_lower, context.get("smriti_companies", {})
            )
            if company_mentioned:
                strength += 0.3  # Company has history in our database

        # If integration context triggered activation, return early
        if strength >= 0.7:
            return min(strength, 1.0)

        # EXISTING LOGIC: Keyword-based activation
        # Check for explicit pattern/history language
        has_pattern = "pattern" in query_lower or "recurring" in query_lower
        if has_pattern:
            return max(0.90, strength)

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
            return max(base_activation, strength)

        # Check for learning from experience
        has_learning = any(
            word in query_lower for word in self.LEARNING_WORDS
        )
        if has_learning:
            return max(0.75, strength)

        # Generic historical words like "before", "earlier" are too common
        # Only activate if explicitly asking about history
        if "remember" in query_lower:
            return max(0.70, strength)

        # Check if context includes substantial historical data
        decision_history = context.get("history", [])
        if len(decision_history) > 3:
            # Significant history available, mild activation
            return max(0.40, strength)

        # No history indicators
        return max(0.15, strength)

    def _deliberate(
        self, query: str, context: Dict[str, Any], circuits: List[str]
    ) -> str:
        """Generate historical analysis and pattern recognition response.

        INTEGRATION-AWARE: If context contains interview_history or
        application_history, performs factual pattern analysis using
        real data from the jobs database.

        Args:
            query: The question or task to process
            context: Additional contextual information
            circuits: List of circuits that have been activated

        Returns:
            Historical and pattern analysis
        """
        # INTEGRATION: Check for real historical data from jobs database
        if "smriti_history" in context or "smriti_patterns" in context:
            circuits.append("integration_pattern_analysis")
            return self._perform_factual_pattern_analysis(
                context.get("smriti_history", []),
                context.get("smriti_patterns", {}),
                context.get("smriti_companies", {}),
                circuits,
            )

        # EXISTING LOGIC: Parliament decision history analysis
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

    def _extract_company_from_query(
        self, query_lower: str, company_history: Dict[str, List[Dict[str, Any]]]
    ) -> bool:
        """Check if any company from history is mentioned in the query.

        Args:
            query_lower: Lowercased query string
            company_history: Dictionary mapping company names to applications

        Returns:
            True if a company from history is mentioned
        """
        for company in company_history.keys():
            if company.lower() in query_lower:
                return True
        return False

    def _perform_factual_pattern_analysis(
        self,
        interview_history: List[Dict[str, Any]],
        performance_patterns: Dict[str, Any],
        company_history: Dict[str, List[Dict[str, Any]]],
        circuits: List[str],
    ) -> str:
        """Perform factual pattern analysis using real interview/application data.

        This method analyzes actual historical data to identify patterns,
        strengths, weaknesses, and success factors.

        Args:
            interview_history: List of past interview questions with ratings
            performance_patterns: Performance metrics by topic
            company_history: Application history grouped by company
            circuits: Active circuits list (modified in place)

        Returns:
            Detailed factual pattern analysis with specific numbers
        """
        circuits.append("factual_memory_analysis")

        response_parts = ["Historical pattern analysis from your data:\n"]

        # Analyze company patterns
        if company_history:
            company_analysis = self._analyze_company_patterns(
                company_history
            )
            if company_analysis:
                response_parts.append("Company patterns:")
                response_parts.extend(company_analysis)
                response_parts.append("")

        # Analyze topic performance from interview questions
        if interview_history and performance_patterns:
            topic_analysis = self._analyze_topic_performance(
                interview_history, performance_patterns
            )
            if topic_analysis:
                total_questions = len(interview_history)
                response_parts.append(
                    f"Topic performance (from {total_questions} interview questions):"
                )
                response_parts.extend(topic_analysis)
                response_parts.append("")

        # Analyze success patterns
        if company_history:
            success_analysis = self._analyze_success_patterns(
                company_history
            )
            if success_analysis:
                response_parts.append("Success pattern detected:")
                response_parts.extend(success_analysis)
                response_parts.append("")

        # Generate recommendation based on patterns
        recommendation = self._generate_pattern_recommendation(
            company_history, performance_patterns
        )
        if recommendation:
            response_parts.append("Recommendation based on patterns:")
            response_parts.append(recommendation)

        return "\n".join(response_parts)

    def _analyze_company_patterns(
        self, company_history: Dict[str, List[Dict[str, Any]]]
    ) -> List[str]:
        """Analyze application patterns by company.

        Args:
            company_history: Dictionary mapping companies to applications

        Returns:
            List of pattern observations
        """
        patterns = []

        # Group companies by size/type if possible
        big_tech = ["Google", "Amazon", "Microsoft", "Meta", "Apple"]
        startups = []
        other = []

        for company, apps in company_history.items():
            if company in big_tech:
                # Analyze big tech patterns
                total = len(apps)
                callbacks = sum(
                    1
                    for app in apps
                    if app.get("status")
                    not in ["Lead", "Applied", "Rejected", "Ghosted"]
                )
                patterns.append(
                    f"  - Past {company} applications: {total} attempts, {callbacks} callbacks"
                )
            else:
                # Collect for later analysis
                other.append((company, apps))

        # Analyze startup patterns (companies with multiple applications)
        startup_total = 0
        startup_callbacks = 0
        for company, apps in other:
            startup_total += len(apps)
            startup_callbacks += sum(
                1
                for app in apps
                if app.get("status")
                not in ["Lead", "Applied", "Rejected", "Ghosted"]
            )

        if startup_total > 0:
            callback_rate = (startup_callbacks / startup_total * 100)
            patterns.append(
                f"  - Past startups/mid-size: {startup_total} applications, "
                f"{startup_callbacks} callbacks ({callback_rate:.0f}%)"
            )

        return patterns

    def _analyze_topic_performance(
        self,
        interview_history: List[Dict[str, Any]],
        performance_patterns: Dict[str, Any],
    ) -> List[str]:
        """Analyze performance by interview topic.

        Args:
            interview_history: List of interview questions
            performance_patterns: Performance metrics by topic

        Returns:
            List of performance observations
        """
        performance = []

        # Sort topics by average rating to identify weaknesses
        topic_ratings = []
        for topic, stats in performance_patterns.items():
            if stats.get("avg_rating") is not None:
                topic_ratings.append((topic, stats))

        # Sort by rating (ascending - worst first)
        topic_ratings.sort(key=lambda x: x[1]["avg_rating"])

        # Show top 3-5 weaknesses and strengths
        weaknesses = topic_ratings[:3]  # Worst 3
        strengths = topic_ratings[-2:]  # Best 2

        for topic, stats in weaknesses:
            avg_rating = stats["avg_rating"]
            question_count = stats["total_questions"]
            status = self._get_performance_status(avg_rating)

            performance.append(
                f"  - {topic}: {question_count} questions, "
                f"avg rating {avg_rating:.1f}/5 → {status}"
            )

        if strengths:
            performance.append("")
            performance.append("  Strengths:")
            for topic, stats in strengths:
                avg_rating = stats["avg_rating"]
                question_count = stats["total_questions"]
                performance.append(
                    f"  - {topic}: {question_count} questions, "
                    f"avg rating {avg_rating:.1f}/5 → Strong"
                )

        return performance

    def _get_performance_status(self, avg_rating: float) -> str:
        """Convert average rating to performance status.

        Args:
            avg_rating: Average rating (1-5)

        Returns:
            Performance status string
        """
        if avg_rating < 2.0:
            return "Critical gap"
        elif avg_rating < 2.5:
            return "Weak area"
        elif avg_rating < 3.5:
            return "Moderate"
        elif avg_rating < 4.0:
            return "Good"
        else:
            return "Strong"

    def _analyze_success_patterns(
        self, company_history: Dict[str, List[Dict[str, Any]]]
    ) -> List[str]:
        """Identify success patterns from application outcomes.

        Args:
            company_history: Application history by company

        Returns:
            List of success pattern observations
        """
        patterns = []

        # Analyze by role type if available
        etl_roles = 0
        etl_callbacks = 0
        big_data_roles = 0
        big_data_callbacks = 0

        for company, apps in company_history.items():
            for app in apps:
                role = app.get("role", "").lower()

                # Categorize by role type
                if any(
                    keyword in role for keyword in ["etl", "data engineer"]
                ):
                    etl_roles += 1
                    if app.get("status") not in [
                        "Lead",
                        "Applied",
                        "Rejected",
                        "Ghosted",
                    ]:
                        etl_callbacks += 1
                elif any(
                    keyword in role for keyword in ["big data", "hadoop", "spark"]
                ):
                    big_data_roles += 1
                    if app.get("status") not in [
                        "Lead",
                        "Applied",
                        "Rejected",
                        "Ghosted",
                    ]:
                        big_data_callbacks += 1

        # Report patterns
        if etl_roles > 0:
            etl_rate = (etl_callbacks / etl_roles * 100)
            patterns.append(
                f"  - Roles emphasizing ETL/Data Engineering: "
                f"{etl_callbacks}/{etl_roles} callbacks ({etl_rate:.0f}%)"
            )

        if big_data_roles > 0:
            bd_rate = (big_data_callbacks / big_data_roles * 100)
            patterns.append(
                f"  - Roles emphasizing Big Data: "
                f"{big_data_callbacks}/{big_data_roles} callbacks ({bd_rate:.0f}%)"
            )

        return patterns

    def _generate_pattern_recommendation(
        self,
        company_history: Dict[str, List[Dict[str, Any]]],
        performance_patterns: Dict[str, Any],
    ) -> str:
        """Generate recommendation based on identified patterns.

        Args:
            company_history: Application history
            performance_patterns: Performance metrics

        Returns:
            Recommendation string
        """
        recommendations = []

        # Identify weakest topics
        weak_topics = []
        for topic, stats in performance_patterns.items():
            if (
                stats.get("avg_rating") is not None
                and stats["avg_rating"] < 2.5
            ):
                weak_topics.append(topic)

        # Identify successful company types
        big_tech_success = False
        startup_success = False

        big_tech_names = ["Google", "Amazon", "Microsoft", "Meta", "Apple"]
        big_tech_total = 0
        big_tech_callbacks = 0
        startup_total = 0
        startup_callbacks = 0

        for company, apps in company_history.items():
            if company in big_tech_names:
                big_tech_total += len(apps)
                big_tech_callbacks += sum(
                    1
                    for app in apps
                    if app.get("status")
                    not in ["Lead", "Applied", "Rejected", "Ghosted"]
                )
            else:
                startup_total += len(apps)
                startup_callbacks += sum(
                    1
                    for app in apps
                    if app.get("status")
                    not in ["Lead", "Applied", "Rejected", "Ghosted"]
                )

        if big_tech_total > 0:
            big_tech_rate = big_tech_callbacks / big_tech_total
            big_tech_success = big_tech_rate > 0.3

        if startup_total > 0:
            startup_rate = startup_callbacks / startup_total
            startup_success = startup_rate > 0.3

        # Build recommendation
        if startup_success and not big_tech_success:
            recommendations.append(
                "Target startups/mid-size companies where you have higher success rate."
            )
        elif weak_topics:
            topic_list = ", ".join(weak_topics[:2])
            recommendations.append(
                f"Strengthen {topic_list} fundamentals before applying to competitive roles."
            )

        if not big_tech_success and big_tech_total > 0:
            recommendations.append(
                "Avoid Big Tech until core skills strengthen to 3.5+/5."
            )

        return " ".join(recommendations) if recommendations else ""

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
