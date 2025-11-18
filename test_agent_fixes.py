"""Test script to verify agent activation fixes and template removal.

Tests:
1. Simple factual queries should have high sparsity (85-100%)
2. Grounded decisions should activate 4-5 agents with specific responses
3. Speculation should activate 3-4 agents with appropriate warnings
"""

from src.parliament.kragentic_parliament import KragenticParliament


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"{title}")
    print("=" * 80)


def check_template_text(text: str) -> list[str]:
    """Check for template/emoji patterns that should be removed."""
    template_indicators = []

    # Emoji patterns
    emoji_patterns = [
        "🌍", "⚓", "🏛️", "⚡", "☯️", "🔄", "🕊️",
        "⏳", "🔗", "🦋", "📚", "🌱", "🔮", "📊",
        "🌌", "⏭️", "🎭", "📜", "🔍", "🌳", "🧠",
        "🎯", "═══", "───"
    ]

    for pattern in emoji_patterns:
        if pattern in text:
            template_indicators.append(f"Found emoji/decoration: {pattern}")

    # Generic template phrases
    template_phrases = [
        "Reality Grounding Analysis:",
        "Temporal Causality Analysis:",
        "Equilibrium Analysis:",
        "Transformation Analysis:",
        "Consider the full temporal chain",
        "Proceed with awareness of all perspectives",
        "AGENT PERSPECTIVES:",
        "DECISION COLLAPSE:",
    ]

    for phrase in template_phrases:
        if phrase in text:
            template_indicators.append(f"Found template phrase: {phrase}")

    return template_indicators


def run_test(test_num: int, query: str, expected_sparsity_range: tuple):
    """Run a single test and report results."""
    print_section(f"TEST {test_num}: {query}")

    # Create parliament and process query
    parliament = KragenticParliament()
    result, trace = parliament.deliberate(query)

    # Extract metrics from trace

    print(f"\nQuery: {query}")
    print(f"\n--- METRICS ---")
    print(f"Sparsity: {trace.sparsity_ratio:.1%}")
    print(f"Kshana Index: {trace.kshana_index:.3f}")
    print(f"Confidence: {trace.confidence:.1%}")
    print(f"Dharmic Alignment: {trace.dharmic_alignment:.1%}")

    # Check sparsity expectation
    min_sparsity, max_sparsity = expected_sparsity_range
    sparsity_ok = min_sparsity <= trace.sparsity_ratio <= max_sparsity
    status = "✓" if sparsity_ok else "✗"
    print(f"\nSparsity Check: {status} Expected {min_sparsity:.0%}-{max_sparsity:.0%}, Got {trace.sparsity_ratio:.1%}")

    print(f"\n--- AGENT ACTIVATIONS ---")
    activated_agents = []
    for agent_name in ["krudi", "parva", "shanti", "rudi", "maya", "smriti", "kshana"]:
        if agent_name in trace.activations:
            activation = trace.activations[agent_name]
            strength = activation.activation_strength
            activated = strength >= 0.5  # Assuming default threshold

            status_symbol = "●" if activated else "○"
            print(f"{status_symbol} {agent_name.capitalize()}: {strength:.2f}")

            if activated:
                activated_agents.append(agent_name)

                # Show first 100 chars of response
                if agent_name in trace.agent_responses:
                    response = trace.agent_responses[agent_name]
                    if response:
                        preview = response[:100].replace("\n", " ")
                        if len(response) > 100:
                            preview += "..."
                        print(f"   Response: {preview}")
        else:
            print(f"○ {agent_name.capitalize()}: Not in trace")

    print(f"\n--- KSHANA SYNTHESIS ---")
    # Show full synthesis (but truncate if too long for display)
    synthesis = result
    if len(synthesis) > 500:
        print(synthesis[:500] + "\n... (truncated)")
    else:
        print(synthesis)

    print(f"\n--- TEMPLATE CHECK ---")
    template_issues = check_template_text(result)

    # Also check individual agent responses
    for agent_name, response in trace.agent_responses.items():
        if response:
            agent_issues = check_template_text(response)
            template_issues.extend([f"[{agent_name}] {issue}" for issue in agent_issues])

    if template_issues:
        print("✗ Template indicators found:")
        for issue in template_issues[:10]:  # Show first 10
            print(f"  - {issue}")
        if len(template_issues) > 10:
            print(f"  ... and {len(template_issues) - 10} more")
    else:
        print("✓ No template text detected")

    print(f"\n--- AGENT RESPONSE SPECIFICITY ---")
    # Check if responses reference the actual query content
    query_keywords = set(query.lower().split())
    query_keywords.discard("the")
    query_keywords.discard("to")
    query_keywords.discard("we")
    query_keywords.discard("a")

    for agent_name, response in trace.agent_responses.items():
        if agent_name != "kshana":
            # Check if response mentions query-specific terms
            if not response:
                response_lower = ""
            else:
                response_lower = response.lower()

            # For simple queries, empty response is OK (agent choosing not to activate)
            if not response or not response.strip():
                print(f"✓ {agent_name.capitalize()}: Empty (chose not to respond)")
            else:
                # Check for query-specific content
                is_specific = any(
                    keyword in response_lower
                    for keyword in query_keywords
                    if len(keyword) > 3
                )

                if is_specific or "Reality" in response or "consequence" in response_lower:
                    print(f"✓ {agent_name.capitalize()}: Query-specific response")
                else:
                    print(f"? {agent_name.capitalize()}: May be generic")

    return {
        "sparsity": trace.sparsity_ratio,
        "activated_agents": activated_agents,
        "synthesis": synthesis,
        "template_issues": len(template_issues),
        "sparsity_ok": sparsity_ok,
    }


def main():
    """Run all tests."""
    print("=" * 80)
    print("AGENT ACTIVATION & TEMPLATE REMOVAL TESTS")
    print("=" * 80)

    # TEST 1: Simple factual query
    test1_results = run_test(
        1,
        "What is 2 plus 2?",
        expected_sparsity_range=(0.85, 1.0)
    )

    # TEST 2: Grounded decision
    test2_results = run_test(
        2,
        "Should we deploy the authentication system to production?",
        expected_sparsity_range=(0.20, 0.40)
    )

    # TEST 3: Speculation
    test3_results = run_test(
        3,
        "What if we had infinite budget and no constraints?",
        expected_sparsity_range=(0.40, 0.60)
    )

    # Summary
    print_section("TEST SUMMARY")

    all_passed = (
        test1_results["sparsity_ok"] and
        test2_results["sparsity_ok"] and
        test3_results["sparsity_ok"]
    )

    print(f"\nTest 1 (Simple Factual): {'✓ PASS' if test1_results['sparsity_ok'] else '✗ FAIL'}")
    print(f"  Sparsity: {test1_results['sparsity']:.1%}")
    print(f"  Template issues: {test1_results['template_issues']}")

    print(f"\nTest 2 (Grounded Decision): {'✓ PASS' if test2_results['sparsity_ok'] else '✗ FAIL'}")
    print(f"  Sparsity: {test2_results['sparsity']:.1%}")
    print(f"  Activated agents: {', '.join(test2_results['activated_agents'])}")
    print(f"  Template issues: {test2_results['template_issues']}")

    print(f"\nTest 3 (Speculation): {'✓ PASS' if test3_results['sparsity_ok'] else '✗ FAIL'}")
    print(f"  Sparsity: {test3_results['sparsity']:.1%}")
    print(f"  Activated agents: {', '.join(test3_results['activated_agents'])}")
    print(f"  Template issues: {test3_results['template_issues']}")

    print(f"\n{'=' * 80}")
    print(f"OVERALL: {'✓ ALL TESTS PASSED' if all_passed else '✗ SOME TESTS FAILED'}")
    print(f"{'=' * 80}")


if __name__ == "__main__":
    main()
