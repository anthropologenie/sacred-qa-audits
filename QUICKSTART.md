# Quick Start Guide - Parliament Job Advisory

Get started with the Kragentic Parliament job advisory system in 5 minutes.

## Prerequisites

```bash
# Ensure you have the jobs database
ls ../jobs-application-automation/data/jobs-tracker.db

# If missing, create it first using jobs-application-automation setup
```

## Step 1: Run Migration (One-time setup)

```bash
cd ../jobs-application-automation
./scripts/apply_parliament_migration.sh
cd -
```

**Expected output:**
```
✅ Migration applied successfully
✓ Table 'parliament_decisions' verified
```

## Step 2: Try the Demo

### Option A: Run all scenarios

```bash
python3 examples/job_advisory_demo.py --non-interactive
```

### Option B: Run specific scenario

```bash
# High-match job
python3 examples/job_advisory_demo.py --scenario A

# Skill-gap analysis
python3 examples/job_advisory_demo.py --scenario B

# Learning transformation (Rudi)
python3 examples/job_advisory_demo.py --scenario D

# Full Parliament (all 7 agents)
python3 examples/job_advisory_demo.py --scenario G
```

**What you'll see:**
- Integration data loading
- Agent activations
- Multi-perspective analysis
- Final recommendation with confidence
- Decision logged to database

## Step 3: Use the Interactive Shell

```bash
python3 examples/job_advisory_shell.py
```

**Try these commands:**

```bash
# See all commands
jobs> help

# View your skills
jobs> skills

# View learning gaps
jobs> gaps

# List high-scoring jobs
jobs> list 80

# Get advice on a specific job
jobs> show 1
jobs> advise 1

# View decision history
jobs> history

# Check accuracy stats
jobs> stats

# Exit
jobs> quit
```

## Step 4: Build Your Data

The more data you track, the better Parliament's advice becomes.

### Add Interview Questions

```sql
-- In jobs-tracker.db
INSERT INTO interview_questions (
    opportunity_id, question_text, question_type,
    difficulty, my_rating, learned
) VALUES (
    1, 'Explain SQL window functions', 'Technical SQL',
    'Hard', 2.5, 1
);
```

### Track Learning Sessions

```sql
INSERT INTO learning_sessions (
    topic_id, duration_minutes, what_was_learned,
    confidence_before, confidence_after, session_date
) VALUES (
    1, 90, 'Window functions: ROW_NUMBER, RANK, DENSE_RANK',
    2.0, 3.5, '2025-01-15'
);
```

### Update Decision Outcomes

```bash
# In the shell
jobs> advise 42
# ✓ Decision logged as #53

# ... apply to job ...

# When you get callback:
jobs> log 53 callback

# When you get interview:
jobs> log 53 interview
```

## Step 5: Monitor Progress

### Check Accuracy Over Time

```bash
jobs> stats

Parliament Accuracy Statistics:
  Total decisions: 15
  High confidence: 87.5% accurate
  Medium confidence: 60.0% accurate
```

### Review Patterns

```bash
jobs> history 10

#15 | 2025-01-15 | Should I apply to Startup ETL?
     Decision: APPLY (78% confidence)
     Outcome: Applied → Callback → Interview

#14 | 2025-01-14 | Should I apply to Google Senior?
     Decision: SKIP (82% confidence)
     Outcome: Not applied
```

## Common Workflows

### Morning Routine: Check New Jobs

```bash
jobs> list 85           # High-quality jobs only
jobs> show 42           # Review details
jobs> advise 42         # Get recommendation
```

### Evening Routine: Update Outcomes

```bash
jobs> history 5         # Recent decisions
jobs> log 53 callback   # Got response!
jobs> log 52 interview  # Scheduled interview
```

### Weekly Review: Assess Progress

```bash
jobs> skills            # Current skill levels
jobs> gaps              # What to study next
jobs> stats             # How accurate has Parliament been?
```

## Tips for Best Results

### 🎯 Get Better Recommendations

1. **Keep interview data current** - Log ratings after each interview
2. **Track all applications** - Even rejections provide valuable data
3. **Update learning progress** - Parliament sees your growth trajectory
4. **Log decision outcomes** - Builds the training loop

### 📊 Interpret Confidence Levels

- **70-100%:** High confidence - well-grounded in your data
- **50-70%:** Medium confidence - some data, but gaps exist
- **0-50%:** Low confidence - insufficient data or poor match

### 🚀 Maximize Accuracy

1. **Apply to recommended jobs** - High confidence APPLY = good odds
2. **Skip low-confidence matches** - Save time, focus on good fits
3. **Study identified gaps** - Parliament knows what's holding you back
4. **Track everything** - More data = better advice

## Troubleshooting

### "Failed to connect to database"

```bash
# Check database exists
ls ../jobs-application-automation/data/jobs-tracker.db

# If missing, initialize jobs-application-automation first
```

### "No jobs found"

```bash
# Lower the threshold
jobs> list 50

# Or populate database with scraped jobs
# (use jobs-application-automation scraper)
```

### "Could not log decision"

```bash
# Run the migration
cd ../jobs-application-automation
./scripts/apply_parliament_migration.sh
```

### Tests failing

```bash
# Fix relative imports
cd sacred-qa-audits
python3 -m pytest tests/test_integration.py -v

# If still failing, check Python version
python3 --version  # Should be 3.8+
```

## Next Steps

Once you're comfortable:

1. **Daily Usage** - Make the shell part of your job search routine
2. **Data Accumulation** - Aim for 50+ decisions with outcomes
3. **Threshold Calibration** - Coming soon: automatic agent tuning
4. **Feedback Loop** - Watch Parliament improve over time

## Getting Help

- **Commands:** Type `help` in the shell
- **Shell Guide:** `examples/README_SHELL.md`
- **Implementation:** `IMPLEMENTATION_SUMMARY.md`
- **Tests:** `python3 -m pytest tests/ -v`

## Architecture Quick Reference

```
You → Shell → Parliament → Decision
                  ↓
            Integration
                  ↓
            Jobs Database
                  ↓
        (interview_questions, study_topics, applications)
                  ↓
            Data-Grounded Advice
                  ↓
        You apply → Outcome
                  ↓
        Log outcome → Accuracy stats
                  ↓
        Improved recommendations
```

## Files to Know

- `examples/job_advisory_shell.py` - Interactive REPL
- `examples/job_advisory_demo.py` - 7 scenario demos
- `src/integrations/jobs_db_integration.py` - Core integration
- `tests/test_integration.py` - Integration tests

## Success Metrics

After 1 week:
- [ ] 10+ decisions logged
- [ ] 5+ outcomes tracked
- [ ] Accuracy stats available

After 1 month:
- [ ] 50+ decisions logged
- [ ] 25+ outcomes tracked
- [ ] Clear pattern of success/failure
- [ ] Ready for threshold calibration

## You're Ready! 🚀

The system is production-ready. Start using it daily, track your outcomes, and watch Parliament get smarter about your career!

```bash
# Start now:
python3 examples/job_advisory_shell.py
```

---

**Version:** 1.0.0
**Status:** Production-Ready ✅
**Last Updated:** November 2025
