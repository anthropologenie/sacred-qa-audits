"""End-to-end integration tests for Sacred QA Audits ↔ Jobs Application Automation.

This test suite validates the complete symbiotic workflow:
1. Parliament queries real job data
2. Agents provide grounded advice
3. Decisions are logged and tracked
4. Outcomes validate predictions
5. Accuracy improves over time
"""

import json
import pytest
import sqlite3
import time
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from src.integrations.jobs_db_integration import JobsDBIntegration
from src.integrations.validation import ParliamentValidator
from src.parliament.kragentic_parliament import KragenticParliament
from src.circuits.activation_tracker import ParliamentDecisionTrace


class TestFullIntegration:
    """End-to-end integration test suite."""

    @pytest.fixture
    def mock_db_integration(self, tmp_path):
        """Create a mock database integration with test data."""
        # Create temporary database
        db_path = tmp_path / "test_jobs.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Create tables
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

        cursor.execute("""
            CREATE TABLE study_topics (
                id INTEGER PRIMARY KEY,
                name TEXT,
                category TEXT,
                priority INTEGER,
                status TEXT,
                estimated_hours INTEGER,
                actual_hours INTEGER,
                deadline TEXT
            )
        """)

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

        cursor.execute("""
            CREATE TABLE scraped_jobs (
                id INTEGER PRIMARY KEY,
                company TEXT,
                job_title TEXT,
                match_score REAL,
                job_url TEXT,
                tags TEXT,
                description TEXT,
                classification TEXT,
                scraped_at TEXT,
                location TEXT,
                salary_range TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE parliament_decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                decision_id TEXT UNIQUE NOT NULL,
                timestamp TEXT NOT NULL,
                query TEXT NOT NULL,
                job_id INTEGER,
                agents_active TEXT,
                decision_text TEXT,
                sparsity REAL,
                confidence REAL,
                dharmic_alignment REAL,
                integration_used INTEGER DEFAULT 0,
                applied INTEGER DEFAULT 0,
                callback INTEGER DEFAULT 0,
                interview INTEGER DEFAULT 0,
                offer INTEGER DEFAULT 0,
                outcome_notes TEXT,
                outcome_date TEXT,
                FOREIGN KEY (job_id) REFERENCES scraped_jobs(id)
            )
        """)

        # Insert test data
        cursor.execute("""
            INSERT INTO opportunities (id, company, role, tech_stack, status, domain_match, is_remote, priority, discovered_date)
            VALUES (1, 'TechCorp', 'Senior Python Engineer', 'Python,FastAPI,PostgreSQL', 'Discovered', 'Good', 1, 'High', '2024-11-01')
        """)

        cursor.execute("""
            INSERT INTO scraped_jobs (id, company, job_title, match_score, tags, description, classification, scraped_at)
            VALUES (1, 'TechCorp', 'Senior Python Engineer', 92.0, 'Python,FastAPI,PostgreSQL,Docker',
                    'Looking for experienced Python developer', 'new', '2024-11-18')
        """)

        # Insert skill data (interview questions)
        skills = [
            ('Python', 3.8, 'Medium'),
            ('Python', 4.0, 'Hard'),
            ('Python', 3.5, 'Easy'),
            ('SQL', 2.0, 'Medium'),
            ('SQL', 2.2, 'Hard'),
            ('Docker', 4.0, 'Easy'),
            ('FastAPI', 3.5, 'Medium')
        ]

        for skill_type, rating, difficulty in skills:
            cursor.execute("""
                INSERT INTO interview_questions (opportunity_id, question_type, my_rating, difficulty, learned, created_at)
                VALUES (1, ?, ?, ?, 1, '2024-11-01')
            """, (skill_type, rating, difficulty))

        # Insert study topics
        cursor.execute("""
            INSERT INTO study_topics (name, category, priority, status, estimated_hours)
            VALUES ('PostgreSQL Basics', 'SQL', 5, 'In Progress', 20)
        """)

        cursor.execute("""
            INSERT INTO study_topics (name, category, priority, status, estimated_hours)
            VALUES ('Advanced FastAPI', 'Python', 4, 'In Progress', 15)
        """)

        # Insert learning session
        cursor.execute("""
            INSERT INTO learning_sessions (topic_id, duration_minutes, confidence_before, confidence_after, session_date)
            VALUES (2, 90, 3.0, 3.8, '2024-11-15')
        """)

        conn.commit()
        conn.close()

        # Create integration
        integration = JobsDBIntegration(db_path=str(db_path))
        integration.connect()

        yield integration

        # Cleanup
        integration.disconnect()

    def test_complete_job_advisory_flow(self, mock_db_integration):
        """Test the complete workflow: query → advice → logging → verification."""
        # Initialize Parliament with integration
        parliament = KragenticParliament(integration=mock_db_integration)

        # Get context for specific job
        context = mock_db_integration.fetch_context("job_evaluation", opportunity_id=1)

        # Enrich with agent-specific data
        for agent_name in ["krudi", "smriti", "parva", "rudi", "maya", "shanti"]:
            agent_context = mock_db_integration.enrich_agent_context(agent_name, context)
            context.update(agent_context)

        # Ask Parliament
        query = "Should I apply to Senior Python Engineer at TechCorp?"
        decision, trace = parliament.deliberate(query, context)

        # Verify decision was made
        assert decision is not None
        assert len(decision) > 0
        assert isinstance(trace, ParliamentDecisionTrace)

        # Verify trace has activations
        assert len(trace.activations) > 0
        assert 'kshana' in trace.activations  # Kshana always active

        # Verify confidence is sensible
        assert 0.0 <= trace.confidence <= 1.0
        assert 0.0 <= trace.sparsity_ratio <= 1.0
        assert 0.0 <= trace.dharmic_alignment <= 1.0

        # Log decision
        log_id = mock_db_integration.log_parliament_decision(trace, job_id=1)
        assert log_id > 0

        # Verify decision was logged
        cursor = mock_db_integration.cursor
        cursor.execute("""
            SELECT decision_id, timestamp, query, job_id, integration_used
            FROM parliament_decisions WHERE id = ?
        """, (log_id,))
        row = cursor.fetchone()

        assert row is not None
        assert row[2] == query  # query field
        assert row[3] == 1  # job_id field
        assert row[4] == 1  # integration_used field

        # Verify integration circuits in trace
        assert hasattr(trace, 'query')
        assert trace.query == query

    def test_all_7_agents_with_integration(self, mock_db_integration):
        """Test that all 7 agents use integration data, no generic templates."""
        parliament = KragenticParliament(integration=mock_db_integration)

        # Get comprehensive context
        context = mock_db_integration.fetch_context("job_evaluation", opportunity_id=1)

        for agent_name in ["krudi", "smriti", "parva", "rudi", "maya", "shanti"]:
            agent_context = mock_db_integration.enrich_agent_context(agent_name, context)
            context.update(agent_context)

        # Complex query that should activate all agents
        query = """Should I apply to the Senior Python Engineer role at TechCorp?
        Consider my skill levels, learning trajectory, past patterns, work-life balance,
        and potential for growth. What are the probable outcomes?"""

        decision, trace = parliament.deliberate(query, context)

        # Verify all 7 agents are present in trace
        expected_agents = {'krudi', 'smriti', 'parva', 'rudi', 'maya', 'shanti', 'kshana'}
        assert set(trace.activations.keys()) == expected_agents

        # Check agent responses for specific data references
        specific_indicators = {
            'krudi': ['3.8', 'Python', 'rating', 'skill'],  # Should mention skill ratings
            'smriti': ['TechCorp', 'interview', 'question', 'history'],  # Should mention history
            'parva': ['trajectory', 'application', 'pattern'],  # Should mention trajectory
            'rudi': ['learning', 'FastAPI', 'study', 'growth'],  # Should mention learning
            'maya': ['outcome', 'similar', 'probability'],  # Should mention scenarios
            'shanti': ['remote', 'balance', 'preference'],  # Should mention preferences
        }

        for agent_name, indicators in specific_indicators.items():
            response = trace.agent_responses.get(agent_name, '').lower()

            # At least one indicator should be present (indicates data-grounded response)
            has_specific_data = any(indicator.lower() in response for indicator in indicators)

            # Should not be empty
            assert len(response) > 50, f"{agent_name} response too short: {response}"

            # For high-activation agents, verify they mention specific data
            activation = trace.activations[agent_name].activation_strength
            if activation >= 0.5:
                assert has_specific_data, (
                    f"{agent_name} activated strongly ({activation:.2f}) but "
                    f"didn't mention specific data. Response: {response[:200]}"
                )

    def test_decision_logging_and_retrieval(self, mock_db_integration):
        """Test logging decisions and updating outcomes."""
        parliament = KragenticParliament(integration=mock_db_integration)

        # Create a simple decision trace (mock)
        trace = Mock(spec=ParliamentDecisionTrace)
        trace.query = "Should I apply to test role?"
        trace.confidence = 0.85
        trace.sparsity_ratio = 0.57
        trace.dharmic_alignment = 0.82
        trace.activations = {
            'krudi': Mock(activation_strength=0.75),
            'parva': Mock(activation_strength=0.65),
            'kshana': Mock(activation_strength=1.0)
        }
        trace.agent_responses = {
            'kshana': 'Test decision response'
        }
        trace.decision = 'Test decision response'

        # Log decision
        log_id = mock_db_integration.log_parliament_decision(trace, job_id=1)
        assert log_id > 0

        # Update with outcome
        outcome = {
            'applied': True,
            'callback': True,
            'interview': True,
            'offer': False,
            'notes': 'Made it to final round'
        }
        success = mock_db_integration.update_decision_outcome(log_id, outcome)
        assert success is True

        # Query back and verify
        cursor = mock_db_integration.cursor
        cursor.execute("SELECT * FROM parliament_decisions WHERE id = ?", (log_id,))
        row = cursor.fetchone()

        assert row is not None
        assert row[11] == 1  # applied
        assert row[12] == 1  # callback
        assert row[13] == 1  # interview
        assert row[14] == 0  # offer
        assert row[15] == 'Made it to final round'  # outcome_notes
        assert row[16] is not None  # outcome_date

    def test_accuracy_calculation(self, mock_db_integration):
        """Test accuracy metrics calculation with mock decisions."""
        parliament = KragenticParliament(integration=mock_db_integration)

        # Create multiple mock decisions with outcomes
        decisions = [
            # High confidence, positive outcome → accurate
            {'confidence': 0.85, 'applied': 1, 'callback': 1, 'interview': 1, 'offer': 1},
            # High confidence, positive outcome → accurate
            {'confidence': 0.80, 'applied': 1, 'callback': 1, 'interview': 1, 'offer': 0},
            # Low confidence, negative outcome → accurate
            {'confidence': 0.30, 'applied': 0, 'callback': 0, 'interview': 0, 'offer': 0},
            # High confidence, negative outcome → inaccurate
            {'confidence': 0.90, 'applied': 1, 'callback': 0, 'interview': 0, 'offer': 0},
            # Medium confidence, medium outcome → moderate
            {'confidence': 0.60, 'applied': 1, 'callback': 1, 'interview': 0, 'offer': 0},
        ]

        # Insert mock decisions
        cursor = mock_db_integration.cursor
        for i, dec in enumerate(decisions):
            cursor.execute("""
                INSERT INTO parliament_decisions
                (decision_id, timestamp, query, confidence, agents_active, integration_used,
                 applied, callback, interview, offer, outcome_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                f"test_dec_{i}",
                datetime.now().isoformat(),
                f"Test query {i}",
                dec['confidence'],
                json.dumps(['krudi', 'parva']),
                1,
                dec['applied'],
                dec['callback'],
                dec['interview'],
                dec['offer'],
                datetime.now().isoformat()
            ))
        mock_db_integration.conn.commit()

        # Calculate accuracy metrics
        validator = ParliamentValidator(mock_db_integration)
        metrics = validator.calculate_accuracy_metrics()

        # Verify metrics structure
        assert 'total_decisions' in metrics
        assert 'decisions_with_outcomes' in metrics
        assert 'accuracy' in metrics
        assert 'by_confidence' in metrics
        assert 'by_agent' in metrics

        # Verify values are sensible
        assert metrics['decisions_with_outcomes'] == 5
        assert 0.0 <= metrics['accuracy']['overall_accuracy'] <= 1.0
        assert 0.0 <= metrics['accuracy']['callback_prediction'] <= 1.0

        # Verify by confidence breakdown
        for level in ['high', 'medium', 'low']:
            assert level in metrics['by_confidence']
            if metrics['by_confidence'][level]['count'] > 0:
                assert 0.0 <= metrics['by_confidence'][level]['accuracy'] <= 1.0

    def test_graceful_degradation(self, mock_db_integration):
        """Test Parliament still works when integration disconnects."""
        # Create Parliament with integration
        parliament = KragenticParliament(integration=mock_db_integration)

        # First, verify it works with integration
        context = mock_db_integration.fetch_context("job_evaluation", opportunity_id=1)
        query = "Should I apply to this role?"
        decision1, trace1 = parliament.deliberate(query, context)

        assert decision1 is not None
        assert len(trace1.activations) > 0

        # Disconnect integration
        mock_db_integration.disconnect()

        # Parliament should still work without integration (no context)
        decision2, trace2 = parliament.deliberate(query, {})

        # Verify it didn't crash
        assert decision2 is not None
        assert len(trace2.activations) > 0

        # Kshana should always work
        assert 'kshana' in trace2.activations

    def test_performance(self, mock_db_integration):
        """Test performance of integration queries."""
        parliament = KragenticParliament(integration=mock_db_integration)

        # Measure time for 10 deliberations
        start_time = time.time()
        num_deliberations = 10

        for i in range(num_deliberations):
            context = mock_db_integration.fetch_context("job_evaluation", opportunity_id=1)

            # Enrich with agent data
            for agent_name in ["krudi", "smriti", "parva"]:
                agent_context = mock_db_integration.enrich_agent_context(agent_name, context)
                context.update(agent_context)

            query = f"Should I apply to role {i}?"
            decision, trace = parliament.deliberate(query, context)

            assert decision is not None

        end_time = time.time()
        elapsed = end_time - start_time
        avg_time = elapsed / num_deliberations

        # Verify performance
        assert elapsed < 20.0, f"10 deliberations took {elapsed:.2f}s (should be < 20s)"
        assert avg_time < 2.0, f"Average deliberation took {avg_time:.2f}s (should be < 2s)"

        print(f"\nPerformance: {num_deliberations} deliberations in {elapsed:.2f}s "
              f"(avg: {avg_time:.2f}s per deliberation)")

    def test_data_consistency(self, mock_db_integration):
        """Test data consistency and referential integrity."""
        cursor = mock_db_integration.cursor

        # Verify tables exist
        cursor.execute("""
            SELECT name FROM sqlite_master WHERE type='table'
        """)
        tables = {row[0] for row in cursor.fetchall()}

        expected_tables = {
            'opportunities', 'interview_questions', 'study_topics',
            'learning_sessions', 'interactions', 'scraped_jobs',
            'parliament_decisions'
        }
        assert expected_tables.issubset(tables), f"Missing tables: {expected_tables - tables}"

        # Verify foreign key constraints for parliament_decisions
        cursor.execute("""
            SELECT job_id FROM parliament_decisions WHERE job_id IS NOT NULL
        """)
        decision_job_ids = {row[0] for row in cursor.fetchall()}

        cursor.execute("SELECT id FROM scraped_jobs")
        scraped_job_ids = {row[0] for row in cursor.fetchall()}

        # All job_ids in decisions should exist in scraped_jobs
        invalid_refs = decision_job_ids - scraped_job_ids
        assert len(invalid_refs) == 0, f"Invalid job_id references: {invalid_refs}"

        # Verify skill data consistency
        cursor.execute("""
            SELECT question_type, AVG(my_rating) as avg_rating
            FROM interview_questions
            WHERE my_rating IS NOT NULL
            GROUP BY question_type
        """)
        skill_ratings = cursor.fetchall()

        for skill_type, avg_rating in skill_ratings:
            # Ratings should be in valid range
            assert 1.0 <= avg_rating <= 5.0, f"{skill_type} has invalid rating: {avg_rating}"

        # Verify no NULL required fields in parliament_decisions
        cursor.execute("""
            SELECT id FROM parliament_decisions
            WHERE decision_id IS NULL OR timestamp IS NULL OR query IS NULL
        """)
        invalid_decisions = cursor.fetchall()
        assert len(invalid_decisions) == 0, "Found decisions with NULL required fields"

    def test_validation_integration_accuracy(self, mock_db_integration):
        """Test ParliamentValidator integration and accuracy reporting."""
        # Insert test decisions with known outcomes
        cursor = mock_db_integration.cursor

        test_cases = [
            # Perfect predictions
            {'conf': 0.90, 'applied': 1, 'cb': 1, 'iv': 1, 'of': 1, 'agents': ['krudi', 'parva']},
            {'conf': 0.85, 'applied': 1, 'cb': 1, 'iv': 1, 'of': 0, 'agents': ['krudi', 'parva']},
            {'conf': 0.20, 'applied': 0, 'cb': 0, 'iv': 0, 'of': 0, 'agents': ['krudi']},
            # Imperfect predictions
            {'conf': 0.80, 'applied': 1, 'cb': 0, 'iv': 0, 'of': 0, 'agents': ['krudi', 'maya']},
            {'conf': 0.30, 'applied': 1, 'cb': 1, 'iv': 0, 'of': 0, 'agents': ['parva']},
        ]

        for i, case in enumerate(test_cases):
            cursor.execute("""
                INSERT INTO parliament_decisions
                (decision_id, timestamp, query, confidence, agents_active, integration_used,
                 applied, callback, interview, offer, outcome_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                f"val_test_{i}",
                datetime.now().isoformat(),
                f"Validation test {i}",
                case['conf'],
                json.dumps(case['agents']),
                1,
                case['applied'],
                case['cb'],
                case['iv'],
                case['of'],
                datetime.now().isoformat()
            ))
        mock_db_integration.conn.commit()

        # Test validator
        validator = ParliamentValidator(mock_db_integration)

        # Test accuracy metrics
        metrics = validator.calculate_accuracy_metrics()
        assert metrics['decisions_with_outcomes'] >= 5
        assert 'accuracy' in metrics
        assert 'overall_accuracy' in metrics['accuracy']

        # Test report generation
        report = validator.generate_accuracy_report()
        assert 'PARLIAMENT ACCURACY REPORT' in report
        assert 'Overall Accuracy' in report
        assert 'BY RECOMMENDATION TYPE' in report

        # Test threshold suggestions
        adjustments = validator.suggest_threshold_adjustments()

        # Should have suggestions for agents that appeared
        assert 'krudi' in adjustments or 'note' in adjustments
        assert 'parva' in adjustments or 'note' in adjustments

        # Adjustments should be in valid range
        for agent, adjustment in adjustments.items():
            if agent != 'note':
                assert -0.15 <= adjustment <= 0.15, (
                    f"{agent} adjustment {adjustment} out of range"
                )


class TestIntegrationEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_database(self, tmp_path):
        """Test integration with empty database."""
        db_path = tmp_path / "empty.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Create tables but no data
        cursor.execute("""
            CREATE TABLE opportunities (
                id INTEGER PRIMARY KEY,
                company TEXT,
                role TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE interview_questions (
                id INTEGER PRIMARY KEY,
                question_type TEXT,
                my_rating REAL
            )
        """)
        cursor.execute("""
            CREATE TABLE parliament_decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                decision_id TEXT,
                timestamp TEXT,
                query TEXT
            )
        """)
        conn.commit()
        conn.close()

        integration = JobsDBIntegration(db_path=str(db_path))
        integration.connect()

        # Should handle empty database gracefully
        context = integration.fetch_context("job_evaluation")

        assert context is not None
        assert isinstance(context, dict)
        assert context.get('user_skills', {}) == {}
        assert context.get('learning_gaps', []) == []

        integration.disconnect()

    def test_invalid_db_path(self):
        """Test handling of invalid database path."""
        integration = JobsDBIntegration(db_path="/nonexistent/path/to/db.db")

        # Should fail to connect
        result = integration.connect()
        assert result is False
        assert integration.connected is False

    def test_malformed_json_in_agents_active(self, tmp_path):
        """Test handling of malformed JSON in agents_active field."""
        db_path = tmp_path / "malformed.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE parliament_decisions (
                id INTEGER PRIMARY KEY,
                decision_id TEXT,
                timestamp TEXT,
                query TEXT,
                agents_active TEXT,
                confidence REAL,
                outcome_date TEXT,
                applied INTEGER,
                callback INTEGER,
                interview INTEGER,
                offer INTEGER
            )
        """)

        # Insert decision with malformed JSON
        cursor.execute("""
            INSERT INTO parliament_decisions
            (decision_id, timestamp, query, agents_active, confidence, outcome_date,
             applied, callback, interview, offer)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'malformed_test',
            datetime.now().isoformat(),
            'Test query',
            'NOT VALID JSON',  # Malformed JSON
            0.75,
            datetime.now().isoformat(),
            1, 1, 0, 0
        ))
        conn.commit()
        conn.close()

        integration = JobsDBIntegration(db_path=str(db_path))
        integration.connect()

        # Should handle malformed JSON gracefully
        validator = ParliamentValidator(integration)
        metrics = validator.calculate_accuracy_metrics()

        # Should still complete without crashing
        assert 'decisions_with_outcomes' in metrics
        assert metrics['decisions_with_outcomes'] == 1

        integration.disconnect()


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=src/integrations', '--cov-report=term-missing'])
