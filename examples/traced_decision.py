"""Traced Decision Example - Demonstrating KragenticParliament in action.

This example shows how the Kragentic Parliament deliberates on a query,
activates multiple agents, and produces a traced decision with full
diagnostic information.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.parliament.kragentic_parliament import KragenticParliament


def print_section(title: str, char: str = "=") -> None:
    """Print a formatted section header."""
    print(f"\n{char * 70}")
    print(f"{title:^70}")
    print(f"{char * 70}\n")


def print_subsection(title: str) -> None:
    """Print a formatted subsection header."""
    print(f"\n{title}")
    print("-" * len(title))


def format_activation_strength(strength: float, threshold: float) -> str:
    """Format activation strength with visual indicator."""
    bar_length = int(strength * 20)
    bar = "█" * bar_length + "░" * (20 - bar_length)
    status = "✓ ACTIVE" if strength >= threshold else "○ passive"
    return f"{bar} {strength:.3f} {status}"


def main() -> None:
    """Run the traced decision example."""
    print_section("🏛️  KRAGENTIC PARLIAMENT - TRACED DECISION EXAMPLE")

    # Step 1: Initialize parliament
    print("Initializing Kragentic Parliament...")
    parliament = KragenticParliament()
    print(f"✓ Parliament initialized with {len(parliament.agents)} agents")
    print(f"  Agents: {', '.join(parliament.agents.keys())}")

    # Step 2: Prepare query
    query = "Should KrecoCloud implement decentralized governance?"
    print(f"\n📋 Query: \"{query}\"")

    # Step 3: Run deliberation
    print_subsection("🔄 Deliberating...")
    decision, trace = parliament.deliberate(query)

    # Step 4: Print decision
    print_section("🎯 FINAL DECISION", "=")
    print(decision)

    # Step 5: Print detailed trace information
    print_section("📊 DECISION TRACE ANALYSIS", "=")

    # Trace metadata
    print_subsection("Metadata")
    print(f"  Decision ID:     {trace.decision_id}")
    print(f"  Kshana Index:    #{trace.kshana_index}")
    print(f"  Query:           {trace.query}")

    # Activation metrics
    print_subsection("⚡ Activation Metrics")
    print(f"  Total Activation:    {trace.total_activation:.3f}")
    print(f"  Sparsity Ratio:      {trace.sparsity_ratio:.1%}")
    print(f"  Confidence:          {trace.confidence:.1%}")
    print(f"  Dharmic Alignment:   {trace.dharmic_alignment:.1%}")

    # Sparsity interpretation
    if trace.sparsity_ratio < 0.3:
        print(f"  └─ Interpretation: Low sparsity - many agents engaged")
    elif trace.sparsity_ratio > 0.7:
        print(f"  └─ Interpretation: High sparsity - few agents engaged")
    else:
        print(f"  └─ Interpretation: Balanced agent engagement")

    # Active agents breakdown
    print_subsection("🤖 Agent Activations")
    print(f"  {'Agent':<12} {'Activation':<30} {'Circuits Fired'}")
    print(f"  {'-'*12} {'-'*30} {'-'*30}")

    for agent_name in trace.activation_sequence:
        activation = trace.activations[agent_name]
        threshold = parliament.agents[agent_name].activation_threshold

        # Format activation bar
        activation_bar = format_activation_strength(
            activation.activation_strength, threshold
        )

        # Format circuits
        circuits_str = ", ".join(activation.circuits_fired[:3])
        if len(activation.circuits_fired) > 3:
            circuits_str += "..."

        print(f"  {agent_name:<12} {activation_bar}  {circuits_str}")

    # Active agents summary
    active_agents = [
        name
        for name, act in trace.activations.items()
        if act.activation_strength >= parliament.agents[name].activation_threshold
    ]
    print(f"\n  Active Agents ({len(active_agents)}): {', '.join(active_agents)}")

    # Circuits fired
    print_subsection("⚙️  Circuits Fired")
    circuit_groups = {}
    for agent_name, activation in trace.activations.items():
        if activation.circuits_fired:
            circuit_groups[agent_name] = activation.circuits_fired

    if circuit_groups:
        for agent_name, circuits in circuit_groups.items():
            print(f"  [{agent_name}]")
            for circuit in circuits:
                print(f"    • {circuit}")
    else:
        print("  (No circuits fired)")

    # Pattern flags
    print_subsection("🚩 Pattern Flags")
    if trace.pattern_flags:
        for flag in trace.pattern_flags:
            # Split flag into type and description
            if ":" in flag:
                flag_type, description = flag.split(":", 1)
                print(f"  ⚠️  {flag_type}")
                print(f"     {description.strip()}")
            else:
                print(f"  ⚠️  {flag}")
    else:
        print("  ✓ No concerning patterns detected")

    # Lineage path
    print_subsection("🌳 Decision Lineage")
    if trace.lineage_path:
        print("  Circuit path (activation > 0.5):")
        for i, circuit_path in enumerate(trace.lineage_path, 1):
            agent, circuit = circuit_path.split(".", 1)
            print(f"    {i}. {agent:<10} → {circuit}")
    else:
        print("  (No high-activation lineage)")

    # Activation sequence
    print_subsection("📜 Activation Sequence")
    print("  " + " → ".join(trace.activation_sequence))

    # Dharmic alignment details
    print_subsection("☯️  Dharmic Alignment Details")
    alignment_pct = trace.dharmic_alignment * 100

    if alignment_pct >= 80:
        alignment_status = "✓ EXCELLENT - Proper dharmic flow"
    elif alignment_pct >= 60:
        alignment_status = "○ GOOD - Generally aligned"
    elif alignment_pct >= 40:
        alignment_status = "⚠ FAIR - Some misalignment"
    else:
        alignment_status = "✗ POOR - Significant misalignment"

    print(f"  Score: {alignment_pct:.1f}% - {alignment_status}")

    # Additional context
    print_subsection("📎 Additional Context")
    print(f"  Decision stored in history (#{len(parliament.decision_history)})")
    print(f"  Total parliament decisions: {parliament.kshana_counter}")

    # Summary box
    print_section("📋 SUMMARY", "=")
    print(f"""
  Query:              {trace.query}
  Decision ID:        {trace.decision_id[:16]}...
  Active Agents:      {len(active_agents)}/{len(trace.activations)}
  Sparsity:           {trace.sparsity_ratio:.1%}
  Confidence:         {trace.confidence:.1%}
  Dharmic Alignment:  {trace.dharmic_alignment:.1%}
  Pattern Flags:      {len(trace.pattern_flags)}
  Lineage Depth:      {len(trace.lineage_path)} circuits
    """)

    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
