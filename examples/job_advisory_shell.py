#!/usr/bin/env python3
"""Job Advisory Shell - Interactive REPL for Parliament-powered job hunting.

This interactive shell provides a command-line interface to consult the
Kragentic Parliament for job application advice, track decisions, and
monitor your skill development.

Usage:
    python3 examples/job_advisory_shell.py

Commands:
    help                 - Show all commands
    list [min_score]     - List scraped jobs
    show <job_id>        - Show job details
    advise <job_id>      - Get Parliament recommendation
    skills               - Show current skill levels
    gaps                 - Show learning gaps
    history [limit]      - Show past decisions
    stats                - Show accuracy stats
    calibrate            - Suggest threshold adjustments
    log <log_id> <outcome> - Update decision outcome
    quit / exit          - Close shell
"""

import sys
import json
from pathlib import Path
from typing import Optional, List, Dict, Any

# Add project root and src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from src.integrations.jobs_db_integration import JobsDBIntegration
from src.integrations.validation import ParliamentValidator
from src.parliament.kragentic_parliament import KragenticParliament

# Try to import readline for better input handling
try:
    import readline
    HAS_READLINE = True
except ImportError:
    HAS_READLINE = False


# ============================================================================
# ANSI Color Codes
# ============================================================================

class Colors:
    """ANSI color codes for terminal output."""
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    DIM = "\033[2m"
    END = "\033[0m"


# ============================================================================
# Job Advisory Shell
# ============================================================================

class JobAdvisoryShell:
    """Interactive shell for Parliament-powered job hunting advice."""

    def __init__(self):
        """Initialize the shell."""
        self.jobs_db: Optional[JobsDBIntegration] = None
        self.parliament: Optional[KragenticParliament] = None
        self.running = True
        self.prompt = f"{Colors.BOLD}{Colors.CYAN}jobs>{Colors.END} "

    def start(self):
        """Start the interactive shell."""
        self.show_banner()
        self.initialize()

        if not self.jobs_db or not self.jobs_db.connected:
            print(f"{Colors.RED}✗ Failed to initialize. Exiting.{Colors.END}")
            return

        print(f"\n{Colors.GREEN}✓ Ready! Type 'help' for commands.{Colors.END}\n")

        # Main REPL loop
        while self.running:
            try:
                command = input(self.prompt).strip()
                if command:
                    self.process_command(command)
            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}Use 'quit' or 'exit' to close.{Colors.END}")
            except EOFError:
                print()
                self.cmd_quit([])
                break

        # Cleanup
        if self.jobs_db:
            self.jobs_db.disconnect()
            print(f"{Colors.GREEN}✓ Disconnected from database{Colors.END}")

    def show_banner(self):
        """Display welcome banner."""
        banner = f"""
{Colors.BOLD}{Colors.CYAN}╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║            🏛️  PARLIAMENT JOB ADVISORY SHELL                 ║
║                                                               ║
║         AI-Powered Career Guidance with Real Data            ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝{Colors.END}

{Colors.DIM}Kragentic Parliament: 7 specialized agents providing data-grounded
career advice based on your real interview history, skills, and outcomes.{Colors.END}
"""
        print(banner)

    def initialize(self):
        """Initialize database connection and parliament."""
        print(f"{Colors.CYAN}Initializing...{Colors.END}")

        # Connect to database
        try:
            self.jobs_db = JobsDBIntegration()
            if self.jobs_db.connect():
                print(f"{Colors.GREEN}✓{Colors.END} Connected to jobs database")
            else:
                print(f"{Colors.RED}✗{Colors.END} Failed to connect to database")
                return
        except Exception as e:
            print(f"{Colors.RED}✗{Colors.END} Database error: {e}")
            return

        # Initialize parliament
        try:
            self.parliament = KragenticParliament(integration=self.jobs_db)
            agent_count = len(self.parliament.agents)
            print(f"{Colors.GREEN}✓{Colors.END} Parliament initialized ({agent_count} agents)")
        except Exception as e:
            print(f"{Colors.RED}✗{Colors.END} Parliament error: {e}")

    def process_command(self, command: str):
        """Process a shell command.

        Args:
            command: User input command string
        """
        parts = command.split()
        if not parts:
            return

        cmd = parts[0].lower()
        args = parts[1:]

        # Command dispatch
        commands = {
            'help': self.cmd_help,
            'list': self.cmd_list,
            'show': self.cmd_show,
            'advise': self.cmd_advise,
            'skills': self.cmd_skills,
            'gaps': self.cmd_gaps,
            'history': self.cmd_history,
            'stats': self.cmd_stats,
            'calibrate': self.cmd_calibrate,
            'log': self.cmd_log,
            'quit': self.cmd_quit,
            'exit': self.cmd_quit,
        }

        if cmd in commands:
            try:
                commands[cmd](args)
            except Exception as e:
                print(f"{Colors.RED}Error:{Colors.END} {e}")
        else:
            print(f"{Colors.YELLOW}Unknown command: '{cmd}'. Type 'help' for available commands.{Colors.END}")

    # ========================================================================
    # COMMAND IMPLEMENTATIONS
    # ========================================================================

    def cmd_help(self, args: List[str]):
        """Show help for all commands."""
        help_text = f"""
{Colors.BOLD}Available Commands:{Colors.END}
{Colors.CYAN}──────────────────────────────────────────────────────────────{Colors.END}

{Colors.BOLD}Job Search:{Colors.END}
  {Colors.GREEN}list{Colors.END} [min_score]      List scraped jobs (default: score >= 70)
  {Colors.GREEN}show{Colors.END} <job_id>         Show detailed job information
  {Colors.GREEN}advise{Colors.END} <job_id>       Get Parliament recommendation for a job

{Colors.BOLD}Self-Assessment:{Colors.END}
  {Colors.GREEN}skills{Colors.END}                Show current skill levels from interviews
  {Colors.GREEN}gaps{Colors.END}                  Show identified learning gaps

{Colors.BOLD}Decision Tracking:{Colors.END}
  {Colors.GREEN}history{Colors.END} [limit]       Show past Parliament decisions (default: 10)
  {Colors.GREEN}stats{Colors.END}                 Show Parliament accuracy statistics
  {Colors.GREEN}calibrate{Colors.END}             Suggest agent threshold adjustments
  {Colors.GREEN}log{Colors.END} <id> <outcome>    Update decision outcome
                         Outcomes: applied, callback, interview, offer

{Colors.BOLD}System:{Colors.END}
  {Colors.GREEN}help{Colors.END}                  Show this help message
  {Colors.GREEN}quit{Colors.END} / {Colors.GREEN}exit{Colors.END}         Exit the shell

{Colors.BOLD}Examples:{Colors.END}
  jobs> list 80               # Show jobs with score >= 80
  jobs> show 42               # Show details for job #42
  jobs> advise 42             # Get Parliament advice on job #42
  jobs> log 15 callback       # Mark decision #15: got callback
  jobs> stats                 # View Parliament accuracy report
  jobs> calibrate             # Get threshold adjustment suggestions
"""
        print(help_text)

    def cmd_list(self, args: List[str]):
        """List scraped jobs."""
        min_score = 70
        if args:
            try:
                min_score = int(args[0])
            except ValueError:
                print(f"{Colors.RED}Error: Invalid score '{args[0]}'{Colors.END}")
                return

        cursor = self.jobs_db.cursor
        cursor.execute(
            """
            SELECT id, company, job_title, match_score, classification, scraped_at
            FROM scraped_jobs
            WHERE match_score >= ?
            ORDER BY match_score DESC, scraped_at DESC
            LIMIT 20
        """,
            (min_score,),
        )
        jobs = cursor.fetchall()

        if not jobs:
            print(f"{Colors.YELLOW}No jobs found with score >= {min_score}{Colors.END}")
            return

        print(f"\n{Colors.BOLD}Jobs (score >= {min_score}):{Colors.END}")
        print(f"{Colors.CYAN}{'─' * 80}{Colors.END}")
        print(f"{Colors.BOLD}{'ID':<5} {'Score':<7} {'Company':<20} {'Position':<30} {'Status':<10}{Colors.END}")
        print(f"{Colors.CYAN}{'─' * 80}{Colors.END}")

        for job in jobs:
            job_id, company, job_title, match_score, classification, scraped_at = job

            # Color code by score
            if match_score >= 90:
                score_color = Colors.GREEN
            elif match_score >= 80:
                score_color = Colors.YELLOW
            else:
                score_color = Colors.DIM

            # Truncate long strings
            company_display = (company[:17] + "...") if len(company) > 20 else company
            title_display = (job_title[:27] + "...") if len(job_title) > 30 else job_title
            status = classification or "new"

            print(
                f"{job_id:<5} {score_color}{match_score:<7.0f}{Colors.END} "
                f"{company_display:<20} {title_display:<30} {Colors.DIM}{status:<10}{Colors.END}"
            )

        print(f"{Colors.CYAN}{'─' * 80}{Colors.END}")
        print(f"{Colors.DIM}Showing {len(jobs)} jobs. Use 'show <id>' for details.{Colors.END}\n")

    def cmd_show(self, args: List[str]):
        """Show detailed job information."""
        if not args:
            print(f"{Colors.RED}Error: Missing job_id. Usage: show <job_id>{Colors.END}")
            return

        try:
            job_id = int(args[0])
        except ValueError:
            print(f"{Colors.RED}Error: Invalid job_id '{args[0]}'{Colors.END}")
            return

        cursor = self.jobs_db.cursor
        cursor.execute(
            """
            SELECT id, company, job_title, match_score, job_url, tags, description,
                   classification, scraped_at, location, salary_range
            FROM scraped_jobs
            WHERE id = ?
        """,
            (job_id,),
        )
        job = cursor.fetchone()

        if not job:
            print(f"{Colors.RED}Error: Job #{job_id} not found{Colors.END}")
            return

        (
            job_id,
            company,
            job_title,
            match_score,
            job_url,
            tags,
            description,
            classification,
            scraped_at,
            location,
            salary,
        ) = job

        # Display job details
        print(f"\n{Colors.BOLD}Job #{job_id}:{Colors.END}")
        print(f"{Colors.CYAN}{'─' * 70}{Colors.END}")

        print(f"{Colors.BOLD}Company:{Colors.END} {company}")
        print(f"{Colors.BOLD}Position:{Colors.END} {job_title}")

        # Score with color
        if match_score >= 90:
            score_color = Colors.GREEN
        elif match_score >= 80:
            score_color = Colors.YELLOW
        else:
            score_color = Colors.DIM
        print(f"{Colors.BOLD}Match Score:{Colors.END} {score_color}{match_score:.0f}/100{Colors.END}")

        if location:
            print(f"{Colors.BOLD}Location:{Colors.END} {location}")
        if salary:
            print(f"{Colors.BOLD}Salary:{Colors.END} {salary}")

        print(f"{Colors.BOLD}Classification:{Colors.END} {classification or 'new'}")
        print(f"{Colors.BOLD}Scraped:{Colors.END} {scraped_at}")

        if tags:
            print(f"\n{Colors.BOLD}Tags/Skills:{Colors.END}")
            # Parse JSON or plain text
            try:
                tag_list = json.loads(tags)
                print(f"  {', '.join(tag_list[:15])}")  # Show first 15
            except (json.JSONDecodeError, TypeError):
                print(f"  {tags[:200]}")

        if description:
            print(f"\n{Colors.BOLD}Description:{Colors.END}")
            desc_preview = description[:300] + "..." if len(description) > 300 else description
            print(f"  {desc_preview}")

        if job_url:
            print(f"\n{Colors.BOLD}URL:{Colors.END} {Colors.CYAN}{job_url}{Colors.END}")

        print(f"{Colors.CYAN}{'─' * 70}{Colors.END}")
        print(f"{Colors.DIM}Use 'advise {job_id}' to get Parliament recommendation{Colors.END}\n")

    def cmd_advise(self, args: List[str]):
        """Get Parliament recommendation for a job."""
        if not args:
            print(f"{Colors.RED}Error: Missing job_id. Usage: advise <job_id>{Colors.END}")
            return

        try:
            job_id = int(args[0])
        except ValueError:
            print(f"{Colors.RED}Error: Invalid job_id '{args[0]}'{Colors.END}")
            return

        # Fetch job details
        cursor = self.jobs_db.cursor
        cursor.execute(
            """
            SELECT company, job_title, match_score, tags
            FROM scraped_jobs
            WHERE id = ?
        """,
            (job_id,),
        )
        job = cursor.fetchone()

        if not job:
            print(f"{Colors.RED}Error: Job #{job_id} not found{Colors.END}")
            return

        company, job_title, match_score, tags = job

        # Display job summary
        print(f"\n{Colors.BOLD}Consulting Parliament on Job #{job_id}:{Colors.END}")
        print(f"{Colors.CYAN}{'─' * 70}{Colors.END}")
        print(f"{Colors.BOLD}{company}{Colors.END} - {job_title}")
        print(f"Match Score: {match_score:.0f}/100")
        print(f"{Colors.CYAN}{'─' * 70}{Colors.END}\n")

        # Prepare query
        query = f"Should I apply to {job_title} role at {company}?"

        # Fetch integration context
        print(f"{Colors.CYAN}Loading integration data...{Colors.END}")
        context = self.jobs_db.fetch_context("job_evaluation", opportunity_id=job_id)

        # Parse tags as requirements
        try:
            req_list = json.loads(tags) if tags else []
            context["job_requirements"] = req_list[:5]  # Top 5 requirements
        except (json.JSONDecodeError, TypeError):
            context["job_requirements"] = ["Role requirements available"]

        # Enrich with all agent data
        for agent_name in ["krudi", "smriti", "parva", "rudi", "maya", "shanti"]:
            agent_context = self.jobs_db.enrich_agent_context(agent_name, context)
            context.update(agent_context)

        # Show context summary
        data_sources = []
        if context.get("user_skills"):
            data_sources.append(f"{len(context['user_skills'])} skills assessed")
        if context.get("smriti_history"):
            data_sources.append(f"{len(context['smriti_history'])} interview questions")
        if context.get("learning_gaps"):
            data_sources.append(f"{len(context['learning_gaps'])} learning gaps")
        if context.get("parva_trajectory"):
            data_sources.append(f"{len(context['parva_trajectory'])} applications tracked")

        print(f"{Colors.GREEN}✓{Colors.END} Loaded: {', '.join(data_sources)}\n")

        # Deliberate
        print(f"{Colors.BOLD}Parliament deliberating...{Colors.END}\n")
        decision, trace = self.parliament.deliberate(query, context)

        # Show agent activations
        self.display_activations(trace)

        # Show key agent responses
        print(f"\n{Colors.BOLD}Agent Perspectives:{Colors.END}")
        print(f"{Colors.CYAN}{'─' * 70}{Colors.END}")

        for agent_name in ["krudi", "smriti", "parva"]:
            response = trace.agent_responses.get(agent_name, "")
            if response:
                print(f"\n{Colors.BOLD}{agent_name.upper()}:{Colors.END}")
                # Show first 3 lines
                lines = response.split("\n")
                for line in lines[:3]:
                    if line.strip():
                        print(f"  {line}")
                if len(lines) > 3:
                    print(f"  {Colors.DIM}... (truncated){Colors.END}")

        # Kshana synthesis
        print(f"\n{Colors.BOLD}KSHANA'S SYNTHESIS:{Colors.END}")
        print(f"{Colors.CYAN}{'─' * 70}{Colors.END}")
        print(f"{decision}\n")

        # Final recommendation
        self.display_recommendation(trace)

        # Display metrics
        self.display_metrics(trace)

        # Log decision
        try:
            log_id = self.jobs_db.log_parliament_decision(trace, job_id=job_id)
            print(f"\n{Colors.GREEN}✓{Colors.END} Decision logged as #{log_id}")
            print(f"{Colors.DIM}Update outcome later with: log {log_id} <outcome>{Colors.END}\n")
        except Exception as e:
            print(f"\n{Colors.YELLOW}⚠{Colors.END} Could not log decision: {e}\n")

    def cmd_skills(self, args: List[str]):
        """Show current skill levels from interview questions."""
        cursor = self.jobs_db.cursor
        cursor.execute(
            """
            SELECT question_type, AVG(my_rating) as avg_rating, COUNT(*) as count
            FROM interview_questions
            WHERE my_rating IS NOT NULL
            GROUP BY question_type
            ORDER BY avg_rating DESC
        """
        )
        skills = cursor.fetchall()

        if not skills:
            print(f"{Colors.YELLOW}No skill data available yet.{Colors.END}")
            print(f"{Colors.DIM}Add interview questions to track your skills.{Colors.END}\n")
            return

        total_questions = sum(s[2] for s in skills)

        print(f"\n{Colors.BOLD}Current Skill Levels{Colors.END} (from {total_questions} interview questions):")
        print(f"{Colors.CYAN}{'─' * 70}{Colors.END}")

        for skill, avg_rating, count in skills:
            # Create progress bar
            bar_length = 20
            filled = int((avg_rating / 5.0) * bar_length)
            bar = "█" * filled + "░" * (bar_length - filled)

            # Color code by rating
            if avg_rating >= 3.5:
                color = Colors.GREEN
            elif avg_rating >= 2.5:
                color = Colors.YELLOW
            else:
                color = Colors.RED

            print(
                f"{skill:<20} {color}{bar}{Colors.END} "
                f"{avg_rating:.1f}/5  {Colors.DIM}({count} question{'s' if count != 1 else ''}){Colors.END}"
            )

        print(f"{Colors.CYAN}{'─' * 70}{Colors.END}\n")

    def cmd_gaps(self, args: List[str]):
        """Show learning gaps."""
        cursor = self.jobs_db.cursor
        cursor.execute(
            """
            SELECT name, category, priority, status, estimated_hours
            FROM study_topics
            ORDER BY priority DESC
            LIMIT 10
        """
        )
        gaps = cursor.fetchall()

        if not gaps:
            print(f"{Colors.YELLOW}No learning gaps identified yet.{Colors.END}\n")
            return

        print(f"\n{Colors.BOLD}Learning Gaps{Colors.END} ({len(gaps)} identified):")
        print(f"{Colors.CYAN}{'─' * 70}{Colors.END}")

        for i, (name, category, priority, status, est_hours) in enumerate(gaps, 1):
            # Priority label
            if priority >= 5:
                priority_label = f"{Colors.RED}CRITICAL{Colors.END}"
            elif priority >= 4:
                priority_label = f"{Colors.YELLOW}HIGH{Colors.END}"
            else:
                priority_label = f"{Colors.GREEN}MEDIUM{Colors.END}"

            print(f"\n{Colors.BOLD}{i}. [{priority_label}] {name}{Colors.END} (Priority: {priority})")
            print(f"   Category: {category}")
            print(f"   Status: {status or 'Not Started'}")
            if est_hours:
                print(f"   Estimated: {est_hours} hours")

        print(f"\n{Colors.CYAN}{'─' * 70}{Colors.END}\n")

    def cmd_history(self, args: List[str]):
        """Show past Parliament decisions."""
        limit = 10
        if args:
            try:
                limit = int(args[0])
            except ValueError:
                print(f"{Colors.RED}Error: Invalid limit '{args[0]}'{Colors.END}")
                return

        cursor = self.jobs_db.cursor
        cursor.execute(
            """
            SELECT id, timestamp, query, confidence, applied, callback, interview, offer
            FROM parliament_decisions
            ORDER BY timestamp DESC
            LIMIT ?
        """,
            (limit,),
        )
        decisions = cursor.fetchall()

        if not decisions:
            print(f"{Colors.YELLOW}No decision history yet.{Colors.END}")
            print(f"{Colors.DIM}Use 'advise <job_id>' to get recommendations.{Colors.END}\n")
            return

        print(f"\n{Colors.BOLD}Parliament Decision History:{Colors.END}")
        print(f"{Colors.CYAN}{'─' * 70}{Colors.END}")

        for decision_id, timestamp, query, confidence, applied, callback, interview, offer in decisions:
            # Format timestamp
            date = timestamp.split("T")[0] if "T" in timestamp else timestamp[:10]

            # Determine recommendation
            if confidence >= 0.7:
                rec = f"{Colors.GREEN}APPLY{Colors.END}"
            elif confidence >= 0.5:
                rec = f"{Colors.YELLOW}CONSIDER{Colors.END}"
            else:
                rec = f"{Colors.RED}SKIP{Colors.END}"

            # Truncate query
            query_short = query[:50] + "..." if len(query) > 50 else query

            print(f"\n{Colors.BOLD}#{decision_id}{Colors.END} | {date} | {query_short}")
            print(f"     Decision: {rec} (Confidence: {confidence * 100:.0f}%)")

            # Outcome
            if applied:
                outcome_parts = []
                if applied:
                    outcome_parts.append(f"{Colors.GREEN}Applied{Colors.END}")
                if callback:
                    outcome_parts.append(f"{Colors.GREEN}Callback{Colors.END}")
                if interview:
                    outcome_parts.append(f"{Colors.GREEN}Interview{Colors.END}")
                if offer:
                    outcome_parts.append(f"{Colors.GREEN}Offer{Colors.END}")

                if not callback and not interview and not offer:
                    outcome_parts.append(f"{Colors.DIM}No response yet{Colors.END}")

                print(f"     Outcome: {' → '.join(outcome_parts)}")
            else:
                print(f"     Outcome: {Colors.DIM}Not applied / No outcome recorded{Colors.END}")

        print(f"\n{Colors.CYAN}{'─' * 70}{Colors.END}\n")

    def cmd_stats(self, args: List[str]):
        """Show Parliament accuracy statistics."""
        try:
            validator = ParliamentValidator(self.jobs_db)
            report = validator.generate_accuracy_report()
            print(report)
        except Exception as e:
            print(f"{Colors.RED}Error generating stats: {e}{Colors.END}\n")

    def cmd_calibrate(self, args: List[str]):
        """Suggest activation threshold adjustments based on accuracy."""
        try:
            validator = ParliamentValidator(self.jobs_db)
            adjustments = validator.suggest_threshold_adjustments()

            if 'note' in adjustments:
                print(f"\n{Colors.YELLOW}{adjustments['note']}{Colors.END}\n")
                return

            print(f"\n{Colors.BOLD}Suggested Threshold Adjustments:{Colors.END}")
            print(f"{Colors.CYAN}{'─' * 70}{Colors.END}")
            print(f"\n{Colors.DIM}Based on historical accuracy patterns{Colors.END}\n")

            # Sort by absolute adjustment magnitude
            sorted_adjustments = sorted(
                adjustments.items(),
                key=lambda x: abs(x[1]),
                reverse=True
            )

            agent_names_full = {
                'krudi': 'Krudi (Reality)',
                'smriti': 'Smriti (Memory)',
                'parva': 'Parva (Causality)',
                'rudi': 'Rudi (Transformation)',
                'maya': 'Maya (Simulation)',
                'shanti': 'Shanti (Equilibrium)',
                'kshana': 'Kshana (Synthesis)'
            }

            has_adjustments = False
            for agent_name, adjustment in sorted_adjustments:
                if adjustment == 0.0:
                    continue

                has_adjustments = True
                full_name = agent_names_full.get(agent_name, agent_name.capitalize())

                # Color code by direction
                if adjustment > 0:
                    color = Colors.RED
                    direction = "INCREASE"
                    explanation = "(agent over-active or inaccurate)"
                else:
                    color = Colors.GREEN
                    direction = "DECREASE"
                    explanation = "(agent under-active or too conservative)"

                print(f"{full_name}:")
                print(f"  {color}{direction} threshold by {abs(adjustment):+.2f}{Colors.END}")
                print(f"  {Colors.DIM}{explanation}{Colors.END}\n")

            if not has_adjustments:
                print(f"{Colors.GREEN}✓ All agents well-calibrated!{Colors.END}")
                print(f"{Colors.DIM}No threshold adjustments needed.{Colors.END}\n")
            else:
                print(f"\n{Colors.CYAN}{'─' * 70}{Colors.END}")
                print(f"{Colors.DIM}Note: Apply these adjustments manually in parliament configuration{Colors.END}")
                print(f"{Colors.DIM}or wait for automatic calibration in future updates.{Colors.END}\n")

        except Exception as e:
            print(f"{Colors.RED}Error generating calibration suggestions: {e}{Colors.END}\n")

    def cmd_log(self, args: List[str]):
        """Update decision outcome."""
        if len(args) < 2:
            print(f"{Colors.RED}Error: Usage: log <log_id> <outcome>{Colors.END}")
            print(f"{Colors.DIM}Outcomes: applied, callback, interview, offer{Colors.END}\n")
            return

        try:
            log_id = int(args[0])
        except ValueError:
            print(f"{Colors.RED}Error: Invalid log_id '{args[0]}'{Colors.END}")
            return

        outcome_type = args[1].lower()
        valid_outcomes = ["applied", "callback", "interview", "offer"]

        if outcome_type not in valid_outcomes:
            print(f"{Colors.RED}Error: Invalid outcome '{outcome_type}'{Colors.END}")
            print(f"{Colors.DIM}Valid outcomes: {', '.join(valid_outcomes)}{Colors.END}\n")
            return

        # Build outcome dict
        outcome = {
            "applied": outcome_type == "applied" or outcome_type in ["callback", "interview", "offer"],
            "callback": outcome_type in ["callback", "interview", "offer"],
            "interview": outcome_type in ["interview", "offer"],
            "offer": outcome_type == "offer",
            "notes": f"Updated via shell: {outcome_type}",
        }

        # Update
        try:
            success = self.jobs_db.update_decision_outcome(log_id, outcome)
            if success:
                print(f"{Colors.GREEN}✓{Colors.END} Updated decision #{log_id}: {outcome_type} = True\n")
            else:
                print(f"{Colors.RED}✗{Colors.END} Failed to update decision #{log_id} (not found?)\n")
        except Exception as e:
            print(f"{Colors.RED}Error updating outcome: {e}{Colors.END}\n")

    def cmd_quit(self, args: List[str]):
        """Exit the shell."""
        print(f"\n{Colors.CYAN}Goodbye! May your job search be successful. 🎯{Colors.END}\n")
        self.running = False

    # ========================================================================
    # DISPLAY HELPERS
    # ========================================================================

    def display_activations(self, trace):
        """Display agent activation bar chart."""
        print(f"{Colors.BOLD}Agent Activations:{Colors.END}")

        max_strength = max(
            act.activation_strength for act in trace.activations.values()
        )

        for agent_name in ["krudi", "smriti", "parva", "rudi", "maya", "shanti", "kshana"]:
            activation = trace.activations.get(agent_name)
            if not activation:
                continue

            strength = activation.activation_strength
            threshold = self.parliament.agents[agent_name].activation_threshold

            # Calculate bar length
            bar_length = 30
            filled = int((strength / max(max_strength, 1.0)) * bar_length)

            # Color based on threshold
            if strength >= threshold:
                color = Colors.GREEN
                status = "ACTIVE"
            else:
                color = Colors.DIM
                status = "passive"

            bar = "█" * filled + "░" * (bar_length - filled)

            print(
                f"  {agent_name.capitalize():<10} {color}{bar}{Colors.END} "
                f"{strength:.3f} ({status})"
            )

    def display_recommendation(self, trace):
        """Display final recommendation with color."""
        confidence = trace.confidence

        if confidence >= 0.7:
            color = Colors.GREEN
            symbol = "✓"
            recommendation = "APPLY"
        elif confidence >= 0.5:
            color = Colors.YELLOW
            symbol = "⚠"
            recommendation = "CONSIDER"
        else:
            color = Colors.RED
            symbol = "✗"
            recommendation = "SKIP"

        print(f"{Colors.CYAN}{'─' * 70}{Colors.END}")
        print(f"\n{color}{Colors.BOLD}{symbol} RECOMMENDATION: {recommendation}{Colors.END}")
        print(f"{color}Confidence: {confidence * 100:.1f}%{Colors.END}\n")
        print(f"{Colors.CYAN}{'─' * 70}{Colors.END}")

    def display_metrics(self, trace):
        """Display decision metrics."""
        print(f"\n{Colors.BOLD}Decision Metrics:{Colors.END}")
        print(f"  Confidence: {trace.confidence * 100:.1f}%")
        print(f"  Dharmic Alignment: {trace.dharmic_alignment * 100:.1f}%")
        print(f"  Sparsity: {trace.sparsity_ratio * 100:.1f}%")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point."""
    shell = JobAdvisoryShell()
    shell.start()


if __name__ == "__main__":
    main()
