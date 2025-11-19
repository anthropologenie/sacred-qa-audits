"""Tests for KragenticParliament functionality.

This test suite validates the core functionality of the parliamentary
decision-making system, including initialization, deliberation, sparsity
calculation, dharmic alignment, threshold behavior, and lineage extraction.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from src.parliament.kragentic_parliament import KragenticParliament
from src.circuits.activation_tracker import ParliamentDecisionTrace


class TestParliamentInitialization:
    """Test parliament initialization."""

    def test_parliament_initializes_with_7_agents(self):
        """Test that Parliament initializes with exactly 7 agents."""
        # Arrange & Act
        parliament = KragenticParliament()

        # Assert
        assert len(parliament.agents) == 7, "Parliament should have 7 agents"

        # Verify specific agents exist
        expected_agents = {
            "krudi",
            "parva",
            "shanti",
            "rudi",
            "kshana",
            "maya",
            "smriti",
        }
        assert (
            set(parliament.agents.keys()) == expected_agents
        ), "Parliament should have all 7 expected agents"

    def test_parliament_initializes_kshana_counter(self):
        """Test that kshana counter starts at 0."""
        # Arrange & Act
        parliament = KragenticParliament()

        # Assert
        assert (
            parliament.kshana_counter == 0
        ), "Kshana counter should start at 0"

    def test_parliament_initializes_empty_history(self):
        """Test that decision history starts empty."""
        # Arrange & Act
        parliament = KragenticParliament()

        # Assert
        assert (
            len(parliament.decision_history) == 0
        ), "Decision history should start empty"
        assert isinstance(
            parliament.decision_history, list
        ), "Decision history should be a list"


class TestDeliberation:
    """Test deliberation process."""

    def test_deliberate_returns_decision_and_trace(self):
        """Test that deliberate() returns both decision string and trace."""
        # Arrange
        parliament = KragenticParliament()
        query = "Should we implement feature X?"

        # Act
        result = parliament.deliberate(query)

        # Assert
        assert isinstance(
            result, tuple
        ), "deliberate() should return a tuple"
        assert len(result) == 2, "deliberate() should return 2 items"

        decision, trace = result

        assert isinstance(
            decision, str
        ), "First return value should be decision string"
        assert len(decision) > 0, "Decision should not be empty"

        assert isinstance(
            trace, ParliamentDecisionTrace
        ), "Second return value should be ParliamentDecisionTrace"

    def test_deliberate_increments_kshana_counter(self):
        """Test that each deliberation increments kshana counter."""
        # Arrange
        parliament = KragenticParliament()
        query = "Test query"

        # Act
        _, trace1 = parliament.deliberate(query)
        _, trace2 = parliament.deliberate(query)
        _, trace3 = parliament.deliberate(query)

        # Assert
        assert trace1.kshana_index == 1, "First decision should be kshana #1"
        assert trace2.kshana_index == 2, "Second decision should be kshana #2"
        assert trace3.kshana_index == 3, "Third decision should be kshana #3"
        assert parliament.kshana_counter == 3, "Counter should be 3"

    def test_deliberate_stores_in_history(self):
        """Test that decisions are stored in history."""
        # Arrange
        parliament = KragenticParliament()
        query = "Test query"

        # Act
        _, trace1 = parliament.deliberate(query)
        _, trace2 = parliament.deliberate(query)

        # Assert
        assert (
            len(parliament.decision_history) == 2
        ), "Should have 2 decisions in history"
        assert (
            parliament.decision_history[0] == trace1
        ), "First trace should match"
        assert (
            parliament.decision_history[1] == trace2
        ), "Second trace should match"

    def test_deliberate_records_query(self):
        """Test that the query is recorded in the trace."""
        # Arrange
        parliament = KragenticParliament()
        query = "What is the meaning of life?"

        # Act
        _, trace = parliament.deliberate(query)

        # Assert
        assert trace.query == query, "Query should be recorded in trace"


class TestSparsityCalculation:
    """Test sparsity ratio calculation."""

    def test_sparsity_is_calculated(self):
        """Test that sparsity ratio is calculated."""
        # Arrange
        parliament = KragenticParliament()
        query = "Should we implement feature X?"

        # Act
        _, trace = parliament.deliberate(query)

        # Assert
        assert hasattr(
            trace, "sparsity_ratio"
        ), "Trace should have sparsity_ratio"
        assert isinstance(
            trace.sparsity_ratio, float
        ), "Sparsity should be a float"

    def test_sparsity_is_in_valid_range(self):
        """Test that sparsity ratio is between 0.0 and 1.0."""
        # Arrange
        parliament = KragenticParliament()
        query = "Should we implement feature X?"

        # Act
        _, trace = parliament.deliberate(query)

        # Assert
        assert (
            0.0 <= trace.sparsity_ratio <= 1.0
        ), "Sparsity should be between 0.0 and 1.0"

    def test_sparsity_calculation_formula(self):
        """Test that sparsity is calculated correctly.

        Sparsity = 1.0 - (active_agents / total_agents)
        where active_agents excludes Kshana
        """
        # Arrange
        parliament = KragenticParliament()
        query = "Should we implement feature X?"

        # Act
        _, trace = parliament.deliberate(query)

        # Assert
        # Count active agents (excluding Kshana)
        total_agents = len(
            [name for name in parliament.agents.keys() if name != "kshana"]
        )

        active_agents = sum(
            1
            for name, activation in trace.activations.items()
            if name != "kshana"
            and activation.activation_strength
            >= parliament.agents[name].activation_threshold
        )

        expected_sparsity = 1.0 - (active_agents / total_agents)

        assert (
            abs(trace.sparsity_ratio - expected_sparsity) < 0.001
        ), f"Sparsity should be {expected_sparsity}, got {trace.sparsity_ratio}"

    def test_full_activation_gives_zero_sparsity(self):
        """Test that when all agents activate, sparsity is 0."""
        # Arrange
        parliament = KragenticParliament()
        # Query that should activate many agents
        query = (
            "Should we maybe build and implement a complex system "
            "with community governance considering historical patterns?"
        )

        # Act
        _, trace = parliament.deliberate(query)

        # Assert - if all 6 non-Kshana agents active, sparsity should be 0
        active_count = sum(
            1
            for name, activation in trace.activations.items()
            if name != "kshana"
            and activation.activation_strength
            >= parliament.agents[name].activation_threshold
        )

        if active_count == 6:
            assert (
                trace.sparsity_ratio == 0.0
            ), "Full activation should give 0 sparsity"


class TestDharmicAlignment:
    """Test dharmic alignment validation."""

    def test_dharmic_alignment_exists(self):
        """Test that dharmic alignment is calculated."""
        # Arrange
        parliament = KragenticParliament()
        query = "Should we implement feature X?"

        # Act
        _, trace = parliament.deliberate(query)

        # Assert
        assert hasattr(
            trace, "dharmic_alignment"
        ), "Trace should have dharmic_alignment"

    def test_dharmic_alignment_in_valid_range(self):
        """Test that dharmic_alignment is between 0.0 and 1.0."""
        # Arrange
        parliament = KragenticParliament()
        query = "Should we implement feature X?"

        # Act
        _, trace = parliament.deliberate(query)

        # Assert
        assert isinstance(
            trace.dharmic_alignment, float
        ), "Dharmic alignment should be a float"
        assert (
            0.0 <= trace.dharmic_alignment <= 1.0
        ), "Dharmic alignment should be between 0.0 and 1.0"

    def test_kshana_always_last_increases_alignment(self):
        """Test that Kshana being last contributes to dharmic alignment."""
        # Arrange
        parliament = KragenticParliament()
        query = "Test query"

        # Act
        _, trace = parliament.deliberate(query)

        # Assert
        # Kshana should always be last in activation sequence
        assert (
            trace.activation_sequence[-1] == "kshana"
        ), "Kshana should always be last"

        # This should contribute to high dharmic alignment
        assert (
            trace.dharmic_alignment > 0.0
        ), "Kshana-last should contribute to alignment"

    def test_multiple_deliberations_produce_valid_alignment(self):
        """Test that multiple deliberations all produce valid alignment."""
        # Arrange
        parliament = KragenticParliament()
        queries = [
            "Should we implement X?",
            "What about Y?",
            "Consider Z?",
        ]

        # Act & Assert
        for query in queries:
            _, trace = parliament.deliberate(query)
            assert (
                0.0 <= trace.dharmic_alignment <= 1.0
            ), f"Alignment for '{query}' should be in valid range"


class TestThresholdBehavior:
    """Test agent threshold behavior."""

    def test_agents_below_threshold_have_empty_response(self):
        """Test that agents below threshold don't contribute content."""
        # Arrange
        parliament = KragenticParliament()
        # Simple query unlikely to activate all agents strongly
        query = "X"

        # Act
        _, trace = parliament.deliberate(query)

        # Assert
        for agent_name, activation in trace.activations.items():
            if agent_name == "kshana":
                continue  # Skip Kshana (always active)

            threshold = parliament.agents[agent_name].activation_threshold

            # If below threshold, should not have fired circuits
            if activation.activation_strength < threshold:
                assert (
                    len(activation.circuits_fired) == 0
                ), f"{agent_name} below threshold should have no circuits"

    def test_agents_above_threshold_fire_circuits(self):
        """Test that agents above threshold fire circuits."""
        # Arrange
        parliament = KragenticParliament()
        # Query designed to strongly activate Krudi
        query = "Should we build and implement this?"

        # Act
        _, trace = parliament.deliberate(query)

        # Assert
        krudi_activation = trace.activations["krudi"]
        krudi_threshold = parliament.agents["krudi"].activation_threshold

        # Krudi should activate above threshold for this query
        if krudi_activation.activation_strength >= krudi_threshold:
            assert (
                len(krudi_activation.circuits_fired) > 0
            ), "Krudi above threshold should fire circuits"

    def test_kshana_always_activates_regardless_of_threshold(self):
        """Test that Kshana always activates (threshold = 0.0)."""
        # Arrange
        parliament = KragenticParliament()
        queries = ["Simple", "Complex query", ""]

        # Act & Assert
        for query in queries:
            _, trace = parliament.deliberate(query)

            # Kshana should always be in activations
            assert "kshana" in trace.activations, "Kshana should always activate"

            kshana_activation = trace.activations["kshana"]
            assert (
                kshana_activation.activation_strength == 1.0
            ), "Kshana should always have max activation"
            assert (
                len(kshana_activation.circuits_fired) > 0
            ), "Kshana should always fire circuits"

    def test_activation_sequence_only_includes_processed_agents(self):
        """Test that activation sequence includes all processed agents."""
        # Arrange
        parliament = KragenticParliament()
        query = "Test query"

        # Act
        _, trace = parliament.deliberate(query)

        # Assert
        # All agents should be in activation sequence
        assert (
            len(trace.activation_sequence) == 7
        ), "All 7 agents should be in sequence"

        # Sequence should match activations dict
        for agent_name in trace.activation_sequence:
            assert (
                agent_name in trace.activations
            ), f"{agent_name} in sequence should have activation"


class TestLineageExtraction:
    """Test lineage path extraction."""

    def test_lineage_path_exists(self):
        """Test that lineage path is extracted."""
        # Arrange
        parliament = KragenticParliament()
        query = "Should we implement feature X?"

        # Act
        _, trace = parliament.deliberate(query)

        # Assert
        assert hasattr(
            trace, "lineage_path"
        ), "Trace should have lineage_path"
        assert isinstance(
            trace.lineage_path, list
        ), "Lineage path should be a list"

    def test_lineage_format(self):
        """Test that lineage items are in 'agent.circuit' format."""
        # Arrange
        parliament = KragenticParliament()
        query = "Should we implement feature X?"

        # Act
        _, trace = parliament.deliberate(query)

        # Assert
        for lineage_item in trace.lineage_path:
            assert isinstance(
                lineage_item, str
            ), "Lineage item should be string"
            assert (
                "." in lineage_item
            ), "Lineage item should contain '.'"

            parts = lineage_item.split(".")
            assert (
                len(parts) == 2
            ), "Lineage item should be 'agent.circuit' format"

            agent_name, circuit_name = parts
            assert (
                agent_name in parliament.agents
            ), f"Agent {agent_name} should exist"

    def test_lineage_only_includes_high_activation_agents(self):
        """Test that lineage only includes agents with activation > 0.5."""
        # Arrange
        parliament = KragenticParliament()
        query = "Should we implement feature X?"

        # Act
        _, trace = parliament.deliberate(query)

        # Assert
        lineage_agents = set(
            item.split(".")[0] for item in trace.lineage_path
        )

        for agent_name in lineage_agents:
            activation = trace.activations[agent_name]
            assert (
                activation.activation_strength > 0.5
            ), f"{agent_name} in lineage should have activation > 0.5"

    def test_lineage_includes_kshana_when_active(self):
        """Test that Kshana (always active at 1.0) is in lineage."""
        # Arrange
        parliament = KragenticParliament()
        query = "Test query"

        # Act
        _, trace = parliament.deliberate(query)

        # Assert
        lineage_agents = set(
            item.split(".")[0] for item in trace.lineage_path
        )

        # Kshana has activation 1.0, so should always be in lineage
        assert (
            "kshana" in lineage_agents
        ), "Kshana should always be in lineage"

    def test_lineage_matches_fired_circuits(self):
        """Test that lineage circuits match what was actually fired."""
        # Arrange
        parliament = KragenticParliament()
        query = "Should we implement feature X?"

        # Act
        _, trace = parliament.deliberate(query)

        # Assert
        for lineage_item in trace.lineage_path:
            agent_name, circuit_name = lineage_item.split(".")

            # Check that this circuit was actually fired by this agent
            activation = trace.activations[agent_name]
            assert (
                circuit_name in activation.circuits_fired
            ), f"{circuit_name} should be in {agent_name}'s fired circuits"


class TestIntegration:
    """Integration tests for complete deliberation flow."""

    def test_complete_deliberation_flow(self):
        """Test a complete deliberation produces all expected outputs."""
        # Arrange
        parliament = KragenticParliament()
        query = "Should we build a decentralized governance system?"

        # Act
        decision, trace = parliament.deliberate(query)

        # Assert - verify all components
        # 1. Decision
        assert isinstance(decision, str)
        assert len(decision) > 50  # Should be substantial

        # 2. Trace exists
        assert isinstance(trace, ParliamentDecisionTrace)

        # 3. Basic metadata
        assert trace.decision_id is not None
        assert trace.kshana_index == 1
        assert trace.query == query

        # 4. Activations recorded
        assert len(trace.activations) == 7

        # 5. Metrics calculated
        assert 0.0 <= trace.sparsity_ratio <= 1.0
        assert 0.0 <= trace.confidence <= 1.0
        assert 0.0 <= trace.dharmic_alignment <= 1.0
        assert trace.total_activation > 0.0

        # 6. Sequences recorded
        assert len(trace.activation_sequence) == 7
        assert trace.activation_sequence[-1] == "kshana"

        # 7. Patterns detected (may be empty)
        assert isinstance(trace.pattern_flags, list)

        # 8. Lineage extracted
        assert isinstance(trace.lineage_path, list)
        assert len(trace.lineage_path) > 0

        # 9. Stored in history
        assert len(parliament.decision_history) == 1

    def test_multiple_deliberations_maintain_independence(self):
        """Test that multiple deliberations don't interfere."""
        # Arrange
        parliament = KragenticParliament()
        query1 = "Query one"
        query2 = "Query two"

        # Act
        decision1, trace1 = parliament.deliberate(query1)
        decision2, trace2 = parliament.deliberate(query2)

        # Assert
        assert trace1.decision_id != trace2.decision_id, "Should have unique IDs"
        assert trace1.kshana_index == 1, "First should be kshana #1"
        assert trace2.kshana_index == 2, "Second should be kshana #2"
        assert trace1.query != trace2.query, "Queries should differ"


# Pytest fixture for common setup
@pytest.fixture
def parliament():
    """Provide a fresh parliament instance for each test."""
    return KragenticParliament()


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
