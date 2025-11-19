# Sacred QA Audits ↔ Jobs Application Automation Integration

## Overview

This document describes the symbiotic integration between **Sacred QA Audits** (the Kragentic Parliament AI decision system) and **Jobs Application Automation** (job hunting tracker and analytics platform).

The integration enables **bidirectional learning**:
- **Direction 1 (Advisory)**: Parliament provides intelligent job hunting advice grounded in real application data
- **Direction 2 (Training)**: Real-world job outcomes validate Parliament decisions and enable continuous improvement

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     SACRED QA AUDITS                                    │
│                   (Kragentic Parliament)                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │  Krudi   │  │  Smriti  │  │  Parva   │  │   Rudi   │  │   Maya   │ │
│  │ Reality  │  │  Memory  │  │Causality │  │Transform │  │Simulation│ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘ │
│       │             │             │              │             │       │
│       └─────────────┴─────────────┴──────────────┴─────────────┘       │
│                               │                                        │
│                         ┌─────▼─────┐                                  │
│                         │  Kshana   │                                  │
│                         │ Synthesis │                                  │
│                         └─────┬─────┘                                  │
│                               │                                        │
│                    ┌──────────▼──────────┐                             │
│                    │ JobsDBIntegration   │                             │
│                    │  (850 lines)        │                             │
│                    └──────────┬──────────┘                             │
└───────────────────────────────┼─────────────────────────────────────────┘
                                │
                    ┌───────────▼───────────┐
                    │   SQLite Database     │
                    │  jobs-tracker.db      │
                    └───────────┬───────────┘
┌───────────────────────────────▼─────────────────────────────────────────┐
│              JOBS APPLICATION AUTOMATION                                │
│                 (Job Hunting Tracker)                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Tables:                                                                │
│  • opportunities - Applications and status                              │
│  • interview_questions - Questions asked, performance ratings           │
│  • study_topics - Learning gaps and priorities                          │
│  • learning_sessions - Study history and progress                       │
│  • interactions - Interview scheduling                                  │
│  • parliament_decisions - Decision log for validation                   │
│  • scraped_jobs - Job listings from RemoteOK, etc.                      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Data Flow: Bidirectional Learning

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    DIRECTION 1: ADVISORY                                 │
│           Parliament queries real data → Grounded advice                 │
└──────────────────────────────────────────────────────────────────────────┘

User Query: "Should I apply to Senior Python Engineer at TechCorp?"
                               │
                               ▼
                  ┌────────────────────────┐
                  │  JobsDBIntegration     │
                  │  fetch_context()       │
                  └────────┬───────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
   ┌─────────┐      ┌──────────┐      ┌──────────┐
   │ Skills  │      │Interview │      │Learning  │
   │Ratings  │      │ History  │      │  Gaps    │
   └────┬────┘      └────┬─────┘      └────┬─────┘
        │                │                  │
        └────────────────┼──────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ Parliament Agents    │
              │ • Krudi: Skill check │
              │ • Smriti: Patterns   │
              │ • Parva: Trajectory  │
              │ • Rudi: Growth path  │
              │ • Maya: Outcomes     │
              │ • Shanti: Balance    │
              └──────────┬───────────┘
                         │
                         ▼
                  ┌──────────────┐
                  │   Kshana     │
                  │  Synthesis   │
                  └──────┬───────┘
                         │
                         ▼
              ┌─────────────────────┐
              │ Decision + Advice   │
              │ "APPLY - 85% conf"  │
              └─────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│                    DIRECTION 2: TRAINING                                 │
│        Real outcomes → Accuracy analysis → Calibration                   │
└──────────────────────────────────────────────────────────────────────────┘

Decision logged → User applies → Outcome tracked → Metrics updated
                                                            │
                                                            ▼
                                              ┌──────────────────────┐
                                              │ParliamentValidator   │
                                              │                      │
                                              │ • Accuracy metrics   │
                                              │ • Calibration report │
                                              │ • Threshold tuning   │
                                              └──────────────────────┘
```

## Components

### 1. Integration Layer

#### `src/integrations/base_integration.py`
Abstract interface defining the contract for all integrations.

**Key Methods**:
- `connect()` / `disconnect()` - Database lifecycle
- `fetch_context(query_type, **kwargs)` - Query external data
- `enrich_agent_context(agent_name, context)` - Agent-specific enrichment
- `validate_decision(decision_trace)` - Outcome validation
- `get_supported_query_types()` - Available query types

#### `src/integrations/jobs_db_integration.py` (850 lines)
SQLite bridge to jobs-application-automation database.

**Supported Query Types**:
1. `job_evaluation` - Context for job application decisions
2. `interview_prep` - Interview preparation guidance
3. `learning_priority` - Study topic prioritization
4. `skill_assessment` - Reality check on skill levels

**Agent Enrichment**:
- **Krudi** (Reality): Current skill levels, constraints
- **Smriti** (Memory): Interview history, question patterns
- **Parva** (Causality): Career trajectory, application timeline
- **Rudi** (Transformation): Learning progress, growth potential
- **Maya** (Simulation): Historical outcomes, pattern analysis
- **Shanti** (Equilibrium): Work-life indicators, preferences

**Decision Tracking**:
- `log_parliament_decision()` - Store decision for later validation
- `update_decision_outcome()` - Record real-world results
- `get_decision_accuracy_stats()` - Calculate accuracy metrics

#### `src/integrations/validation.py` (208 lines)
Accuracy tracking and threshold calibration.

**Key Methods**:
- `calculate_accuracy_metrics()` - Comprehensive accuracy analysis
- `generate_accuracy_report()` - Human-readable reports
- `suggest_threshold_adjustments()` - Data-driven calibration

### 2. Enhanced Agents (7/7 Integration-Aware)

All agents have been updated to leverage external data:

#### **Krudi (Reality Agent)**
```python
# Before: Generic reality checks
"Based on typical requirements..."

# After: Grounded in actual skill data
"Your Python rating: 3.8/5 (from 12 interview questions)
Data Warehouse: 1.0/5 (critical gap for this role)
SQL: 4.2/5 (strong match)"
```

#### **Smriti (Memory Agent)**
```python
# Before: No historical context
"Consider your past experience..."

# After: Pattern recognition from real data
"You've applied to 3 similar roles:
- TechCorp (2023): Rejected after technical
- DataCo (2024): Ghosted
- CloudInc (2024): Offer received
Pattern: You excel when role emphasizes Python over SQL"
```

#### **Parva (Causality Agent)**
```python
# Before: Abstract causality
"This could lead to future opportunities..."

# After: Trajectory-based analysis
"Your application velocity: 2.5 applications/week
Time to first interview: avg 8 days
This role fits your ascending trajectory toward senior positions"
```

#### **Rudi (Transformation Agent)**
```python
# Before: Generic growth advice
"This role could help you grow..."

# After: Learning-path aware
"Current study plan: Data Warehousing (15 hours logged)
This role requires exactly what you're learning
Estimated readiness: 3 weeks at current pace"
```

#### **Maya (Simulation Agent)**
```python
# Before: Hypothetical scenarios
"Imagine if you applied..."

# After: Outcome-based modeling
"Similar roles (n=8):
- 62% callback rate
- 38% reached interview
- 12% received offer
Your success pattern: Strong in Python-heavy roles"
```

#### **Shanti (Equilibrium Agent)**
```python
# Before: Generic balance concerns
"Consider work-life balance..."

# After: Preference-aware
"Your preferences (extracted from applications):
- 89% remote applications
- Prefer domain: Fintech (45%), AI/ML (32%)
- Priority distribution: 60% high-priority applications"
```

#### **Kshana (Synthesis Agent)**
Now receives integration metadata and incorporates data grounding into synthesis.

### 3. Examples

#### `examples/job_advisory_demo.py` (430 lines)
Comprehensive showcase demonstrating 7 scenarios:

1. **Job Evaluation** - Should I apply to this role?
2. **Interview Preparation** - How to prepare for Data Warehousing questions?
3. **Learning Priority** - What should I study next?
4. **Skill Reality Check** - Am I really good at Python?
5. **Career Trajectory** - Where am I heading?
6. **Decision Logging** - Track advice and outcomes
7. **Accuracy Validation** - How accurate has Parliament been?

#### `examples/job_advisory_shell.py` (790 lines)
Interactive REPL for Parliament-powered job hunting.

**Commands**:
```bash
help                 - Show all commands
list [min_score]     - List scraped jobs
show <job_id>        - Show job details
advise <job_id>      - Get Parliament recommendation
skills               - Show current skill levels
gaps                 - Show learning gaps
history [limit]      - Show past decisions
stats                - Show accuracy statistics
calibrate            - Suggest threshold adjustments
log <id> <outcome>   - Update decision outcome
quit / exit          - Close shell
```

### 4. Database Schema

The integration uses a dedicated table for decision tracking:

```sql
CREATE TABLE parliament_decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Decision identification
    decision_id TEXT UNIQUE NOT NULL,
    timestamp TEXT NOT NULL,
    query TEXT NOT NULL,
    job_id INTEGER,

    -- Decision details
    agents_active TEXT,          -- JSON array of active agents
    decision_text TEXT,          -- Synthesized decision
    sparsity REAL,               -- Sparsity ratio
    confidence REAL,             -- Confidence (0-1)
    dharmic_alignment REAL,      -- Dharmic alignment (0-1)
    integration_used INTEGER,    -- Was integration used?

    -- Outcome tracking (filled later)
    applied INTEGER DEFAULT 0,
    callback INTEGER DEFAULT 0,
    interview INTEGER DEFAULT 0,
    offer INTEGER DEFAULT 0,
    outcome_notes TEXT,
    outcome_date TEXT,

    FOREIGN KEY (job_id) REFERENCES scraped_jobs(id)
);
```

## Setup

### Prerequisites

1. **Jobs Application Automation** database set up with data
2. **Sacred QA Audits** cloned and dependencies installed

### Installation Steps

```bash
# 1. Navigate to jobs-application-automation
cd ~/projects/jobs-application-automation

# 2. Apply Parliament migration (creates parliament_decisions table)
./scripts/apply_parliament_migration.sh

# 3. Verify migration
sqlite3 data/jobs-tracker.db "SELECT name FROM sqlite_master WHERE type='table' AND name='parliament_decisions';"

# 4. Navigate to sacred-qa-audits
cd ../sacred-qa-audits

# 5. Run integration tests
python3 -m pytest tests/test_integration.py -v

# 6. Try the demo
python3 examples/job_advisory_demo.py

# 7. Launch interactive shell
python3 examples/job_advisory_shell.py
```

### Configuration

The integration auto-detects the database path:

```python
# Default path (relative to sacred-qa-audits)
../jobs-application-automation/data/jobs-tracker.db

# Custom path
from src.integrations.jobs_db_integration import JobsDBIntegration

jobs_db = JobsDBIntegration(db_path="/path/to/jobs-tracker.db")
jobs_db.connect()
```

## Usage

### 1. Basic Advisory (Python API)

```python
from src.integrations.jobs_db_integration import JobsDBIntegration
from src.parliament.kragentic_parliament import KragenticParliament

# Connect to jobs database
jobs_db = JobsDBIntegration()
jobs_db.connect()

# Create Parliament with integration
parliament = KragenticParliament(integration=jobs_db)

# Get job evaluation context
context = jobs_db.fetch_context("job_evaluation", opportunity_id=42)

# Enrich with agent-specific data
for agent_name in ["krudi", "smriti", "parva", "rudi", "maya", "shanti"]:
    agent_context = jobs_db.enrich_agent_context(agent_name, context)
    context.update(agent_context)

# Ask Parliament
query = "Should I apply to Senior Python Engineer at TechCorp?"
decision, trace = parliament.deliberate(query, context)

print(f"Decision: {decision}")
print(f"Confidence: {trace.confidence:.1%}")
print(f"Active agents: {list(trace.activations.keys())}")

# Log decision for tracking
log_id = jobs_db.log_parliament_decision(trace, job_id=42)
print(f"Decision logged as #{log_id}")

# Later, after applying and getting outcome...
jobs_db.update_decision_outcome(log_id, {
    'applied': True,
    'callback': True,
    'interview': True,
    'offer': False,
    'notes': 'Made it to final round but no offer'
})

jobs_db.disconnect()
```

### 2. Interactive Shell

```bash
$ python3 examples/job_advisory_shell.py

╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║            🏛️  PARLIAMENT JOB ADVISORY SHELL                 ║
║                                                               ║
║         AI-Powered Career Guidance with Real Data            ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

Initializing...
✓ Connected to jobs database
✓ Parliament initialized (7 agents)

✓ Ready! Type 'help' for commands.

jobs> list 80
Jobs (score >= 80):
────────────────────────────────────────────────────────────────────────────
ID    Score   Company              Position                       Status
────────────────────────────────────────────────────────────────────────────
15    92      TechCorp             Senior Python Engineer         new
23    88      DataWorks            ML Engineer                    new
31    85      CloudInc             Backend Developer              new
────────────────────────────────────────────────────────────────────────────

jobs> show 15

Job #15:
──────────────────────────────────────────────────────────────────
Company: TechCorp
Position: Senior Python Engineer
Match Score: 92/100
Classification: new
Scraped: 2024-11-18

Tags/Skills:
  Python, FastAPI, PostgreSQL, Docker, AWS, REST APIs

Description:
  We're looking for a Senior Python Engineer to join our backend team...

URL: https://remoteok.com/remote-jobs/123456
──────────────────────────────────────────────────────────────────

jobs> advise 15

Consulting Parliament on Job #15:
──────────────────────────────────────────────────────────────────
TechCorp - Senior Python Engineer
Match Score: 92/100
──────────────────────────────────────────────────────────────────

Loading integration data...
✓ Loaded: 12 skills assessed, 45 interview questions, 8 learning gaps, 23 applications tracked

Parliament deliberating...

Agent Activations:
  Krudi      ████████████████████████░░░░░░ 0.825 (ACTIVE)
  Smriti     ██████████████████░░░░░░░░░░░░ 0.615 (passive)
  Parva      ███████████████████████░░░░░░░ 0.782 (ACTIVE)
  Rudi       ██████████████████████████░░░░ 0.891 (ACTIVE)
  Maya       ████████████████░░░░░░░░░░░░░░ 0.542 (passive)
  Shanti     ████████████████████░░░░░░░░░░ 0.638 (passive)
  Kshana     ██████████████████████████████ 1.000 (ACTIVE)

Agent Perspectives:
──────────────────────────────────────────────────────────────────

KRUDI:
  Your Python rating is 3.8/5 based on 12 interview questions.
  This is a strong foundation but the role requires senior-level expertise.
  Critical gap: PostgreSQL (rated 2.1/5) - high priority for this role.

PARVA:
  Your application trajectory shows steady upward movement.
  Similar senior roles: 2 applications in last 3 months.
  Success pattern: 50% callback rate for Python-focused positions.

RUDI:
  You're actively studying FastAPI (6 hours logged this week).
  This role aligns perfectly with your growth trajectory.
  Estimated time to readiness: Already prepared for 70% of requirements.

KSHANA'S SYNTHESIS:
──────────────────────────────────────────────────────────────────
This role presents a good opportunity with manageable risks. Your Python
skills are solid (3.8/5), and your current learning focus on FastAPI
directly supports this role. The PostgreSQL gap is notable but addressable.

Your historical pattern shows 50% success rate with similar roles, and
your upward trajectory indicates readiness for senior positions. The
remote nature aligns with your preferences (89% of applications are remote).

Recommendation: APPLY, but prioritize PostgreSQL study in parallel.
This role represents appropriate stretch growth within your capabilities.

──────────────────────────────────────────────────────────────────

✓ RECOMMENDATION: APPLY
Confidence: 85.4%

──────────────────────────────────────────────────────────────────

Decision Metrics:
  Confidence: 85.4%
  Dharmic Alignment: 78.9%
  Sparsity: 57.1%

✓ Decision logged as #47
Update outcome later with: log 47 <outcome>

jobs> log 47 callback

✓ Updated decision #47: callback = True

jobs> stats

PARLIAMENT ACCURACY REPORT
═══════════════════════════════════════════════

Total Decisions: 18
With Known Outcomes: 12

Overall Accuracy: 73.5%
  • Recommendation Followed: 83.3%
  • Callback Prediction: 75.0%

═══════════════════════════════════════════════
BY RECOMMENDATION TYPE
═══════════════════════════════════════════════

APPLY recommendations: 8
  Success rate: 75.0% (led to callback/interview/offer)

SKIP recommendations: 4
  Correct rate: 100.0% (avoided poor outcomes)

═══════════════════════════════════════════════
BY AGENT ACCURACY
═══════════════════════════════════════════════

Krudi (Reality):
  Accuracy: 81.8%
  Sample Size: 11 activations
  Activation Rate: 91.7%
  Avg Outcome: 1.82/3.0

Parva (Causality):
  Accuracy: 77.8%
  Sample Size: 9 activations
  Activation Rate: 75.0%
  Avg Outcome: 1.67/3.0

...

jobs> calibrate

Suggested Threshold Adjustments:
──────────────────────────────────────────────────────────────

Based on historical accuracy patterns

Krudi (Reality):
  INCREASE threshold by +0.05
  (agent over-active or inaccurate)

Rudi (Transformation):
  DECREASE threshold by -0.10
  (agent under-active or too conservative)

✓ All other agents well-calibrated!

jobs> quit

Goodbye! May your job search be successful. 🎯
```

### 3. Decision Tracking Workflow

```python
# 1. Get Parliament advice
decision, trace = parliament.deliberate(query, context)

# 2. Log the decision
log_id = jobs_db.log_parliament_decision(trace, job_id=42)

# 3. User applies (or doesn't)
# ...time passes...

# 4. Update with outcome
jobs_db.update_decision_outcome(log_id, {
    'applied': True,
    'callback': True,
    'interview': False,
    'offer': False,
    'notes': 'Got callback but declined interview due to salary'
})

# 5. Check accuracy
stats = jobs_db.get_decision_accuracy_stats()
print(f"Overall accuracy: {stats['accuracy']['overall_accuracy']:.1%}")

# 6. Get calibration suggestions
from src.integrations.validation import ParliamentValidator

validator = ParliamentValidator(jobs_db)
adjustments = validator.suggest_threshold_adjustments()

for agent, adjustment in adjustments.items():
    if adjustment != 0.0:
        print(f"{agent}: {adjustment:+.2f}")
```

## Validation & Accuracy

### Accuracy Metrics

The validation system tracks multiple accuracy dimensions:

1. **Overall Accuracy**: How well confidence matched outcomes
   ```
   outcome_score = (callback ? 1 : 0) + (interview ? 1 : 0) + (offer ? 1 : 0)
   normalized = outcome_score / 3.0
   accuracy = 1.0 - |confidence - normalized|
   ```

2. **Recommendation Following**: % of times user followed advice
   - High confidence (≥70%) → User applied
   - Low confidence (<50%) → User skipped

3. **Callback Prediction**: % of times callback prediction was correct
   - Predicted callback (confidence ≥70%)
   - Actual callback received

4. **By Confidence Level**:
   - HIGH (≥70%): Should lead to strong outcomes
   - MEDIUM (50-70%): Mixed outcomes expected
   - LOW (<50%): Should avoid poor outcomes

5. **By Agent**: Individual agent accuracy and activation patterns

### Calibration Process

The system suggests threshold adjustments based on:

**Criteria**:
- **Accuracy deviation** from ideal 70%
- **Activation rate** compared to ideal 60%
- **Outcome correlation** with agent participation

**Adjustment Logic**:
```python
if accuracy > 75% and activation_rate < 40%:
    # Too conservative - lower threshold
    adjustment = -0.10
elif accuracy < 60% and activation_rate > 70%:
    # Over-eager - raise threshold
    adjustment = +0.15
else:
    # Well calibrated
    adjustment = 0.0
```

**Application**:
Adjustments are capped at ±0.15 for stability. Apply manually or wait for automatic calibration in future versions.

### Continuous Improvement Loop

```
┌─────────────┐
│   Advice    │ ──── Parliament provides recommendation
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Action    │ ──── User applies (or doesn't)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Outcome   │ ──── Real-world result (callback, etc.)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Logging    │ ──── Outcome recorded in database
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Analysis   │ ──── Accuracy metrics calculated
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Calibration │ ──── Threshold adjustments suggested
└──────┬──────┘
       │
       └──────────► (Loop: Better advice next time)
```

## Future Enhancements

### Planned Features

1. **Real-time Calibration**
   - Automatic threshold application with user confirmation
   - A/B testing framework for threshold changes
   - Confidence interval tracking

2. **Multi-Project Tracking**
   - Support multiple job databases
   - Cross-project pattern recognition
   - Industry-specific calibration

3. **API Endpoints**
   - REST API for dashboard integration
   - WebSocket for real-time updates
   - GraphQL query interface

4. **Explainable AI Visualization**
   - Decision tree visualization
   - Agent contribution breakdown
   - Confidence calibration curves
   - Historical trend charts

5. **Advanced Analytics**
   - Temporal accuracy trends
   - Cohort analysis (by job type, company, etc.)
   - Skill gap impact analysis
   - ROI tracking (time saved, offers received)

6. **Automated Workflows**
   - Auto-apply to high-confidence opportunities
   - Scheduled decision reviews
   - Weekly accuracy reports
   - Learning plan generation

### Research Directions

1. **Causal Inference**
   - Counterfactual analysis: "What if I had applied?"
   - Treatment effect estimation
   - Propensity score matching

2. **Transfer Learning**
   - Learn from other users' anonymized data
   - Domain adaptation (tech → non-tech roles)
   - Few-shot learning for new job categories

3. **Multi-Agent Coordination**
   - Agent specialization discovery
   - Dynamic threshold adaptation
   - Meta-learning for threshold initialization

4. **Interpretability**
   - LIME/SHAP for decision explanations
   - Attention mechanism visualization
   - Reasoning chain extraction

## Best Practices

### For Developers

1. **Always use context managers**:
   ```python
   with JobsDBIntegration() as jobs_db:
       # Integration automatically connects and disconnects
       context = jobs_db.fetch_context("job_evaluation")
   ```

2. **Enrich context for all agents**:
   ```python
   for agent_name in jobs_db.get_supported_agents():
       context.update(jobs_db.enrich_agent_context(agent_name, context))
   ```

3. **Log all decisions**:
   ```python
   log_id = jobs_db.log_parliament_decision(trace, job_id=job_id)
   # Store log_id for later outcome tracking
   ```

4. **Update outcomes promptly**:
   - Record outcomes as soon as known
   - Include detailed notes for analysis
   - Track partial outcomes (applied but no callback yet)

5. **Review accuracy regularly**:
   ```python
   validator = ParliamentValidator(jobs_db)
   report = validator.generate_accuracy_report()
   print(report)  # Review weekly/monthly
   ```

### For Users

1. **Maintain accurate data**:
   - Rate interview questions honestly
   - Update application statuses promptly
   - Log learning sessions consistently

2. **Track outcomes diligently**:
   - Use `log` command after every outcome
   - Include notes on why outcomes occurred
   - Track rejections (learning opportunity)

3. **Review stats regularly**:
   - Run `stats` command weekly
   - Check `calibrate` monthly
   - Adjust behavior based on patterns

4. **Trust the process**:
   - Parliament learns from your data
   - More outcomes = better accuracy
   - Accuracy improves over time

## Troubleshooting

### Common Issues

**Issue**: `ConnectionError: Not connected to jobs database`
```python
# Solution: Ensure connect() is called
jobs_db = JobsDBIntegration()
if not jobs_db.connect():
    print("Check database path")
```

**Issue**: Empty accuracy stats
```bash
# Solution: Log more decision outcomes
jobs> log 1 callback
jobs> log 2 applied
# Need at least 10 outcomes for stats
```

**Issue**: Integration not found
```python
# Solution: Check relative path
import os
print(os.path.exists("../jobs-application-automation/data/jobs-tracker.db"))

# Or use absolute path
jobs_db = JobsDBIntegration(db_path="/full/path/to/jobs-tracker.db")
```

**Issue**: `parliament_decisions` table doesn't exist
```bash
# Solution: Run migration
cd jobs-application-automation
./scripts/apply_parliament_migration.sh
```

## Contributing

Contributions welcome! Areas of interest:

1. Additional integrations (Notion, Airtable, etc.)
2. Improved calibration algorithms
3. Visualization dashboards
4. Additional query types
5. Performance optimizations

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - See [LICENSE](LICENSE) for details.

## Support

- GitHub Issues: [Report bugs](https://github.com/anthropics/sacred-qa-audits/issues)
- Documentation: [Full docs](https://sacred-qa-audits.readthedocs.io)
- Discussions: [Community forum](https://github.com/anthropics/sacred-qa-audits/discussions)

---

**Next Steps**: See [SYMBIOTIC_ARCHITECTURE.md](SYMBIOTIC_ARCHITECTURE.md) for deep dive into the bidirectional learning philosophy and Krecosystem vision.
