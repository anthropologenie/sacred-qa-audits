# Parliament Validation Integration

## Overview

This document describes the Parliament validation and accuracy tracking system that enables measuring Parliament's historical accuracy and suggesting threshold calibration adjustments.

## Components Created

### 1. `src/integrations/validation.py`

**Class: `ParliamentValidator`**

A comprehensive validation and calibration system for the Kragentic Parliament.

#### Key Methods:

##### `calculate_accuracy_metrics() -> Dict[str, Any]`

Calculates detailed accuracy metrics from historical Parliament decisions:

- **Overall Accuracy**: Combined accuracy metric based on confidence vs. outcomes
- **Recommendation Following**: % of times user followed Parliament's advice
- **Callback Prediction**: % of times callback prediction was correct
- **By Recommendation Type**:
  - APPLY: Success rate when Parliament recommended applying
  - SKIP: Correct rate when Parliament recommended skipping
- **By Confidence Level**:
  - HIGH (≥70%): Accuracy and average outcome
  - MEDIUM (50-70%): Accuracy and average outcome
  - LOW (<50%): Accuracy and average outcome
- **By Agent**:
  - Per-agent accuracy rates
  - Activation rates
  - Sample sizes
  - Average outcomes

##### `generate_accuracy_report() -> str`

Generates a human-readable accuracy report with:
- Total decisions and outcomes
- Overall accuracy percentages
- Breakdown by recommendation type
- Breakdown by confidence level
- Agent-specific accuracy metrics
- Calibration status and recommendations

Example output:
```
PARLIAMENT ACCURACY REPORT
═══════════════════════════════════════════════

Total Decisions: 25
With Known Outcomes: 18

Overall Accuracy: 73.5%
  • Recommendation Followed: 82.3%
  • Callback Prediction: 70.6%

═══════════════════════════════════════════════
BY RECOMMENDATION TYPE
═══════════════════════════════════════════════

APPLY recommendations: 12
  Success rate: 75.0% (led to callback/interview/offer)

SKIP recommendations: 6
  Correct rate: 83.3% (avoided poor outcomes)

...
```

##### `suggest_threshold_adjustments() -> Dict[str, float]`

Analyzes accuracy patterns and suggests threshold adjustments:

- **Too Conservative** (high accuracy, low activation): Suggests lowering threshold (-0.05 to -0.15)
- **Too Optimistic** (low accuracy, high activation): Suggests raising threshold (+0.05 to +0.15)
- **Well Calibrated**: No adjustment (0.0)

Returns dictionary mapping agent names to suggested adjustments:
```python
{
    'krudi': +0.05,   # Slightly over-active
    'smriti': -0.10,  # Too conservative
    'parva': 0.0,     # Well calibrated
    ...
}
```

### 2. Integration with `job_advisory_shell.py`

#### Updated `stats` Command

The existing `stats` command now uses `ParliamentValidator` to generate comprehensive reports:

```python
def cmd_stats(self, args: List[str]):
    """Show Parliament accuracy statistics."""
    validator = ParliamentValidator(self.jobs_db)
    report = validator.generate_accuracy_report()
    print(report)
```

#### New `calibrate` Command

Provides threshold adjustment suggestions:

```bash
jobs> calibrate

Suggested Threshold Adjustments:
──────────────────────────────────────────────────────────

Krudi (Reality):
  INCREASE threshold by +0.05
  (agent over-active or inaccurate)

Smriti (Memory):
  DECREASE threshold by -0.10
  (agent under-active or too conservative)

✓ All other agents well-calibrated!
```

### 3. Test Suite

Created `tests/test_validation.py` with comprehensive tests:

- ✓ Validator initialization with connected/disconnected DB
- ✓ Accuracy calculation with no outcomes
- ✓ Report generation with no data
- ✓ Threshold adjustment suggestions with no data
- ✓ Decision accuracy scoring (perfect match)
- ✓ Decision accuracy scoring (mismatches)

**All tests passing**: 7/7 ✓

## Usage Examples

### In the Job Advisory Shell

1. **View Accuracy Report**:
   ```bash
   jobs> stats
   ```
   Shows comprehensive accuracy metrics for Parliament decisions.

2. **Get Calibration Suggestions**:
   ```bash
   jobs> calibrate
   ```
   Analyzes historical data and suggests threshold adjustments.

3. **Log Decision Outcomes** (for tracking):
   ```bash
   jobs> log 15 callback    # Record that decision #15 led to callback
   jobs> log 16 interview   # Record interview outcome
   jobs> log 17 offer       # Record offer received
   ```

### Programmatic Usage

```python
from src.integrations.jobs_db_integration import JobsDBIntegration
from src.integrations.validation import ParliamentValidator

# Connect to database
jobs_db = JobsDBIntegration()
jobs_db.connect()

# Create validator
validator = ParliamentValidator(jobs_db)

# Get metrics
metrics = validator.calculate_accuracy_metrics()
print(f"Overall accuracy: {metrics['accuracy']['overall_accuracy']:.1%}")

# Get report
report = validator.generate_accuracy_report()
print(report)

# Get calibration suggestions
adjustments = validator.suggest_threshold_adjustments()
for agent, adjustment in adjustments.items():
    if adjustment != 0.0:
        print(f"{agent}: {adjustment:+.2f}")
```

## Database Schema

The validation system uses the `parliament_decisions` table:

```sql
CREATE TABLE parliament_decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    decision_id TEXT UNIQUE NOT NULL,
    timestamp TEXT NOT NULL,
    query TEXT NOT NULL,
    job_id INTEGER,
    agents_active TEXT,          -- JSON array of active agents
    decision_text TEXT,
    sparsity REAL,
    confidence REAL,
    dharmic_alignment REAL,
    integration_used INTEGER,

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

## Accuracy Calculation Methodology

### Decision Accuracy Score

For each decision, accuracy is calculated as:

```
outcome_score = (callback ? 1 : 0) + (interview ? 1 : 0) + (offer ? 1 : 0)
normalized_outcome = outcome_score / 3.0
accuracy = 1.0 - |confidence - normalized_outcome|
```

This measures how well Parliament's confidence matched the actual outcome:
- High confidence + strong outcome = high accuracy
- Low confidence + weak outcome = high accuracy
- Mismatch = low accuracy

### Threshold Adjustment Logic

Adjustments are suggested based on:

1. **Accuracy Deviation**: How far from ideal 70% accuracy
2. **Activation Rate**: How often the agent activates (ideal ~60%)

Rules:
- High accuracy (>75%) + low activation (<40%) → Decrease threshold (encourage participation)
- Low accuracy (<60%) + high activation (>70%) → Increase threshold (reduce noise)
- Well-balanced → No adjustment

Adjustments are capped at ±0.15 for stability.

## Future Enhancements

1. **Automatic Threshold Application**: Auto-apply suggested adjustments with user confirmation
2. **Temporal Analysis**: Track accuracy trends over time
3. **Per-Domain Calibration**: Different thresholds for different job types
4. **Confidence Calibration Curves**: Detailed calibration analysis
5. **A/B Testing**: Test threshold changes against control group
6. **Export Reports**: Generate PDF/HTML accuracy reports

## Files Modified/Created

**Created**:
- `src/integrations/validation.py` (208 lines)
- `tests/test_validation.py` (104 lines)
- `examples/VALIDATION_INTEGRATION.md` (this file)

**Modified**:
- `src/integrations/__init__.py` - Added ParliamentValidator export
- `examples/job_advisory_shell.py` - Added `calibrate` command, updated `stats` command

## Key Features

✓ Comprehensive accuracy tracking across multiple dimensions
✓ Human-readable reports with actionable insights
✓ Intelligent threshold calibration suggestions
✓ Full test coverage
✓ Integration with existing job advisory shell
✓ Database-backed historical analysis
✓ Sparsity and diversity metrics
✓ Per-agent accuracy breakdown
✓ Confidence level analysis
✓ Recommendation type analysis

## Conclusion

The Parliament validation system provides a robust framework for:
1. **Measuring** Parliament's historical accuracy
2. **Understanding** which agents perform well in which scenarios
3. **Improving** decision quality through data-driven threshold calibration
4. **Tracking** the training loop: Advice → Action → Outcome → Learning

This completes the symbiotic integration between sacred-qa-audits and jobs-application-automation, enabling Parliament to learn from real-world outcomes and continuously improve its job hunting advice.
