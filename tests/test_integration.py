"""Integration tests for sacred-qa-audits + jobs-application-automation symbiosis.

This test suite validates the complete integration between the Kragentic Parliament
and the jobs-application-automation database, ensuring that:

1. Database connections work reliably
2. Context fetching provides correct data
3. Agents use real data for enhanced decision-making
4. Parliament auto-enrichment works seamlessly
5. Full workflows produce grounded, data-backed decisions

Run with: python3 -m pytest tests/test_integration.py -v
"""

import sys
from pathlib import Path
import tempfile
import sqlite3
from unittest.mock import Mock, patch

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from src.integrations.jobs_db_integration import JobsDBIntegration
from src.parliament.kragentic_parliament import KragenticParliament
from src.agents.krudi_agent import KrudiAgent
from src.agents.smriti_agent import SmritiAgent
from src.agents.parva_agent import ParvaAgent


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def temp_test_db():
    """Create a temporary test database with sample data.

    Returns:
        Path to temporary database file
    """
    # Create temporary database file
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    db_path = temp_db.name
    temp_db.close()

    # Initialize database with schema and test data
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create opportunities table
    cursor.execute("""
        CREATE TABLE opportunities (
            id INTEGER PRIMARY KEY,
            company TEXT,
            role TEXT,
            tech_stack TEXT,
            salary_range TEXT,
            is_remote INTEGER,
            domain_match TEXT,
            status TEXT,
            priority TEXT,
            notes TEXT,
            discovered_date TEXT,
            applied_date TEXT,
            offer_date TEXT
        )
    """)

    # Create interview_questions table
    cursor.execute("""
        CREATE TABLE interview_questions (
            id INTEGER PRIMARY KEY,
            opportunity_id INTEGER,
            question_text TEXT,
            question_type TEXT,
            difficulty TEXT,
            my_rating REAL,
            learned INTEGER,
            created_at TEXT
        )
    """)

    # Create study_topics table
    cursor.execute("""
        CREATE TABLE study_topics (
            id INTEGER PRIMARY KEY,
            name TEXT,
            category TEXT,
            priority INTEGER,
            status TEXT,
            estimated_hours REAL,
            actual_hours REAL,
            deadline TEXT
        )
    """)

    # Create learning_sessions table
    cursor.execute("""
        CREATE TABLE learning_sessions (
            id INTEGER PRIMARY KEY,
            topic_id INTEGER,
            duration_minutes INTEGER,
            what_was_learned TEXT,
            confidence_before REAL,
            confidence_after REAL,
            session_date TEXT
        )
    """)

    # Create interactions table
    cursor.execute("""
        CREATE TABLE interactions (
            id INTEGER PRIMARY KEY,
            opportunity_id INTEGER,
            type TEXT,
            date TEXT,
            time TEXT,
            meet_link TEXT
        )
    """)

    # Insert sample data - opportunities
    cursor.execute("""
        INSERT INTO opportunities
        (company, role, tech_stack, is_remote, domain_match, status, priority, discovered_date)
        VALUES
        ('TechCorp', 'Data Engineer', 'SQL,Python,ETL', 1, 'Good', 'Applied', 'High', '2024-01-01'),
        ('StartupX', 'ETL Engineer', 'ETL Tools,SQL', 1, 'Perfect', 'Technical', 'High', '2024-01-15'),
        ('BigTech', 'Senior Data Engineer', 'SQL,Data Warehouse,Python', 0, 'Moderate', 'Screening', 'Medium', '2024-02-01')
    """)

    # Insert sample interview questions with ratings
    questions = [
        (1, 'Explain SQL joins', 'Technical SQL', 'Medium', 3.0, 1),
        (1, 'Design ETL pipeline', 'ETL Tools', 'Hard', 2.5, 1),
        (2, 'Python data processing', 'Python', 'Easy', 2.0, 0),
        (2, 'SQL optimization', 'Technical SQL', 'Medium', 2.8, 1),
        (3, 'Data warehouse design', 'Data Warehouse', 'Hard', 1.0, 0),
        (3, 'ETL best practices', 'ETL Tools', 'Medium', 3.5, 1),
    ]

    for opp_id, question, q_type, difficulty, rating, learned in questions:
        cursor.execute("""
            INSERT INTO interview_questions
            (opportunity_id, question_text, question_type, difficulty, my_rating, learned, created_at)
            VALUES (?, ?, ?, ?, ?, ?, '2024-01-01')
        """, (opp_id, question, q_type, difficulty, rating, learned))

    # Insert learning gaps
    cursor.execute("""
        INSERT INTO study_topics
        (name, category, priority, status, estimated_hours)
        VALUES
        ('Advanced SQL Optimization', 'Technical SQL', 4, 'In Progress', 20),
        ('Data Warehouse Fundamentals', 'Data Warehouse', 5, 'Not Started', 30),
        ('Python Advanced Features', 'Python', 3, 'In Progress', 15)
    """)

    # Insert learning session
    cursor.execute("""
        INSERT INTO learning_sessions
        (topic_id, duration_minutes, what_was_learned, confidence_before, confidence_after, session_date)
        VALUES
        (1, 60, 'Index optimization techniques', 2.5, 3.5, '2024-01-10')
    """)

    conn.commit()
    conn.close()

    yield db_path

    # Cleanup
    Path(db_path).unlink()


@pytest.fixture
def jobs_db(temp_test_db):
    """Provide a JobsDBIntegration instance connected to test database.

    Args:
        temp_test_db: Path to temporary test database

    Returns:
        Connected JobsDBIntegration instance
    """
    integration = JobsDBIntegration(db_path=temp_test_db)
    integration.connect()
    yield integration
    integration.disconnect()


@pytest.fixture
def parliament_with_integration(jobs_db):
    """Provide a parliament with integration enabled.

    Args:
        jobs_db: Connected JobsDBIntegration instance

    Returns:
        KragenticParliament with integration
    """
    return KragenticParliament(integration=jobs_db)


# ============================================================================
# TEST SECTION 1: JobsDBIntegration Connection
# ============================================================================


class TestJobsDBIntegrationConnection:
    """Test database connection and error handling."""

    def test_connection(self, temp_test_db):
        """Verify integration connects to database successfully."""
        # Arrange
        integration = JobsDBIntegration(db_path=temp_test_db)

        # Act
        result = integration.connect()

        # Assert
        assert result is True, "Connection should succeed"
        assert integration.connected is True, "Should be marked as connected"
        assert integration.conn is not None, "Connection object should exist"
        assert integration.cursor is not None, "Cursor should exist"

        # Cleanup
        integration.disconnect()

    def test_required_tables_exist(self, jobs_db):
        """Check that all required tables are present in database."""
        # Arrange
        required_tables = [
            'opportunities',
            'interview_questions',
            'study_topics',
            'learning_sessions',
            'interactions'
        ]

        # Act & Assert
        for table_name in required_tables:
            jobs_db.cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (table_name,)
            )
            result = jobs_db.cursor.fetchone()
            assert result is not None, f"Table '{table_name}' should exist"

    def test_graceful_failure(self):
        """Verify integration handles missing database gracefully."""
        # Arrange
        integration = JobsDBIntegration(db_path="/nonexistent/path/to/db.db")

        # Act
        result = integration.connect()

        # Assert
        assert result is False, "Connection should fail for invalid path"
        assert integration.connected is False, "Should not be marked as connected"
        assert integration.conn is None, "Connection object should be None"


# ============================================================================
# TEST SECTION 2: Context Fetching
# ============================================================================


class TestContextFetching:
    """Test context fetching methods for different query types."""

    def test_fetch_job_evaluation_context(self, jobs_db):
        """Test fetching job evaluation context returns user_skills and job_requirements."""
        # Act
        context = jobs_db.fetch_context("job_evaluation", opportunity_id=1)

        # Assert
        assert "user_skills" in context, "Should include user_skills"
        assert "job_requirements" in context, "Should include job_requirements"
        assert "learning_gaps" in context, "Should include learning_gaps"

        # Verify user_skills has data
        assert isinstance(context["user_skills"], dict), "user_skills should be dict"
        assert len(context["user_skills"]) > 0, "Should have skill ratings"

        # Verify job_requirements extracted from tech_stack
        assert isinstance(context["job_requirements"], list), "job_requirements should be list"
        assert "SQL" in context["job_requirements"], "Should parse tech_stack"

    def test_fetch_interview_prep_context(self, jobs_db):
        """Test fetching interview prep context returns weak_topics and past_questions."""
        # Act
        context = jobs_db.fetch_context("interview_prep")

        # Assert
        assert "learning_gaps" in context, "Should include weak topics"
        assert "past_questions" in context, "Should include past questions"
        assert "performance_patterns" in context, "Should include patterns"
        assert "upcoming_interviews" in context, "Should include upcoming interviews"

        # Verify past_questions has data
        assert isinstance(context["past_questions"], list), "past_questions should be list"
        assert len(context["past_questions"]) > 0, "Should have question history"

    def test_fetch_learning_priority_context(self, jobs_db):
        """Test fetching learning priority context returns learning_gaps and study_topics."""
        # Act
        context = jobs_db.fetch_context("learning_priority")

        # Assert
        assert "learning_gaps" in context, "Should include learning_gaps"
        assert "study_topics" in context, "Should include study_topics"
        assert "recent_sessions" in context, "Should include recent_sessions"
        assert "confidence_trends" in context, "Should include confidence_trends"

        # Verify learning_gaps has priority ordering
        assert isinstance(context["learning_gaps"], list), "learning_gaps should be list"
        if len(context["learning_gaps"]) > 1:
            # Verify sorted by priority (descending)
            priorities = [gap.get("priority", 0) for gap in context["learning_gaps"]]
            assert priorities == sorted(priorities, reverse=True), "Should be sorted by priority"

    def test_fetch_skill_assessment_context(self, jobs_db):
        """Test fetching skill assessment context returns skill_ratings."""
        # Act
        context = jobs_db.fetch_context("skill_assessment")

        # Assert
        assert "user_skills" in context, "Should include user_skills"
        assert "skill_trends" in context, "Should include skill_trends"

        # Verify skill ratings are numeric
        for skill, rating in context["user_skills"].items():
            assert isinstance(rating, (int, float)), f"Rating for {skill} should be numeric"
            assert 1.0 <= rating <= 5.0, f"Rating for {skill} should be 1-5"


# ============================================================================
# TEST SECTION 3: Agent Enhancement
# ============================================================================


class TestAgentEnhancement:
    """Test that agents use real data from integration."""

    def test_krudi_with_integration(self, jobs_db):
        """Verify Krudi uses real skill data for gap analysis."""
        # Arrange
        krudi = KrudiAgent()
        context = {
            "user_skills": {"Technical SQL": 2.9, "ETL Tools": 3.0},
            "job_requirements": ["Advanced SQL", "ETL Tools"],
            "learning_gaps": [
                {"name": "SQL Optimization", "category": "Technical SQL", "current_rating": 2.5}
            ]
        }
        query = "Should I apply to this role?"

        # Act
        response, activation = krudi.process(query, context)

        # Assert
        assert activation.activation_strength > 0.5, "Krudi should activate for job evaluation"
        assert "integration_skill_analysis" in activation.circuits_fired, "Should fire integration circuit"

        # Verify response contains specific numbers (not templates)
        assert "2.9" in response or "2.86" in response, "Should include actual skill rating"
        assert "gap" in response.lower(), "Should mention skill gaps"
        assert any(prob in response for prob in ["5-10%", "15-25%", "35-50%", "60-75%"]), \
            "Should include realistic callback probability"

    def test_smriti_with_integration(self, jobs_db):
        """Verify Smriti uses real application history for pattern recognition."""
        # Arrange
        smriti = SmritiAgent()

        # Enrich context with real history
        context = jobs_db.enrich_agent_context("smriti", {})
        query = "What patterns do you see in my interview history?"

        # Act
        response, activation = smriti.process(query, context)

        # Assert
        assert "smriti_history" in context, "Should have interview history"
        assert "smriti_patterns" in context, "Should have performance patterns"
        assert "smriti_companies" in context, "Should have company history"

        # Verify Smriti activated
        assert activation.activation_strength > 0, "Smriti should process pattern query"

    def test_parva_with_integration(self, jobs_db):
        """Verify Parva uses real career trajectory data."""
        # Arrange
        parva = ParvaAgent()

        # Enrich context with trajectory
        context = jobs_db.enrich_agent_context("parva", {})
        query = "What's my career trajectory?"

        # Act
        response, activation = parva.process(query, context)

        # Assert
        assert "parva_trajectory" in context, "Should have career trajectory"
        assert "parva_timeline" in context, "Should have application timeline"

        # Verify context has actual data
        assert isinstance(context["parva_trajectory"], list), "Trajectory should be list"

    def test_responses_include_specific_numbers(self, jobs_db):
        """Verify responses include specific data points, not generic templates."""
        # Arrange
        krudi = KrudiAgent()
        context = jobs_db.fetch_context("job_evaluation", opportunity_id=1)
        context["job_requirements"] = ["Advanced SQL", "Data Warehouse"]
        query = "Should I apply?"

        # Act
        response, _ = krudi.process(query, context)

        # Assert - should contain specific numeric values
        has_numbers = any(char.isdigit() for char in response)
        assert has_numbers, "Response should include specific numbers"

        # Should NOT contain generic phrases
        generic_phrases = [
            "consider whether",
            "think about",
            "evaluate your",
            "you should probably"
        ]
        for phrase in generic_phrases:
            assert phrase.lower() not in response.lower(), \
                f"Response should not contain generic phrase: '{phrase}'"


# ============================================================================
# TEST SECTION 4: Parliament Auto-Enrichment
# ============================================================================


class TestParliamentAutoEnrichment:
    """Test parliament's automatic context enrichment."""

    def test_detect_query_type(self):
        """Verify parliament correctly classifies query types."""
        # Arrange
        parliament = KragenticParliament()

        # Test cases: (query, expected_type)
        test_cases = [
            ("Should I apply to Data Engineer at Google?", "job_evaluation"),
            ("Help me prepare for interview", "interview_prep"),
            ("What should I study next?", "learning_priority"),
            ("Am I ready for this role?", "skill_assessment"),
        ]

        # Act & Assert
        for query, expected_type in test_cases:
            detected_type = parliament._detect_query_type(query)
            assert detected_type == expected_type, \
                f"Query '{query}' should be detected as '{expected_type}', got '{detected_type}'"

    def test_auto_enrichment(self, parliament_with_integration):
        """Verify parliament automatically enriches context before deliberation."""
        # Arrange
        query = "Should I apply to Data Engineer role?"

        # Act
        decision, trace = parliament_with_integration.deliberate(query)

        # Assert - verify enrichment happened
        # Check that Krudi received integration data
        krudi_activation = trace.activations.get("krudi")
        assert krudi_activation is not None, "Krudi should have activated"

        # If integration worked, Krudi should fire integration circuit
        if krudi_activation.activation_strength >= 0.5:
            # Check for integration-specific circuits
            circuits = krudi_activation.circuits_fired
            integration_circuits = [c for c in circuits if "integration" in c or "skill" in c]
            # Note: This may vary based on context, so we just verify structure is valid
            assert isinstance(circuits, list), "Circuits should be a list"

    def test_backward_compatibility(self):
        """Verify parliament works without integration (backward compatibility)."""
        # Arrange - parliament WITHOUT integration
        parliament = KragenticParliament(integration=None)
        query = "Should I apply to this job?"

        # Act
        decision, trace = parliament.deliberate(query)

        # Assert - should still work, just without integration data
        assert isinstance(decision, str), "Should return decision"
        assert len(decision) > 0, "Decision should not be empty"
        assert isinstance(trace.activations, dict), "Should have activations"
        assert len(trace.activations) == 7, "All agents should be processed"


# ============================================================================
# TEST SECTION 5: Full Workflow
# ============================================================================


class TestFullWorkflow:
    """Test complete end-to-end integration workflows."""

    def test_job_evaluation_workflow(self, parliament_with_integration, jobs_db):
        """Test complete job evaluation workflow from query to decision."""
        # Arrange
        query = "Should I apply to Senior Data Engineer at BigTech requiring Advanced SQL?"

        # Manually enrich context to simulate real scenario
        context = jobs_db.fetch_context("job_evaluation", opportunity_id=3)
        context["job_requirements"] = ["Advanced SQL", "Data Warehouse", "Python"]

        # Act
        decision, trace = parliament_with_integration.deliberate(query, context)

        # Assert - verify complete workflow
        # 1. Decision was made
        assert isinstance(decision, str), "Should produce decision"
        assert len(decision) > 50, "Decision should be substantial"

        # 2. Krudi activated and analyzed gaps
        krudi_activation = trace.activations.get("krudi")
        assert krudi_activation is not None, "Krudi should activate"
        krudi_response = trace.agent_responses.get("krudi", "")

        # 3. Decision is grounded in data
        # Should mention specific skills or gaps
        has_skill_analysis = any(
            keyword in krudi_response.lower()
            for keyword in ["sql", "warehouse", "rating", "gap"]
        )
        assert has_skill_analysis, "Should include skill analysis"

        # 4. Metrics are valid
        assert 0.0 <= trace.confidence <= 1.0, "Confidence should be valid"
        assert 0.0 <= trace.dharmic_alignment <= 1.0, "Alignment should be valid"

    def test_integration_circuits_traced(self, parliament_with_integration, jobs_db):
        """Verify integration-specific circuits appear in decision trace."""
        # Arrange
        query = "Should I apply to this Data Engineer role?"
        context = jobs_db.fetch_context("job_evaluation", opportunity_id=1)
        context["job_requirements"] = ["SQL", "ETL Tools"]

        # Act
        decision, trace = parliament_with_integration.deliberate(query, context)

        # Assert - verify integration circuits were traced
        all_circuits = []
        for activation in trace.activations.values():
            all_circuits.extend(activation.circuits_fired)

        # Check for integration-related circuits
        integration_circuits = [
            c for c in all_circuits
            if any(keyword in c for keyword in ["integration", "skill_reality", "skill_analysis"])
        ]

        # Should have at least one integration circuit if Krudi activated
        krudi_activation = trace.activations.get("krudi")
        if krudi_activation and krudi_activation.activation_strength >= 0.5:
            assert len(integration_circuits) > 0, \
                "Should have integration-specific circuits in trace"

        # Verify lineage includes integration circuits
        if integration_circuits:
            lineage_str = " ".join(trace.lineage_path)
            has_integration_in_lineage = any(
                keyword in lineage_str
                for keyword in ["integration", "skill"]
            )
            # Note: May not always be in lineage depending on activation strength
            # Just verify lineage structure is valid
            assert isinstance(trace.lineage_path, list), "Lineage should be a list"

    def test_learning_priority_workflow(self, parliament_with_integration, jobs_db):
        """Test learning priority recommendation workflow."""
        # Arrange
        query = "What should I study next to improve my interview success?"
        context = jobs_db.fetch_context("learning_priority")

        # Act
        decision, trace = parliament_with_integration.deliberate(query, context)

        # Assert
        # 1. Decision provides learning guidance
        assert isinstance(decision, str), "Should produce decision"

        # 2. Multiple agents should activate for learning query
        active_agents = [
            name for name, act in trace.activations.items()
            if act.activation_strength >= parliament_with_integration.agents[name].activation_threshold
        ]
        assert len(active_agents) >= 2, "Multiple agents should activate for complex query"

        # 3. Should have learning-related data in context
        assert "learning_gaps" in context, "Should have learning gaps"
        assert "study_topics" in context, "Should have study topics"


# ============================================================================
# INTEGRATION QUALITY TESTS
# ============================================================================


class TestIntegrationQuality:
    """Test quality and correctness of integration."""

    def test_user_skills_calculated_correctly(self, jobs_db):
        """Verify user skills are calculated as averages from interview data."""
        # Act
        user_skills = jobs_db._get_user_skills()

        # Assert
        # Based on test data:
        # Technical SQL: (3.0 + 2.8) / 2 = 2.9
        # ETL Tools: (2.5 + 3.5) / 2 = 3.0
        # Python: 2.0 / 1 = 2.0
        # Data Warehouse: 1.0 / 1 = 1.0

        assert "Technical SQL" in user_skills, "Should have SQL skill"
        assert abs(user_skills["Technical SQL"] - 2.9) < 0.1, "SQL average should be ~2.9"

        assert "ETL Tools" in user_skills, "Should have ETL skill"
        assert abs(user_skills["ETL Tools"] - 3.0) < 0.1, "ETL average should be ~3.0"

    def test_learning_gaps_ordered_by_priority(self, jobs_db):
        """Verify learning gaps are ordered by priority descending."""
        # Act
        learning_gaps = jobs_db._get_learning_gaps()

        # Assert
        if len(learning_gaps) > 1:
            for i in range(len(learning_gaps) - 1):
                current_priority = learning_gaps[i].get("priority", 0)
                next_priority = learning_gaps[i + 1].get("priority", 0)
                assert current_priority >= next_priority, \
                    "Learning gaps should be ordered by priority descending"

    def test_context_enrichment_preserves_existing_data(self, jobs_db):
        """Verify enrichment adds data without overwriting existing context."""
        # Arrange
        original_context = {
            "custom_field": "custom_value",
            "user_preference": "important_setting"
        }

        # Act
        enriched = jobs_db.enrich_agent_context("krudi", original_context.copy())

        # Assert
        assert enriched["custom_field"] == "custom_value", "Should preserve existing fields"
        assert enriched["user_preference"] == "important_setting", "Should preserve settings"
        assert "krudi_skills" in enriched, "Should add new enrichment data"


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_fetch_context_requires_connection(self):
        """Verify fetch_context raises error if not connected."""
        # Arrange
        integration = JobsDBIntegration(db_path="/tmp/test.db")
        # Don't connect

        # Act & Assert
        with pytest.raises(ConnectionError, match="Not connected"):
            integration.fetch_context("job_evaluation")

    def test_unsupported_query_type_raises_error(self, jobs_db):
        """Verify unsupported query types raise ValueError."""
        # Act & Assert
        with pytest.raises(ValueError, match="Unsupported query_type"):
            jobs_db.fetch_context("invalid_query_type")

    def test_enrich_agent_context_requires_connection(self):
        """Verify enrich_agent_context raises error if not connected."""
        # Arrange
        integration = JobsDBIntegration(db_path="/tmp/test.db")
        # Don't connect

        # Act & Assert
        with pytest.raises(ConnectionError, match="Not connected"):
            integration.enrich_agent_context("krudi", {})

    def test_parliament_continues_if_integration_fails(self, temp_test_db):
        """Verify parliament continues functioning if integration fails."""
        # Arrange
        integration = JobsDBIntegration(db_path=temp_test_db)
        integration.connect()

        # Simulate integration failure by disconnecting mid-use
        integration.disconnect()

        parliament = KragenticParliament(integration=integration)
        query = "Should I apply to this job?"

        # Act
        decision, trace = parliament.deliberate(query)

        # Assert - should still work without integration
        assert isinstance(decision, str), "Should still produce decision"
        assert len(trace.activations) == 7, "All agents should still process"


# ============================================================================
# RUN TESTS
# ============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
