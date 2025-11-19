"""Jobs database integration for Kragentic Parliament.

This module provides integration with the jobs-application-automation SQLite
database, enabling the Parliament to access real-world job hunting data for
grounded decision-making.
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..circuits.activation_tracker import ParliamentDecisionTrace
from .base_integration import BaseIntegration


class JobsDBIntegration(BaseIntegration):
    """Integration with jobs-application-automation SQLite database.

    This integration provides bidirectional data flow between the Kragentic
    Parliament and the job hunting tracker:

    DIRECTION 1 (Advisory): Parliament queries job data to provide intelligent
    career advice based on actual skills, interview history, and learning gaps.

    DIRECTION 2 (Training): Job outcomes validate parliamentary decisions and
    calibrate agent activation thresholds for improved accuracy.

    Attributes:
        db_path: Path to the jobs-tracker.db SQLite database
        conn: SQLite connection object
        cursor: SQLite cursor for queries
    """

    def __init__(self, db_path: Optional[str] = None) -> None:
        """Initialize the jobs database integration.

        Args:
            db_path: Path to jobs-tracker.db. If None, uses default relative path.
        """
        super().__init__(name="jobs_db")

        # Set default path if not provided
        if db_path is None:
            # Default: ../jobs-application-automation/data/jobs-tracker.db
            current_file = Path(__file__).resolve()
            project_root = current_file.parent.parent.parent
            db_path = str(
                project_root.parent
                / "jobs-application-automation"
                / "data"
                / "jobs-tracker.db"
            )

        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None

    def connect(self) -> bool:
        """Establish connection to the jobs database.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Enable column access by name
            self.cursor = self.conn.cursor()
            self.connected = True
            return True
        except sqlite3.Error as e:
            print(f"Error connecting to jobs database: {e}")
            self.connected = False
            return False

    def disconnect(self) -> None:
        """Close connection to the jobs database."""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None
            self.connected = False

    def fetch_context(
        self, query_type: str, **kwargs: Any
    ) -> Dict[str, Any]:
        """Fetch relevant context from jobs database.

        Supported query types:
            - 'job_evaluation': Get job details for application decision
            - 'interview_prep': Get interview patterns and weak areas
            - 'learning_priority': Get study topics and gaps
            - 'skill_assessment': Get current skill ratings

        Args:
            query_type: Type of query to execute
            **kwargs: Query-specific parameters

        Returns:
            Dictionary containing relevant context data

        Raises:
            ValueError: If query_type is not supported
            ConnectionError: If not connected to database
        """
        if not self.connected:
            raise ConnectionError(
                "Not connected to jobs database. Call connect() first."
            )

        if query_type == "job_evaluation":
            return self._fetch_job_evaluation_context(**kwargs)
        elif query_type == "interview_prep":
            return self._fetch_interview_prep_context(**kwargs)
        elif query_type == "learning_priority":
            return self._fetch_learning_priority_context(**kwargs)
        elif query_type == "skill_assessment":
            return self._fetch_skill_assessment_context(**kwargs)
        else:
            raise ValueError(
                f"Unsupported query_type: {query_type}. "
                f"Supported types: {self.get_supported_query_types()}"
            )

    def _fetch_job_evaluation_context(
        self, opportunity_id: Optional[int] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        """Fetch context for job application evaluation.

        Args:
            opportunity_id: Optional specific opportunity to evaluate
            **kwargs: Additional parameters

        Returns:
            Context containing job details, user skills, similar applications
        """
        context: Dict[str, Any] = {}

        # Get job details if opportunity_id provided
        if opportunity_id is not None:
            self.cursor.execute(
                """
                SELECT id, company, role, tech_stack, salary_range,
                       is_remote, domain_match, status, priority, notes
                FROM opportunities
                WHERE id = ?
                """,
                (opportunity_id,),
            )
            row = self.cursor.fetchone()
            if row:
                context["job"] = dict(row)
                context["job_requirements"] = (
                    row["tech_stack"].split(",")
                    if row["tech_stack"]
                    else []
                )

        # Get user's current skill levels
        context["user_skills"] = self._get_user_skills()

        # Get similar past applications
        if opportunity_id is not None and "job" in context:
            context["similar_applications"] = (
                self._get_similar_applications(context["job"]["company"])
            )

        # Get learning gaps
        context["learning_gaps"] = self._get_learning_gaps()

        return context

    def _fetch_interview_prep_context(
        self, topic: Optional[str] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        """Fetch context for interview preparation.

        Args:
            topic: Optional specific topic to focus on
            **kwargs: Additional parameters

        Returns:
            Context containing weak topics, past questions, patterns
        """
        context: Dict[str, Any] = {}

        # Get learning gaps (weak areas)
        context["learning_gaps"] = self._get_learning_gaps()

        # Get past interview questions
        if topic:
            context["past_questions"] = self._get_questions_by_topic(topic)
        else:
            context["past_questions"] = self._get_recent_questions()

        # Get interview performance patterns
        context["performance_patterns"] = self._get_performance_patterns()

        # Get upcoming interviews
        context["upcoming_interviews"] = self._get_upcoming_interviews()

        return context

    def _fetch_learning_priority_context(
        self, **kwargs: Any
    ) -> Dict[str, Any]:
        """Fetch context for learning priority planning.

        Returns:
            Context containing learning gaps, study topics, confidence levels
        """
        context: Dict[str, Any] = {}

        # Get learning gaps ordered by importance
        context["learning_gaps"] = self._get_learning_gaps()

        # Get study topics with status
        context["study_topics"] = self._get_study_topics()

        # Get recent learning sessions
        context["recent_sessions"] = self._get_recent_learning_sessions()

        # Get confidence trends
        context["confidence_trends"] = self._get_confidence_trends()

        return context

    def _fetch_skill_assessment_context(
        self, skill: Optional[str] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        """Fetch context for skill reality check.

        Args:
            skill: Optional specific skill to assess
            **kwargs: Additional parameters

        Returns:
            Context containing current skill ratings, trends
        """
        context: Dict[str, Any] = {}

        # Get all user skills
        context["user_skills"] = self._get_user_skills()

        # Get skill-specific details if requested
        if skill:
            context["skill_details"] = self._get_skill_details(skill)

        # Get skill trends over time
        context["skill_trends"] = self._get_skill_trends()

        return context

    def _get_user_skills(self) -> Dict[str, float]:
        """Extract user's current skill levels from interview questions.

        Returns:
            Dictionary mapping skill names to average ratings (1-5)
        """
        try:
            self.cursor.execute(
                """
                SELECT question_type, AVG(my_rating) as avg_rating
                FROM interview_questions
                WHERE my_rating IS NOT NULL
                GROUP BY question_type
                """
            )
            skills = {}
            for row in self.cursor.fetchall():
                if row["question_type"]:
                    skills[row["question_type"]] = round(
                        row["avg_rating"], 2
                    )
            return skills
        except sqlite3.Error:
            return {}

    def _get_learning_gaps(self) -> List[Dict[str, Any]]:
        """Get learning gaps ordered by importance.

        Returns:
            List of dictionaries containing gap information
        """
        try:
            self.cursor.execute(
                """
                SELECT
                    st.name,
                    st.category,
                    st.priority,
                    st.status,
                    AVG(iq.my_rating) as current_rating,
                    COUNT(iq.id) as question_count
                FROM study_topics st
                LEFT JOIN interview_questions iq
                    ON st.category = iq.question_type
                WHERE st.status != 'Completed'
                GROUP BY st.name, st.category, st.priority, st.status
                HAVING current_rating < 3.5 OR current_rating IS NULL
                ORDER BY st.priority DESC, current_rating ASC
                """
            )
            return [dict(row) for row in self.cursor.fetchall()]
        except sqlite3.Error:
            return []

    def _get_similar_applications(
        self, company: str
    ) -> List[Dict[str, Any]]:
        """Get similar past applications for pattern analysis.

        Args:
            company: Company name to search for

        Returns:
            List of similar opportunities
        """
        try:
            self.cursor.execute(
                """
                SELECT id, company, role, status, domain_match,
                       applied_date, notes
                FROM opportunities
                WHERE company = ? OR company LIKE ?
                ORDER BY discovered_date DESC
                LIMIT 5
                """,
                (company, f"%{company}%"),
            )
            return [dict(row) for row in self.cursor.fetchall()]
        except sqlite3.Error:
            return []

    def _get_questions_by_topic(self, topic: str) -> List[Dict[str, Any]]:
        """Get past interview questions for a specific topic.

        Args:
            topic: Question topic/type to filter by

        Returns:
            List of questions with performance data
        """
        try:
            self.cursor.execute(
                """
                SELECT
                    iq.question_text,
                    iq.question_type,
                    iq.difficulty,
                    iq.my_rating,
                    iq.learned,
                    o.company
                FROM interview_questions iq
                LEFT JOIN opportunities o ON iq.opportunity_id = o.id
                WHERE iq.question_type = ?
                ORDER BY iq.created_at DESC
                LIMIT 10
                """,
                (topic,),
            )
            return [dict(row) for row in self.cursor.fetchall()]
        except sqlite3.Error:
            return []

    def _get_recent_questions(self) -> List[Dict[str, Any]]:
        """Get recent interview questions across all topics.

        Returns:
            List of recent questions
        """
        try:
            self.cursor.execute(
                """
                SELECT
                    iq.question_text,
                    iq.question_type,
                    iq.difficulty,
                    iq.my_rating,
                    iq.learned,
                    o.company
                FROM interview_questions iq
                LEFT JOIN opportunities o ON iq.opportunity_id = o.id
                ORDER BY iq.created_at DESC
                LIMIT 20
                """
            )
            return [dict(row) for row in self.cursor.fetchall()]
        except sqlite3.Error:
            return []

    def _get_performance_patterns(self) -> Dict[str, Any]:
        """Analyze interview performance patterns.

        Returns:
            Dictionary with performance metrics by topic
        """
        try:
            self.cursor.execute(
                """
                SELECT
                    question_type,
                    COUNT(*) as total_questions,
                    AVG(my_rating) as avg_rating,
                    SUM(CASE WHEN learned = 1 THEN 1 ELSE 0 END) as learned_count,
                    AVG(CASE
                        WHEN difficulty = 'Easy' THEN 1
                        WHEN difficulty = 'Medium' THEN 2
                        WHEN difficulty = 'Hard' THEN 3
                    END) as avg_difficulty
                FROM interview_questions
                WHERE my_rating IS NOT NULL
                GROUP BY question_type
                """
            )
            patterns = {}
            for row in self.cursor.fetchall():
                patterns[row["question_type"]] = dict(row)
            return patterns
        except sqlite3.Error:
            return {}

    def _get_upcoming_interviews(self) -> List[Dict[str, Any]]:
        """Get upcoming scheduled interviews.

        Returns:
            List of upcoming interview interactions
        """
        try:
            self.cursor.execute(
                """
                SELECT
                    i.type,
                    i.date,
                    i.time,
                    i.meet_link,
                    o.company,
                    o.role,
                    o.status
                FROM interactions i
                JOIN opportunities o ON i.opportunity_id = o.id
                WHERE i.date >= DATE('now')
                  AND i.type = 'Interview'
                ORDER BY i.date ASC, i.time ASC
                LIMIT 5
                """
            )
            return [dict(row) for row in self.cursor.fetchall()]
        except sqlite3.Error:
            return []

    def _get_study_topics(self) -> List[Dict[str, Any]]:
        """Get study topics with their current status.

        Returns:
            List of study topics
        """
        try:
            self.cursor.execute(
                """
                SELECT
                    name,
                    category,
                    priority,
                    status,
                    estimated_hours,
                    actual_hours,
                    deadline
                FROM study_topics
                ORDER BY priority DESC, deadline ASC
                """
            )
            return [dict(row) for row in self.cursor.fetchall()]
        except sqlite3.Error:
            return []

    def _get_recent_learning_sessions(self) -> List[Dict[str, Any]]:
        """Get recent learning sessions.

        Returns:
            List of recent learning sessions
        """
        try:
            self.cursor.execute(
                """
                SELECT
                    ls.duration_minutes,
                    ls.what_was_learned,
                    ls.confidence_before,
                    ls.confidence_after,
                    ls.session_date,
                    st.name as topic_name,
                    st.category
                FROM learning_sessions ls
                JOIN study_topics st ON ls.topic_id = st.id
                ORDER BY ls.session_date DESC
                LIMIT 10
                """
            )
            return [dict(row) for row in self.cursor.fetchall()]
        except sqlite3.Error:
            return []

    def _get_confidence_trends(self) -> Dict[str, Any]:
        """Calculate confidence trends over time.

        Returns:
            Dictionary with confidence trend data
        """
        try:
            self.cursor.execute(
                """
                SELECT
                    st.category,
                    AVG(ls.confidence_before) as avg_before,
                    AVG(ls.confidence_after) as avg_after,
                    AVG(ls.confidence_after - ls.confidence_before) as avg_improvement
                FROM learning_sessions ls
                JOIN study_topics st ON ls.topic_id = st.id
                GROUP BY st.category
                """
            )
            trends = {}
            for row in self.cursor.fetchall():
                trends[row["category"]] = {
                    "avg_before": round(row["avg_before"], 2),
                    "avg_after": round(row["avg_after"], 2),
                    "avg_improvement": round(row["avg_improvement"], 2),
                }
            return trends
        except sqlite3.Error:
            return {}

    def _get_skill_details(self, skill: str) -> Dict[str, Any]:
        """Get detailed information about a specific skill.

        Args:
            skill: Skill name to analyze

        Returns:
            Dictionary with skill details
        """
        try:
            self.cursor.execute(
                """
                SELECT
                    COUNT(*) as total_questions,
                    AVG(my_rating) as avg_rating,
                    MAX(my_rating) as best_rating,
                    MIN(my_rating) as worst_rating,
                    SUM(CASE WHEN learned = 1 THEN 1 ELSE 0 END) as learned_count
                FROM interview_questions
                WHERE question_type = ? AND my_rating IS NOT NULL
                """,
                (skill,),
            )
            row = self.cursor.fetchone()
            return dict(row) if row else {}
        except sqlite3.Error:
            return {}

    def _get_skill_trends(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get skill rating trends over time.

        Returns:
            Dictionary mapping skills to their rating history
        """
        try:
            self.cursor.execute(
                """
                SELECT
                    question_type,
                    my_rating,
                    created_at
                FROM interview_questions
                WHERE my_rating IS NOT NULL
                ORDER BY question_type, created_at ASC
                """
            )
            trends: Dict[str, List[Dict[str, Any]]] = {}
            for row in self.cursor.fetchall():
                skill = row["question_type"]
                if skill not in trends:
                    trends[skill] = []
                trends[skill].append(
                    {"rating": row["my_rating"], "date": row["created_at"]}
                )
            return trends
        except sqlite3.Error:
            return {}

    def enrich_agent_context(
        self, agent_name: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add agent-specific external data to context.

        Enriches context with data relevant to each agent's domain:
            - krudi: Current skill levels for reality grounding
            - parva: Career trajectory for temporal analysis
            - shanti: Work-life indicators for balance assessment
            - rudi: Learning progress for transformation potential
            - maya: Historical outcomes for scenario modeling
            - smriti: Interview history for pattern recognition

        Args:
            agent_name: Name of the agent to enrich context for
            context: Existing context dictionary

        Returns:
            Enriched context dictionary

        Raises:
            ConnectionError: If not connected to database
        """
        if not self.connected:
            raise ConnectionError(
                "Not connected to jobs database. Call connect() first."
            )

        enriched = context.copy()

        if agent_name == "krudi":
            # Reality grounding: current skill levels
            enriched["krudi_skills"] = self._get_user_skills()
            enriched["krudi_constraints"] = self._get_reality_constraints()

        elif agent_name == "parva":
            # Temporal causality: career trajectory
            enriched["parva_trajectory"] = self._get_career_trajectory()
            enriched["parva_timeline"] = self._get_application_timeline()

        elif agent_name == "shanti":
            # Equilibrium: work-life balance indicators
            enriched["shanti_balance"] = self._get_work_life_indicators()
            enriched["shanti_preferences"] = self._get_job_preferences()

        elif agent_name == "rudi":
            # Transformation: learning and growth
            enriched["rudi_learning"] = self._get_learning_progress()
            enriched["rudi_growth"] = self._get_growth_potential()

        elif agent_name == "maya":
            # Simulation: historical outcomes for modeling
            enriched["maya_outcomes"] = self._get_historical_outcomes()
            enriched["maya_patterns"] = self._get_outcome_patterns()

        elif agent_name == "smriti":
            # Memory: interview history and patterns
            enriched["smriti_history"] = self._get_interview_history()
            enriched["smriti_patterns"] = self._get_performance_patterns()
            enriched["smriti_companies"] = self._get_company_history()

        return enriched

    def _get_reality_constraints(self) -> Dict[str, Any]:
        """Get reality constraints (current situation).

        Returns:
            Dictionary with current constraints
        """
        try:
            self.cursor.execute(
                """
                SELECT
                    COUNT(*) as total_applications,
                    SUM(CASE WHEN status = 'Applied' THEN 1 ELSE 0 END) as pending_count,
                    SUM(CASE WHEN status IN ('Technical', 'Manager') THEN 1 ELSE 0 END) as active_interviews
                FROM opportunities
                """
            )
            return dict(self.cursor.fetchone())
        except sqlite3.Error:
            return {}

    def _get_career_trajectory(self) -> List[Dict[str, Any]]:
        """Get career progression timeline.

        Returns:
            List of career milestones
        """
        try:
            self.cursor.execute(
                """
                SELECT
                    company,
                    role,
                    status,
                    discovered_date,
                    applied_date,
                    offer_date
                FROM opportunities
                WHERE status IN ('Applied', 'Technical', 'Manager', 'Offer', 'Accepted')
                ORDER BY discovered_date ASC
                """
            )
            return [dict(row) for row in self.cursor.fetchall()]
        except sqlite3.Error:
            return []

    def _get_application_timeline(self) -> Dict[str, Any]:
        """Get application timeline statistics.

        Returns:
            Dictionary with timeline metrics
        """
        try:
            self.cursor.execute(
                """
                SELECT
                    MIN(discovered_date) as first_application,
                    MAX(discovered_date) as latest_application,
                    COUNT(*) as total_count,
                    AVG(JULIANDAY(applied_date) - JULIANDAY(discovered_date)) as avg_days_to_apply
                FROM opportunities
                WHERE applied_date IS NOT NULL
                """
            )
            return dict(self.cursor.fetchone())
        except sqlite3.Error:
            return {}

    def _get_work_life_indicators(self) -> Dict[str, Any]:
        """Get work-life balance indicators.

        Returns:
            Dictionary with balance metrics
        """
        try:
            self.cursor.execute(
                """
                SELECT
                    SUM(CASE WHEN is_remote = 1 THEN 1 ELSE 0 END) as remote_count,
                    COUNT(*) as total_count,
                    AVG(CASE
                        WHEN priority = 'High' THEN 3
                        WHEN priority = 'Medium' THEN 2
                        ELSE 1
                    END) as avg_priority
                FROM opportunities
                WHERE status NOT IN ('Rejected', 'Declined', 'Ghosted')
                """
            )
            row = self.cursor.fetchone()
            result = dict(row)
            if result["total_count"] > 0:
                result["remote_ratio"] = (
                    result["remote_count"] / result["total_count"]
                )
            return result
        except sqlite3.Error:
            return {}

    def _get_job_preferences(self) -> Dict[str, Any]:
        """Extract job preferences from application history.

        Returns:
            Dictionary with preference indicators
        """
        try:
            self.cursor.execute(
                """
                SELECT
                    domain_match,
                    COUNT(*) as count
                FROM opportunities
                GROUP BY domain_match
                """
            )
            preferences = {}
            for row in self.cursor.fetchall():
                preferences[row["domain_match"]] = row["count"]
            return preferences
        except sqlite3.Error:
            return {}

    def _get_learning_progress(self) -> Dict[str, Any]:
        """Get overall learning progress metrics.

        Returns:
            Dictionary with learning progress data
        """
        try:
            self.cursor.execute(
                """
                SELECT
                    COUNT(*) as total_sessions,
                    SUM(duration_minutes) as total_minutes,
                    AVG(confidence_after - confidence_before) as avg_improvement
                FROM learning_sessions
                """
            )
            return dict(self.cursor.fetchone())
        except sqlite3.Error:
            return {}

    def _get_growth_potential(self) -> Dict[str, Any]:
        """Calculate growth potential based on learning trends.

        Returns:
            Dictionary with growth metrics
        """
        try:
            self.cursor.execute(
                """
                SELECT
                    st.category,
                    st.status,
                    COUNT(ls.id) as session_count,
                    AVG(ls.confidence_after) as current_confidence
                FROM study_topics st
                LEFT JOIN learning_sessions ls ON st.id = ls.topic_id
                GROUP BY st.category, st.status
                """
            )
            potential = {}
            for row in self.cursor.fetchall():
                potential[row["category"]] = dict(row)
            return potential
        except sqlite3.Error:
            return {}

    def _get_historical_outcomes(self) -> List[Dict[str, Any]]:
        """Get historical application outcomes for modeling.

        Returns:
            List of completed application outcomes
        """
        try:
            self.cursor.execute(
                """
                SELECT
                    company,
                    role,
                    status,
                    domain_match,
                    tech_stack,
                    discovered_date,
                    applied_date,
                    offer_date
                FROM opportunities
                WHERE status IN ('Accepted', 'Rejected', 'Declined', 'Ghosted', 'Offer')
                ORDER BY discovered_date DESC
                """
            )
            return [dict(row) for row in self.cursor.fetchall()]
        except sqlite3.Error:
            return []

    def _get_outcome_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in application outcomes.

        Returns:
            Dictionary with outcome pattern analysis
        """
        try:
            self.cursor.execute(
                """
                SELECT
                    status,
                    COUNT(*) as count,
                    AVG(CASE
                        WHEN domain_match = 'Perfect' THEN 4
                        WHEN domain_match = 'Good' THEN 3
                        WHEN domain_match = 'Moderate' THEN 2
                        ELSE 1
                    END) as avg_match_score
                FROM opportunities
                WHERE status IN ('Accepted', 'Rejected', 'Offer')
                GROUP BY status
                """
            )
            patterns = {}
            for row in self.cursor.fetchall():
                patterns[row["status"]] = dict(row)
            return patterns
        except sqlite3.Error:
            return {}

    def _get_interview_history(self) -> List[Dict[str, Any]]:
        """Get complete interview question history.

        Returns:
            List of all interview questions
        """
        try:
            self.cursor.execute(
                """
                SELECT
                    iq.question_text,
                    iq.question_type,
                    iq.difficulty,
                    iq.my_rating,
                    iq.learned,
                    o.company,
                    o.role
                FROM interview_questions iq
                LEFT JOIN opportunities o ON iq.opportunity_id = o.id
                ORDER BY iq.created_at DESC
                """
            )
            return [dict(row) for row in self.cursor.fetchall()]
        except sqlite3.Error:
            return []

    def _get_company_history(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get application history grouped by company.

        Returns:
            Dictionary mapping companies to their application history
        """
        try:
            self.cursor.execute(
                """
                SELECT
                    company,
                    role,
                    status,
                    discovered_date,
                    applied_date
                FROM opportunities
                ORDER BY company, discovered_date DESC
                """
            )
            history: Dict[str, List[Dict[str, Any]]] = {}
            for row in self.cursor.fetchall():
                company = row["company"]
                if company not in history:
                    history[company] = []
                history[company].append(dict(row))
            return history
        except sqlite3.Error:
            return {}

    def validate_decision(
        self, decision_trace: ParliamentDecisionTrace
    ) -> Dict[str, Any]:
        """Validate a parliamentary decision against real-world outcomes.

        Args:
            decision_trace: The decision trace to validate

        Returns:
            Dictionary containing validation metrics

        Raises:
            ConnectionError: If not connected to database
        """
        if not self.connected:
            raise ConnectionError(
                "Not connected to jobs database. Call connect() first."
            )

        # This is a placeholder for future implementation
        # Would need to store decisions and match them with outcomes
        return {
            "outcome": None,
            "accuracy": None,
            "confidence_accuracy": None,
            "agent_accuracies": {},
            "note": "Validation requires historical decision tracking",
        }

    def calibrate_thresholds(
        self, agent_stats: Dict[str, Dict[str, Any]]
    ) -> Dict[str, float]:
        """Suggest threshold adjustments based on outcome data.

        Args:
            agent_stats: Statistics about agent activation patterns

        Returns:
            Dictionary mapping agent names to suggested thresholds

        Raises:
            ConnectionError: If not connected to database
        """
        if not self.connected:
            raise ConnectionError(
                "Not connected to jobs database. Call connect() first."
            )

        # This is a placeholder for future implementation
        # Would analyze accuracy rates and suggest adjustments
        return {
            "note": "Calibration requires historical accuracy tracking"
        }

    def get_supported_query_types(self) -> List[str]:
        """Get list of supported query types.

        Returns:
            List of supported query type strings
        """
        return [
            "job_evaluation",
            "interview_prep",
            "learning_priority",
            "skill_assessment",
        ]

    def get_supported_agents(self) -> List[str]:
        """Get list of agents that can be enriched.

        Returns:
            List of supported agent names
        """
        return ["krudi", "parva", "shanti", "rudi", "maya", "smriti"]

    # =========================================================================
    # DIRECTION 2: Decision Logging & Outcome Tracking
    # =========================================================================

    def log_parliament_decision(
        self,
        trace: ParliamentDecisionTrace,
        job_id: Optional[int] = None,
    ) -> int:
        """Log Parliament decision for future validation.

        This enables DIRECTION 2 (Training): Track Parliament advice and later
        validate against real outcomes to calibrate agent thresholds.

        Args:
            trace: ParliamentDecisionTrace containing decision details
            job_id: Optional job_id if decision relates to specific job

        Returns:
            log_id: Database ID for tracking this decision

        Raises:
            ConnectionError: If not connected to database
        """
        if not self.connected:
            raise ConnectionError(
                "Not connected to jobs database. Call connect() first."
            )

        # Generate decision_id if not present
        decision_id = getattr(trace, 'decision_id', None)
        if not decision_id:
            # Generate unique ID from timestamp and query hash
            decision_id = f"dec_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(trace.query) % 10000:04d}"

        # Collect active agents (those above 0.3 activation)
        active_agents = [
            name
            for name, act in trace.activations.items()
            if act.activation_strength >= 0.3
        ]

        # Get the final decision text
        decision_text = getattr(trace, 'decision', '')
        if not decision_text and hasattr(trace, 'agent_responses'):
            # Fallback: use Kshana's response if no final decision
            decision_text = trace.agent_responses.get('kshana', '')

        cursor = self.cursor
        cursor.execute(
            """
            INSERT INTO parliament_decisions
            (decision_id, timestamp, query, job_id, agents_active,
             decision_text, sparsity, confidence, dharmic_alignment,
             integration_used)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                decision_id,
                datetime.now().isoformat(),
                trace.query,
                job_id,
                json.dumps(active_agents),
                decision_text,
                trace.sparsity_ratio,
                trace.confidence,
                trace.dharmic_alignment,
                1,  # integration was used (since we're in JobsDBIntegration)
            ),
        )
        self.conn.commit()

        log_id = cursor.lastrowid
        return log_id

    def update_decision_outcome(
        self, log_id: int, outcome: Dict[str, Any]
    ) -> bool:
        """Update logged decision with real outcome.

        Call this after user has taken action on the Parliament's advice
        to track accuracy and enable calibration.

        Args:
            log_id: Database ID from log_parliament_decision()
            outcome: Dictionary with outcome data:
                {
                    'applied': bool,       # Did user apply?
                    'callback': bool,      # Got callback/response?
                    'interview': bool,     # Got interview?
                    'offer': bool,         # Got offer?
                    'notes': str          # Any additional notes
                }

        Returns:
            True if update successful, False otherwise

        Raises:
            ConnectionError: If not connected to database

        Example:
            >>> log_id = jobs_db.log_parliament_decision(trace, job_id=15)
            >>> # ... user applies to job ...
            >>> outcome = {
            >>>     'applied': True,
            >>>     'callback': True,
            >>>     'interview': True,
            >>>     'offer': False,
            >>>     'notes': 'Technical interview went well but no offer'
            >>> }
            >>> jobs_db.update_decision_outcome(log_id, outcome)
        """
        if not self.connected:
            raise ConnectionError(
                "Not connected to jobs database. Call connect() first."
            )

        cursor = self.cursor
        cursor.execute(
            """
            UPDATE parliament_decisions
            SET applied = ?, callback = ?, interview = ?,
                offer = ?, outcome_notes = ?, outcome_date = ?
            WHERE id = ?
        """,
            (
                outcome.get("applied", False),
                outcome.get("callback", False),
                outcome.get("interview", False),
                outcome.get("offer", False),
                outcome.get("notes", ""),
                datetime.now().isoformat(),
                log_id,
            ),
        )
        self.conn.commit()

        return cursor.rowcount > 0

    def get_decision_accuracy_stats(
        self, min_decisions: int = 10
    ) -> Dict[str, Any]:
        """Get accuracy statistics for logged decisions with outcomes.

        This enables analyzing how well Parliament predictions matched reality.

        Args:
            min_decisions: Minimum decisions needed per category for stats

        Returns:
            Dictionary with accuracy statistics:
            {
                'total_decisions': int,
                'decisions_with_outcomes': int,
                'overall_accuracy': float,  # % where prediction matched outcome
                'by_confidence': {
                    'high': {'count': int, 'accuracy': float},
                    'medium': {'count': int, 'accuracy': float},
                    'low': {'count': int, 'accuracy': float}
                },
                'by_agent': {
                    'krudi': {'activations': int, 'accurate': int, 'accuracy': float},
                    ...
                }
            }
        """
        if not self.connected:
            raise ConnectionError(
                "Not connected to jobs database. Call connect() first."
            )

        cursor = self.cursor

        # Get all decisions with outcomes
        cursor.execute(
            """
            SELECT id, agents_active, confidence, applied, callback, interview, offer
            FROM parliament_decisions
            WHERE outcome_date IS NOT NULL
        """
        )
        decisions = cursor.fetchall()

        if len(decisions) < min_decisions:
            return {
                "note": f"Need at least {min_decisions} decisions with outcomes. Currently have {len(decisions)}.",
                "total_decisions": len(decisions),
            }

        # Calculate statistics
        stats = {
            "total_decisions": len(decisions),
            "decisions_with_outcomes": len(decisions),
            "by_confidence": {
                "high": {"count": 0, "accurate": 0},
                "medium": {"count": 0, "accurate": 0},
                "low": {"count": 0, "accurate": 0},
            },
            "by_agent": {},
        }

        for decision in decisions:
            _, agents_json, confidence, applied, callback, interview, offer = (
                decision
            )

            # Categorize by confidence
            if confidence >= 0.7:
                conf_cat = "high"
            elif confidence >= 0.5:
                conf_cat = "medium"
            else:
                conf_cat = "low"

            stats["by_confidence"][conf_cat]["count"] += 1

            # Determine if prediction was accurate
            # (This is simplified - real implementation would need prediction storage)
            # For now, we consider high confidence + positive outcome = accurate
            positive_outcome = callback or interview or offer
            if (confidence >= 0.7 and positive_outcome) or (
                confidence < 0.5 and not positive_outcome
            ):
                stats["by_confidence"][conf_cat]["accurate"] += 1

            # Track by agent
            agents = json.loads(agents_json)
            for agent in agents:
                if agent not in stats["by_agent"]:
                    stats["by_agent"][agent] = {
                        "activations": 0,
                        "accurate": 0,
                    }
                stats["by_agent"][agent]["activations"] += 1
                if (confidence >= 0.7 and positive_outcome) or (
                    confidence < 0.5 and not positive_outcome
                ):
                    stats["by_agent"][agent]["accurate"] += 1

        # Calculate accuracy percentages
        for conf_cat in stats["by_confidence"]:
            count = stats["by_confidence"][conf_cat]["count"]
            if count > 0:
                accurate = stats["by_confidence"][conf_cat]["accurate"]
                stats["by_confidence"][conf_cat]["accuracy"] = (
                    accurate / count
                )

        for agent in stats["by_agent"]:
            activations = stats["by_agent"][agent]["activations"]
            if activations > 0:
                accurate = stats["by_agent"][agent]["accurate"]
                stats["by_agent"][agent]["accuracy"] = accurate / activations

        return stats

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
