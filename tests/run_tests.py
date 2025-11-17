"""Simple test runner for parliament tests (no pytest required)."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.parliament.kragentic_parliament import KragenticParliament


def test_parliament_initializes_with_7_agents():
    """Test that Parliament initializes with exactly 7 agents."""
    parliament = KragenticParliament()
    assert len(parliament.agents) == 7
    expected_agents = {"krudi", "parva", "shanti", "rudi", "kshana", "maya", "smriti"}
    assert set(parliament.agents.keys()) == expected_agents
    return "✓ Parliament initializes with 7 agents"


def test_deliberate_returns_decision_and_trace():
    """Test that deliberate() returns both decision and trace."""
    parliament = KragenticParliament()
    query = "Should we implement feature X?"
    result = parliament.deliberate(query)

    assert isinstance(result, tuple)
    assert len(result) == 2

    decision, trace = result
    assert isinstance(decision, str)
    assert len(decision) > 0
    assert hasattr(trace, 'decision_id')

    return "✓ deliberate() returns decision and trace"


def test_sparsity_is_in_valid_range():
    """Test that sparsity ratio is between 0.0 and 1.0."""
    parliament = KragenticParliament()
    query = "Should we implement feature X?"
    _, trace = parliament.deliberate(query)

    assert 0.0 <= trace.sparsity_ratio <= 1.0
    return f"✓ Sparsity in valid range: {trace.sparsity_ratio:.1%}"


def test_dharmic_alignment_in_valid_range():
    """Test that dharmic_alignment is between 0.0 and 1.0."""
    parliament = KragenticParliament()
    query = "Should we implement feature X?"
    _, trace = parliament.deliberate(query)

    assert isinstance(trace.dharmic_alignment, float)
    assert 0.0 <= trace.dharmic_alignment <= 1.0
    return f"✓ Dharmic alignment in range: {trace.dharmic_alignment:.1%}"


def test_agents_below_threshold_have_empty_response():
    """Test that agents below threshold don't fire circuits."""
    parliament = KragenticParliament()
    query = "X"
    _, trace = parliament.deliberate(query)

    passed = True
    for agent_name, activation in trace.activations.items():
        if agent_name == "kshana":
            continue

        threshold = parliament.agents[agent_name].activation_threshold
        if activation.activation_strength < threshold:
            if len(activation.circuits_fired) > 0:
                passed = False
                break

    assert passed
    return "✓ Agents below threshold have no circuits"


def test_lineage_path_extracted():
    """Test that lineage path is extracted."""
    parliament = KragenticParliament()
    query = "Should we implement feature X?"
    _, trace = parliament.deliberate(query)

    assert hasattr(trace, 'lineage_path')
    assert isinstance(trace.lineage_path, list)

    # Check format
    for item in trace.lineage_path:
        assert '.' in item
        agent, circuit = item.split('.')
        assert agent in parliament.agents

    return f"✓ Lineage extracted: {len(trace.lineage_path)} circuits"


def test_kshana_always_last():
    """Test that Kshana always activates last."""
    parliament = KragenticParliament()
    query = "Test query"
    _, trace = parliament.deliberate(query)

    assert trace.activation_sequence[-1] == "kshana"
    kshana_activation = trace.activations["kshana"]
    assert kshana_activation.activation_strength == 1.0

    return "✓ Kshana always activates last at 1.0"


def test_complete_deliberation_flow():
    """Test a complete deliberation produces all expected outputs."""
    parliament = KragenticParliament()
    query = "Should we build a decentralized governance system?"
    decision, trace = parliament.deliberate(query)

    # Verify all components
    assert isinstance(decision, str)
    assert len(decision) > 100

    assert trace.decision_id is not None
    assert trace.kshana_index == 1
    assert trace.query == query

    assert len(trace.activations) == 7
    assert 0.0 <= trace.sparsity_ratio <= 1.0
    assert 0.0 <= trace.confidence <= 1.0
    assert 0.0 <= trace.dharmic_alignment <= 1.0

    assert len(trace.activation_sequence) == 7
    assert trace.activation_sequence[-1] == "kshana"

    assert isinstance(trace.pattern_flags, list)
    assert isinstance(trace.lineage_path, list)
    assert len(trace.lineage_path) > 0

    assert len(parliament.decision_history) == 1

    return "✓ Complete deliberation flow works"


def run_all_tests():
    """Run all tests and report results."""
    print("=" * 70)
    print("SACRED QA AUDITS - PARLIAMENT TEST SUITE")
    print("=" * 70)

    tests = [
        ("Initialization", test_parliament_initializes_with_7_agents),
        ("Deliberation", test_deliberate_returns_decision_and_trace),
        ("Sparsity Calculation", test_sparsity_is_in_valid_range),
        ("Dharmic Alignment", test_dharmic_alignment_in_valid_range),
        ("Threshold Behavior", test_agents_below_threshold_have_empty_response),
        ("Lineage Extraction", test_lineage_path_extracted),
        ("Kshana Always Last", test_kshana_always_last),
        ("Integration", test_complete_deliberation_flow),
    ]

    passed = 0
    failed = 0

    for i, (name, test_func) in enumerate(tests, 1):
        try:
            result = test_func()
            print(f"\n{i}. {name}")
            print(f"   {result}")
            passed += 1
        except AssertionError as e:
            print(f"\n{i}. {name}")
            print(f"   ✗ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"\n{i}. {name}")
            print(f"   ✗ ERROR: {e}")
            failed += 1

    print("\n" + "=" * 70)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)

    return passed, failed


if __name__ == "__main__":
    passed, failed = run_all_tests()
    sys.exit(0 if failed == 0 else 1)
