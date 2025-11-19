# Job Advisory Shell - Interactive Parliament REPL

An interactive command-line interface for consulting the Kragentic Parliament on job hunting decisions, powered by real data from your job application tracking database.

## Features

### 🏛️ Parliament-Powered Advice
- Get AI-powered recommendations on job applications
- 7 specialized agents analyze each opportunity from different perspectives
- Data-grounded decisions based on your actual skills, interview history, and outcomes

### 📊 Real-Time Analytics
- View current skill levels from interview performance
- Track learning gaps and priorities
- Monitor Parliament decision accuracy
- Review application history and outcomes

### 🎯 Decision Tracking
- Every recommendation is logged for future analysis
- Update outcomes as they happen (applied, callback, interview, offer)
- Build a feedback loop for continuous improvement

## Installation & Setup

### Prerequisites

1. **Jobs Database** - Ensure `../jobs-application-automation/data/jobs-tracker.db` exists
2. **Migration** - Run Parliament decisions table migration:
   ```bash
   cd ../jobs-application-automation
   ./scripts/apply_parliament_migration.sh
   ```

### Launch the Shell

```bash
python3 examples/job_advisory_shell.py
```

## Commands

### Job Search

#### `list [min_score]`
List scraped jobs sorted by match score.

```
jobs> list 80
Jobs (score >= 80):
────────────────────────────────────────────────────────────────────────────────
ID    Score   Company              Position                       Status
────────────────────────────────────────────────────────────────────────────────
42    95      DataCorp            Senior Data Engineer           new
43    88      TechStart           ETL Developer                  new
44    82      BigData Inc         Data Analyst                   applied
```

**Default:** Shows jobs with score >= 70
**Example:** `list 90` - Show only jobs with 90+ score

---

#### `show <job_id>`
Show detailed information about a specific job.

```
jobs> show 42

Job #42:
──────────────────────────────────────────────────────────────────────────
Company: DataCorp
Position: Senior Data Engineer
Match Score: 95/100
Location: Remote
Salary: $120k-$160k
Classification: HIGH_FIT
Scraped: 2025-01-15

Tags/Skills:
  SQL, Python, ETL, Data Warehouse, Apache Airflow, PostgreSQL

Description:
  We're looking for a Senior Data Engineer to join our growing team...

URL: https://datacorp.com/jobs/senior-de
──────────────────────────────────────────────────────────────────────────
Use 'advise 42' to get Parliament recommendation
```

---

#### `advise <job_id>`
Consult the Kragentic Parliament for a recommendation on whether to apply.

```
jobs> advise 42

Consulting Parliament on Job #42:
──────────────────────────────────────────────────────────────────────────
DataCorp - Senior Data Engineer
Match Score: 95/100
──────────────────────────────────────────────────────────────────────────

Loading integration data...
✓ Loaded: 5 skills assessed, 12 interview questions, 3 learning gaps, 25 applications tracked

Parliament deliberating...

Agent Activations:
  Krudi      ████████████████████████████░░ 0.850 (ACTIVE)
  Smriti     ███████████████████████░░░░░░░ 0.720 (ACTIVE)
  Parva      ████████████████████░░░░░░░░░░ 0.680 (ACTIVE)
  Rudi       ████████░░░░░░░░░░░░░░░░░░░░░░ 0.280 (passive)
  Maya       ██████░░░░░░░░░░░░░░░░░░░░░░░░ 0.200 (passive)
  Shanti     ████░░░░░░░░░░░░░░░░░░░░░░░░░░ 0.150 (passive)
  Kshana     ██████████████████████████████ 1.000 (ACTIVE)

Agent Perspectives:
──────────────────────────────────────────────────────────────────────────

KRUDI:
  Reality-grounded skill gap analysis:
  - SQL: You rated 2.9/5, Role requires 4.0+/5 → Gap: 1.1 points
  - Data Warehouse: You rated 1.0/5, Role requires 3.5+/5 → Gap: 2.5 points
  ... (truncated)

SMRITI:
  Historical pattern analysis:
  - Past senior roles: 2/8 callbacks (25%)
  - Past mid-level roles: 12/25 callbacks (48%)
  - This role matches your weak areas (Data Warehouse)
  ... (truncated)

PARVA:
  Trajectory analysis:
  - Current level: Mid-level (2.5-3.0/5 avg)
  - Target level: Senior (4.0+/5 required)
  - Timeline gap: 6-12 months skill building needed
  ... (truncated)

KSHANA'S SYNTHESIS:
──────────────────────────────────────────────────────────────────────────
Decision supported with caution. Prerequisites: (1) strengthen Data Warehouse
to 3.0+/5, (2) improve SQL to 3.5+/5. Target mid-level roles with 48% callback
rate first. Re-evaluate senior roles in 6 months.

──────────────────────────────────────────────────────────────────────────

✗ RECOMMENDATION: SKIP
Confidence: 68.0%

──────────────────────────────────────────────────────────────────────────

Decision Metrics:
  Confidence: 68.0%
  Dharmic Alignment: 85.0%
  Sparsity: 71.4%

✓ Decision logged as #47
Update outcome later with: log 47 <outcome>
```

**Output includes:**
- Job summary
- Integration data loaded
- Agent activation visualization
- Key agent perspectives with reasoning
- Kshana's synthesized decision
- Color-coded recommendation (APPLY/CONSIDER/SKIP)
- Decision metrics
- Decision log ID for tracking

---

### Self-Assessment

#### `skills`
Show current skill levels calculated from interview performance.

```
jobs> skills

Current Skill Levels (from 12 interview questions):
──────────────────────────────────────────────────────────────────────────
ETL Tools            ████████████░░░░░░░░ 3.0/5  (1 question)
Technical SQL        ███████████░░░░░░░░░ 2.9/5  (7 questions)
Python               █████████░░░░░░░░░░░ 2.3/5  (3 questions)
Data Warehouse       ████░░░░░░░░░░░░░░░░ 1.0/5  (1 question)
──────────────────────────────────────────────────────────────────────────
```

**Color coding:**
- 🟢 Green (3.5+/5): Strong skills
- 🟡 Yellow (2.5-3.4/5): Moderate skills
- 🔴 Red (<2.5/5): Needs improvement

---

#### `gaps`
Show identified learning gaps ordered by priority.

```
jobs> gaps

Learning Gaps (5 identified):
──────────────────────────────────────────────────────────────────────────

1. [CRITICAL] Data Warehouse Concepts (Priority: 5)
   Category: Data Warehouse
   Status: Not Started
   Estimated: 12 hours

2. [CRITICAL] Advanced SQL - Window Functions (Priority: 5)
   Category: SQL
   Status: In Progress
   Estimated: 15 hours

3. [HIGH] Pytest Framework (Priority: 4)
   Category: Python
   Status: Not Started
   Estimated: 15 hours
──────────────────────────────────────────────────────────────────────────
```

---

### Decision Tracking

#### `history [limit]`
Show past Parliament decisions with outcomes.

```
jobs> history 5

Parliament Decision History:
──────────────────────────────────────────────────────────────────────────

#47 | 2025-01-15 | Should I apply to Google Senior DE?
     Decision: SKIP (Confidence: 82%)
     Outcome: Not applied / No outcome recorded

#46 | 2025-01-14 | Should I apply to Startup ETL role?
     Decision: APPLY (Confidence: 78%)
     Outcome: Applied → Callback → Interview

#45 | 2025-01-13 | Should I apply to Amazon Data Engineer?
     Decision: CONSIDER (Confidence: 65%)
     Outcome: Applied → No response yet
──────────────────────────────────────────────────────────────────────────
```

**Default:** Shows last 10 decisions
**Example:** `history 20` - Show last 20 decisions

---

#### `stats`
Show Parliament accuracy statistics (when sufficient outcome data available).

```
jobs> stats

Parliament Accuracy Statistics:
──────────────────────────────────────────────────────────────────────────

Overall:
  Total decisions: 25
  With outcomes: 15

By Confidence Level:
  High         8 decisions   87.5% accurate
  Medium       5 decisions   60.0% accurate
  Low          2 decisions   50.0% accurate

By Agent:
  Krudi       15 activations   86.7% accurate
  Smriti      12 activations   83.3% accurate
  Parva       10 activations   80.0% accurate
  Kshana      15 activations   86.7% accurate
──────────────────────────────────────────────────────────────────────────
```

---

#### `log <log_id> <outcome>`
Update a decision's outcome to build accuracy tracking.

```
jobs> log 47 callback
✓ Updated decision #47: callback = True
```

**Valid outcomes:**
- `applied` - You applied to the job
- `callback` - Got a response/callback
- `interview` - Got an interview
- `offer` - Received an offer

**Cascading:** Higher outcomes automatically set lower ones:
- `offer` → sets applied, callback, interview, offer
- `interview` → sets applied, callback, interview
- `callback` → sets applied, callback

---

### System

#### `help`
Show all available commands with examples.

#### `quit` / `exit`
Close the shell and disconnect from database.

## Workflow Example

### Daily Job Hunting Session

```bash
# Launch shell
python3 examples/job_advisory_shell.py

# Check new jobs
jobs> list 85

# Review a promising job
jobs> show 52

# Get Parliament recommendation
jobs> advise 52

# Decision: APPLY (Confidence: 82%)
# ✓ Decision logged as #53

# Apply to the job (outside shell)
# ...

# Update outcome when you get response
jobs> log 53 callback

# Check learning priorities
jobs> gaps

# Review your skill progress
jobs> skills

# Check how accurate Parliament has been
jobs> stats

# Done for the day
jobs> quit
```

## Tips & Best Practices

### 🎯 For Best Results

1. **Keep Data Updated**
   - Log interview questions and ratings regularly
   - Update study topics and learning progress
   - Track all applications in the database

2. **Trust the Numbers**
   - Parliament's confidence reflects real data
   - High confidence (70%+) recommendations are well-grounded
   - Low confidence (<50%) means insufficient data or poor match

3. **Update Outcomes Promptly**
   - Log outcomes as they happen: `log <id> <outcome>`
   - This improves Parliament's accuracy over time
   - Enables threshold calibration for better future recommendations

4. **Review Patterns**
   - Use `history` to spot trends
   - Use `stats` to validate Parliament accuracy
   - Adjust your strategy based on what's working

### 🚀 Advanced Usage

**Filter jobs precisely:**
```bash
jobs> list 95  # Only show exceptional matches
```

**Focus on specific skills:**
```bash
jobs> skills   # Identify weakest areas
jobs> gaps     # See what to study next
```

**Track decision quality:**
```bash
jobs> stats    # See which agents are most accurate
```

## Color Coding

The shell uses colors to help you quickly assess information:

- 🟢 **Green** - Positive (APPLY, high scores, strong skills)
- 🟡 **Yellow** - Moderate (CONSIDER, medium confidence)
- 🔴 **Red** - Negative (SKIP, critical gaps, low scores)
- 🔵 **Cyan** - Informational (headings, separators)
- ⚫ **Dim** - Secondary info (metadata, timestamps)

## Troubleshooting

### "Failed to connect to database"
**Solution:** Ensure `../jobs-application-automation/data/jobs-tracker.db` exists.

### "No jobs found with score >= 70"
**Solution:** Lower the threshold: `list 50` or populate the database with scraped jobs.

### "Could not log decision"
**Solution:** Run the Parliament migration:
```bash
cd ../jobs-application-automation
./scripts/apply_parliament_migration.sh
```

### Commands not working
**Solution:** Check that you're in the correct directory and all dependencies are installed.

## Architecture

The shell integrates three key components:

1. **JobsDBIntegration** - Connects to jobs-tracker.db for real data
2. **KragenticParliament** - 7-agent decision system
3. **Decision Logging** - Tracks advice → outcomes for learning

```
┌─────────────────────────────────────────────────┐
│          Job Advisory Shell (REPL)              │
│                                                 │
│  Commands: list, show, advise, skills, gaps... │
└────────────────┬────────────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
┌───────▼──────┐   ┌──────▼──────────┐
│  Parliament  │   │  Jobs Database  │
│              │   │                 │
│  7 Agents:   │   │  • scraped_jobs │
│  - Krudi     │◄──┤  • interview_q  │
│  - Smriti    │   │  • study_topics │
│  - Parva     │   │  • parliament_  │
│  - Rudi      │   │    decisions    │
│  - Maya      │   └─────────────────┘
│  - Shanti    │
│  - Kshana    │
└──────┬───────┘
       │
       ▼
  Decision Trace
  (logged → outcomes → accuracy → calibration)
```

## Data Sources

Parliament recommendations are grounded in:

- **Interview Questions** - Your ratings on past technical questions
- **Application History** - Success rates by company type, role, etc.
- **Learning Progress** - Study topics, gaps, confidence trends
- **Decision Outcomes** - What happened when you followed advice

All data comes from `jobs-tracker.db` - the more data you track, the better the advice!

## Future Enhancements

Planned features:
- [ ] `apply <job_id>` - Mark as applied directly from shell
- [ ] `search <keyword>` - Full-text search across jobs
- [ ] `compare <id1> <id2>` - Side-by-side job comparison
- [ ] `export` - Export decisions to CSV for analysis
- [ ] `calibrate` - Run agent threshold calibration
- [ ] Tab completion for commands
- [ ] Command history (up/down arrows)

## Contributing

This shell is part of the sacred-qa-audits project's symbiotic integration system. See the main README for contribution guidelines.

## License

Part of the sacred-qa-audits project.

---

**Built with:** Python 3, SQLite, Kragentic Parliament
**Status:** Production-ready
**Version:** 1.0.0
