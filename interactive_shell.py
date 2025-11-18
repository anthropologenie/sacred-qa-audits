#!/usr/bin/env python3
"""Interactive shell for Sacred QA Audits - Kragentic Parliament.

This shell provides a REPL interface to interact with the parliament,
view decision traces, and analyze agent activations.
"""

import sys
from pathlib import Path

# Add src/ to sys.path FIRST
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

import os
from typing import List, Optional
from parliament.kragentic_parliament import KragenticParliament
from circuits.activation_tracker import ParliamentDecisionTrace

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    # Dharmic alignment colors
    HIGH_DHARMA = '\033[92m'  # Green
    MED_DHARMA = '\033[93m'   # Yellow
    LOW_DHARMA = '\033[91m'   # Red


def print_banner():
    """Print welcome banner."""
    banner = f"""
{Colors.HEADER}{Colors.BOLD}╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║      SACRED QA AUDITS - KRAGENTIC PARLIAMENT SHELL           ║
║                                                               ║
║      Circuit-traced Multi-Agent Decision System              ║
║      with Dharmic Validation                                 ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝{Colors.ENDC}

{Colors.OKCYAN}Type 'help' for available commands or enter a query to deliberate.{Colors.ENDC}
"""
    print(banner)


def print_help():
    """Print help information."""
    help_text = f"""
{Colors.BOLD}Available Commands:{Colors.ENDC}

  {Colors.OKGREEN}help{Colors.ENDC}           - Show this help message
  {Colors.OKGREEN}history{Colors.ENDC}        - Show decision history
  {Colors.OKGREEN}stats{Colors.ENDC}          - Show agent activation statistics
  {Colors.OKGREEN}last{Colors.ENDC}           - Show details of last decision
  {Colors.OKGREEN}circuits on{Colors.ENDC}    - Enable detailed circuit tracing
  {Colors.OKGREEN}circuits off{Colors.ENDC}   - Disable detailed circuit tracing
  {Colors.OKGREEN}clear{Colors.ENDC}          - Clear the screen
  {Colors.OKGREEN}quit{Colors.ENDC}           - Exit the shell (or use Ctrl+D)

{Colors.BOLD}Query Mode:{Colors.ENDC}
  Enter any question to deliberate with the parliament.
  The parliament will activate relevant agents and synthesize a decision.

{Colors.BOLD}Examples:{Colors.ENDC}
  > Should we implement a new feature?
  > What are the consequences of this decision?
  > How should we balance speed and quality?
"""
    print(help_text)


def format_dharmic_alignment(alignment: float) -> str:
    """Format dharmic alignment with color coding."""
    if alignment >= 0.75:
        color = Colors.HIGH_DHARMA
        label = "HIGH"
    elif alignment >= 0.50:
        color = Colors.MED_DHARMA
        label = "MEDIUM"
    else:
        color = Colors.LOW_DHARMA
        label = "LOW"

    return f"{color}{alignment:.2%} ({label}){Colors.ENDC}"


def draw_bar_chart(value: float, width: int = 30, char: str = '█') -> str:
    """Draw a simple bar chart for activation values."""
    filled = int(value * width)
    empty = width - filled

    # Color based on value
    if value >= 0.7:
        color = Colors.OKGREEN
    elif value >= 0.4:
        color = Colors.WARNING
    else:
        color = Colors.FAIL

    bar = f"{color}{char * filled}{Colors.ENDC}{'░' * empty}"
    return f"{bar} {value:.2f}"


def print_activation_chart(trace: ParliamentDecisionTrace, show_circuits: bool = False):
    """Print agent activations as bar charts."""
    print(f"\n{Colors.BOLD}Agent Activations:{Colors.ENDC}")
    print("─" * 70)

    for agent_name in trace.activation_sequence:
        activation = trace.activations.get(agent_name)
        if activation:
            strength = activation.activation_strength
            print(f"  {agent_name:10} {draw_bar_chart(strength)}")

            if show_circuits and activation.circuits_fired:
                circuits_str = ", ".join(activation.circuits_fired)
                print(f"             {Colors.OKCYAN}↳ Circuits: {circuits_str}{Colors.ENDC}")

    print("─" * 70)


def print_decision_summary(trace: ParliamentDecisionTrace, show_circuits: bool = False):
    """Print a summary of the decision trace."""
    print(f"\n{Colors.BOLD}{Colors.HEADER}Decision Summary:{Colors.ENDC}")
    print(f"  Kshana Index:      {trace.kshana_index}")
    print(f"  Decision ID:       {trace.decision_id[:16]}...")
    print(f"  Active Agents:     {len([a for a in trace.activations.values() if a.activation_strength >= 0.3])}/{len(trace.activations)}")
    print(f"  Sparsity Ratio:    {trace.sparsity_ratio:.2%}")
    print(f"  Confidence:        {trace.confidence:.2%}")
    print(f"  Dharmic Alignment: {format_dharmic_alignment(trace.dharmic_alignment)}")

    if trace.pattern_flags:
        print(f"\n{Colors.WARNING}Pattern Flags:{Colors.ENDC}")
        for flag in trace.pattern_flags:
            print(f"  ⚠ {flag}")

    print_activation_chart(trace, show_circuits)


def print_history(parliament: KragenticParliament):
    """Print decision history."""
    history = parliament.get_decision_history(limit=10)

    if not history:
        print(f"\n{Colors.WARNING}No decisions in history yet.{Colors.ENDC}")
        return

    print(f"\n{Colors.BOLD}Decision History (last 10):{Colors.ENDC}")
    print("─" * 70)

    for trace in history:
        dharma_str = format_dharmic_alignment(trace.dharmic_alignment)
        print(f"  [{trace.kshana_index:3}] {trace.query[:45]:45} | Dharma: {dharma_str}")

    print("─" * 70)


def print_stats(parliament: KragenticParliament):
    """Print agent statistics."""
    stats = parliament.get_agent_statistics()

    if not stats:
        print(f"\n{Colors.WARNING}No statistics available yet.{Colors.ENDC}")
        return

    print(f"\n{Colors.BOLD}Agent Activation Statistics:{Colors.ENDC}")
    print("─" * 70)
    print(f"{'Agent':10} {'Total':>7} {'Active':>7} {'Mean Strength':>13} {'Rate':>7}")
    print("─" * 70)

    for agent_name, agent_stats in stats.items():
        total = agent_stats['total_activations']
        active = agent_stats['active_count']
        mean = agent_stats['mean_strength']
        rate = agent_stats['activation_rate']

        print(f"{agent_name:10} {total:>7} {active:>7} {mean:>13.2f} {rate:>7.1%}")

    print("─" * 70)


def main():
    """Main interactive shell loop."""
    print_banner()

    # Initialize parliament
    parliament = KragenticParliament()
    show_circuits = False
    last_trace: Optional[ParliamentDecisionTrace] = None

    # Main REPL loop
    while True:
        try:
            # Get user input
            user_input = input(f"\n{Colors.OKBLUE}{Colors.BOLD}parliament>{Colors.ENDC} ").strip()

            # Skip empty input
            if not user_input:
                continue

            # Handle commands
            if user_input.lower() == 'quit' or user_input.lower() == 'exit':
                print(f"\n{Colors.OKCYAN}Farewell. May your decisions be dharmically aligned.{Colors.ENDC}\n")
                break

            elif user_input.lower() == 'help':
                print_help()

            elif user_input.lower() == 'clear':
                os.system('clear' if os.name == 'posix' else 'cls')
                print_banner()

            elif user_input.lower() == 'history':
                print_history(parliament)

            elif user_input.lower() == 'stats':
                print_stats(parliament)

            elif user_input.lower() == 'last':
                if last_trace:
                    print_decision_summary(last_trace, show_circuits)
                    print(f"\n{Colors.BOLD}Final Decision:{Colors.ENDC}")
                    print(last_trace.decision)
                else:
                    print(f"\n{Colors.WARNING}No decisions made yet.{Colors.ENDC}")

            elif user_input.lower() == 'circuits on':
                show_circuits = True
                print(f"{Colors.OKGREEN}Circuit tracing enabled.{Colors.ENDC}")

            elif user_input.lower() == 'circuits off':
                show_circuits = False
                print(f"{Colors.WARNING}Circuit tracing disabled.{Colors.ENDC}")

            else:
                # Treat as query for parliament deliberation
                print(f"\n{Colors.OKCYAN}Deliberating...{Colors.ENDC}")

                decision, trace = parliament.deliberate(user_input)
                last_trace = trace

                # Print decision summary
                print_decision_summary(trace, show_circuits)

                # Print the full decision
                print(f"\n{Colors.BOLD}Parliament Decision:{Colors.ENDC}")
                print(decision)

        except EOFError:
            # Handle Ctrl+D
            print(f"\n\n{Colors.OKCYAN}Farewell. May your decisions be dharmically aligned.{Colors.ENDC}\n")
            break

        except KeyboardInterrupt:
            # Handle Ctrl+C
            print(f"\n\n{Colors.WARNING}Interrupted. Type 'quit' to exit or continue querying.{Colors.ENDC}")
            continue

        except Exception as e:
            print(f"\n{Colors.FAIL}Error: {e}{Colors.ENDC}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
