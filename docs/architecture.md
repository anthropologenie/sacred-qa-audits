# Sacred QA Audits - Architecture Documentation

## Table of Contents

1. [Overview](#overview)
2. [Three-Layer Architecture](#three-layer-architecture)
3. [Circuit Tracing Mechanism](#circuit-tracing-mechanism)
4. [Sparsity Principle](#sparsity-principle)
5. [Dharmic Validation Logic](#dharmic-validation-logic)
6. [Example Decision Flow](#example-decision-flow)
7. [Design Principles](#design-principles)

---

## Overview

Sacred QA Audits implements a **parliamentary multi-agent decision-making system** where specialized agents deliberate on queries through an activation-based mechanism. The system traces all activations, maintains decision lineages, and validates decisions against dharmic (proper flow) principles.

### Key Concepts

- **Sparse Activation**: Only relevant agents activate for a given query
- **Circuit Tracing**: All decision pathways are recorded for auditability
- **Dharmic Alignment**: Decisions follow proper ordering principles
- **Kshana Synthesis**: The moment of decision collapse where possibilities become actuality

---

## Three-Layer Architecture

The system is organized into three distinct layers, each with specific responsibilities:

```
┌─────────────────────────────────────────────────────────────┐
│                    PARLIAMENT LAYER                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │         KragenticParliament                            │ │
│  │  • Orchestrates multi-agent deliberation               │ │
│  │  • Manages activation flow                             │ │
│  │  • Computes dharmic alignment                          │ │
│  │  • Maintains decision history                          │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      AGENT LAYER                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Krudi   │  │  Parva   │  │  Shanti  │  │   Rudi   │   │
│  │ Reality  │  │Temporal  │  │Equilib-  │  │Transform │   │
│  │Grounding │  │Causality │  │  rium    │  │ -ation   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│  │  Kshana  │  │   Maya   │  │  Smriti  │                 │
│  │Synthesis │  │Simulation│  │  Memory  │                 │
│  └──────────┘  └──────────┘  └──────────┘                 │
│                                                             │
│  Each agent:                                                │
│  • Computes activation strength (0.0-1.0)                  │
│  • Deliberates if above threshold                          │
│  • Fires specialized circuits                              │
│  • Extracts relevant context                               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                     CIRCUIT LAYER                            │
│  ┌────────────────────────────────────────────────────────┐ │
│  │         CircuitActivation                              │ │
│  │  • Agent name                                          │ │
│  │  • Activation strength                                 │ │
│  │  • Circuits fired                                      │ │
│  │  • Timestamp                                           │ │
│  │  • Context snapshot                                    │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │         ParliamentDecisionTrace                        │ │
│  │  • Decision ID (UUID)                                  │ │
│  │  • Kshana index (decision moment)                      │ │
│  │  • All agent activations                               │ │
│  │  • Sparsity ratio                                      │ │
│  │  • Dharmic alignment score                             │ │
│  │  • Pattern flags                                       │ │
│  │  • Lineage path                                        │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Layer Responsibilities

#### 1. Circuit Layer (`src/circuits/`)

**Purpose**: Provides data structures for tracking activations and decisions.

- `CircuitActivation`: Records a single agent's activation event
  - Timestamp when activation occurred
  - Strength of activation (0.0-1.0)
  - Which circuits fired
  - Contextual snapshot

- `ParliamentDecisionTrace`: Records the complete decision process
  - All agent activations
  - Activation sequence
  - Metrics (sparsity, confidence, dharmic alignment)
  - Pattern flags and lineage

**Key Feature**: Immutable record-keeping for auditability and learning.

#### 2. Agent Layer (`src/agents/`)

**Purpose**: Specialized agents that process queries through activation-based deliberation.

Each agent implements:
- `_compute_activation()`: Determines relevance to query (0.0-1.0)
- `_deliberate()`: Performs reasoning if activated
- `_extract_context()`: Extracts domain-relevant context

**Seven Agents**:

| Agent | Role | Key Circuits |
|-------|------|--------------|
| **Krudi** | Reality grounding, embodied constraints | `reality_anchor`, `embodied_grounding`, `sovereignty_alignment` |
| **Parva** | Temporal causality, consequences | `consequence_modeling`, `ripple_analysis`, `temporal_flow` |
| **Shanti** | Equilibrium, conflict resolution | `stability_check`, `conflict_resolution`, `balance_restore` |
| **Rudi** | Transformation, adaptation | `adaptation_pathway`, `learning_update`, `mutation_trigger` |
| **Kshana** | Presence, synthesis (ALWAYS active) | `synthesis`, `decision_collapse`, `presence_anchor` |
| **Maya** | Simulation, forward modeling | `forward_model`, `scenario_generation`, `possibility_space` |
| **Smriti** | Memory, pattern recognition | `history_retrieval`, `pattern_recognition`, `lineage_trace` |

**Activation Threshold**: Each agent has a threshold (default 0.3) that must be exceeded to engage in deliberation.

#### 3. Parliament Layer (`src/parliament/`)

**Purpose**: Orchestrates multi-agent deliberation and validates decision quality.

The `KragenticParliament` class:
- Manages all seven agents
- Coordinates deliberation flow
- Measures conflict between agents
- Computes dharmic alignment
- Detects problematic patterns
- Maintains decision history

---

## Circuit Tracing Mechanism

Circuit tracing provides **complete auditability** of the decision-making process. Every activation is recorded with full context.

### How It Works

```
Query: "Should we build feature X?"
         ↓
    ┌────────────────────────────┐
    │  1. Query sent to agents   │
    └────────────────────────────┘
         ↓
    ┌────────────────────────────┐
    │  2. Each agent computes    │
    │     activation strength    │
    └────────────────────────────┘
         ↓
    ┌────────────────────────────┐
    │  3. If above threshold:    │
    │     • Fire circuits        │
    │     • Perform deliberation │
    │     • Extract context      │
    └────────────────────────────┘
         ↓
    ┌────────────────────────────┐
    │  4. Record activation:     │
    │     • Timestamp            │
    │     • Strength             │
    │     • Circuits fired       │
    │     • Context snapshot     │
    └────────────────────────────┘
         ↓
    ┌────────────────────────────┐
    │  5. Build decision trace   │
    │     with all activations   │
    └────────────────────────────┘
```

### CircuitActivation Record

Each activation creates an immutable record:

```python
CircuitActivation(
    agent_name="krudi",
    activation_strength=0.75,
    circuits_fired=["reality_anchor", "embodied_grounding"],
    timestamp=datetime(2024, 11, 17, 14, 30, 45),
    context={
        "has_decision_language": True,
        "has_speculation_language": False,
        "resources": {...}
    }
)
```

### ParliamentDecisionTrace

The complete decision creates a comprehensive trace:

```python
ParliamentDecisionTrace(
    decision_id="6f0f71cf-40e8-4a2b-9e31-da2b58cde796",
    kshana_index=42,  # 42nd decision
    query="Should we build feature X?",
    activations={
        "krudi": CircuitActivation(...),
        "maya": CircuitActivation(...),
        "kshana": CircuitActivation(...)
    },
    sparsity_ratio=0.57,  # 57% of agents inactive
    total_activation=2.85,
    activation_sequence=["krudi", "maya", "parva", "kshana"],
    confidence=0.78,
    dharmic_alignment=0.95,
    pattern_flags=["UNGROUNDED_SIMULATION"],
    lineage_path=["krudi.reality_anchor", "kshana.synthesis"]
)
```

### Benefits of Circuit Tracing

1. **Auditability**: Every decision can be reconstructed
2. **Learning**: Patterns emerge from historical traces
3. **Debugging**: Identify why decisions were made
4. **Transparency**: Full visibility into reasoning process
5. **Evolution**: System can learn from past decisions

---

## Sparsity Principle

**Sparsity** is the core activation principle: **only relevant agents should activate for a given query**.

### Why Sparsity Matters

- **Efficiency**: Don't waste computation on irrelevant perspectives
- **Clarity**: Too many voices create noise, not wisdom
- **Signal Detection**: High-activation agents signal true relevance
- **Biological Inspiration**: Neural networks use sparse activation for efficiency

### Computing Sparsity

```python
sparsity_ratio = 1.0 - (active_agents / total_agents)
```

Where:
- `active_agents` = agents with activation ≥ threshold
- `total_agents` = all agents in parliament (excluding Kshana)

### Sparsity Interpretation

| Sparsity Ratio | Interpretation | Typical Meaning |
|----------------|----------------|-----------------|
| **0.0 - 0.3** | Low sparsity | Many agents engaged - complex query |
| **0.3 - 0.7** | Balanced | Healthy engagement level |
| **0.7 - 1.0** | High sparsity | Few agents engaged - specialized query |

### Example Scenarios

#### Low Sparsity (0.17 - Many Agents Active)

```
Query: "Should we implement decentralized governance?"

Active agents: Krudi, Parva, Rudi, Maya, Smriti (5/6)
Sparsity: 0.17

Why? This query touches multiple domains:
  • Krudi: Implementation reality
  • Parva: Long-term consequences
  • Rudi: Organizational transformation
  • Maya: Governance models
  • Smriti: Historical precedents
```

#### High Sparsity (0.83 - Few Agents Active)

```
Query: "What color should the button be?"

Active agents: Krudi (1/6)
Sparsity: 0.83

Why? Simple, grounded decision:
  • Krudi: Practical implementation detail
  • Others: Not relevant to this query
```

### Pattern Flags Related to Sparsity

The parliament detects and flags sparsity issues:

- **LOW_SPARSITY** (< 0.3): "Too many agents - decision may be overly complex"
- **HIGH_SPARSITY** (> 0.8): "Too few agents - decision may lack perspective"

### Adaptive Thresholds

Each agent has its own activation threshold:

```python
krudi.activation_threshold = 0.3   # Moderate
shanti.activation_threshold = 0.3  # Moderate
kshana.activation_threshold = 0.0  # ALWAYS activates
```

This allows fine-tuning of sparsity behavior per agent.

---

## Dharmic Validation Logic

**Dharmic alignment** measures whether the decision followed proper principles of flow and ordering. It's a quality score for the decision process itself.

### Etymology

"Dharma" (Sanskrit: धर्म) refers to the natural order, proper conduct, and cosmic law. In this system, it means **decisions should follow proper ordering principles**.

### Core Dharmic Principles

The system validates four key principles:

#### 1. Synthesis Last (Kshana Finality)

**Principle**: Kshana must synthesize at the end, never in the middle.

**Why**: Decision collapse is the final step - you can't synthesize before gathering perspectives.

**Validation**:
```python
if trace.activation_sequence[-1] == "kshana":
    alignment_score += 1.0  # ✓ Proper ordering
```

#### 2. Grounding Before Simulation (Krudi → Maya)

**Principle**: If both Krudi and Maya activate, Krudi should come first.

**Why**: Ground plans in reality before simulating futures. Ungrounded simulation leads to fantasy.

**Validation**:
```python
if krudi_active and maya_active:
    krudi_idx = trace.activation_sequence.index("krudi")
    maya_idx = trace.activation_sequence.index("maya")
    if krudi_idx < maya_idx:
        alignment_score += 1.0  # ✓ Grounding before speculation
```

**Pattern Flag**: If violated → `UNGROUNDED_SIMULATION`

#### 3. Equilibrium When Needed (Shanti on Conflict)

**Principle**: When agent conflict is high (conflict_score > 0.6), Shanti should activate.

**Why**: High disagreement requires mediation and balance restoration.

**Validation**:
```python
conflict_score = measure_conflict(trace)
if conflict_score > 0.6:
    if shanti_active:
        alignment_score += 1.0  # ✓ Equilibrium restored
```

**Pattern Flag**: If violated → `UNRESOLVED_CONFLICT`

#### 4. Memory Informs Transformation (Smriti + Rudi)

**Principle**: When Rudi (transformation) activates, Smriti (memory) should provide context.

**Why**: Transformation without historical awareness repeats past mistakes.

**Validation**:
```python
if rudi_active:
    if smriti_active:
        alignment_score += 1.0  # ✓ History informs change
    else:
        alignment_score += 0.5  # ○ Acceptable but not ideal
```

**Pattern Flag**: If violated → `AHISTORICAL_TRANSFORMATION`

### Dharmic Alignment Score

The final score is computed as:

```python
dharmic_alignment = alignment_score / checks_performed
```

Where `checks_performed` is the number of applicable principles (1-4).

### Interpreting Alignment Scores

| Score | Status | Meaning |
|-------|--------|---------|
| **0.80 - 1.00** | ✓ EXCELLENT | Proper dharmic flow |
| **0.60 - 0.79** | ○ GOOD | Generally aligned |
| **0.40 - 0.59** | ⚠ FAIR | Some misalignment |
| **0.00 - 0.39** | ✗ POOR | Significant misalignment |

### Why Dharmic Validation Matters

1. **Quality Assurance**: High alignment = high-quality decision process
2. **Pattern Learning**: Low alignment reveals process issues
3. **Self-Correction**: System can learn to improve ordering
4. **Trust Building**: Transparent validation builds confidence
5. **Principled Governance**: Decisions follow coherent philosophy

---

## Example Decision Flow

Let's trace a complete decision through the system with full visualization.

### Query

```
"Maybe we should theoretically build a blockchain-based voting system for the community?"
```

### Phase 1: Activation Computation

Each agent computes its activation strength:

```
Agent      Activation  Threshold  Status     Reason
─────────────────────────────────────────────────────────────
Krudi      0.95        0.3        ✓ ACTIVE   Decision + speculation detected
Parva      0.50        0.3        ✓ ACTIVE   "system" implies consequences
Shanti     0.25        0.3        ○ passive  No conflict yet
Rudi       0.35        0.3        ✓ ACTIVE   "build" implies change
Maya       0.90        0.3        ✓ ACTIVE   Simulation keywords present
Smriti     0.60        0.3        ✓ ACTIVE   Patterns with "blockchain"
Kshana     1.00        0.0        ✓ ACTIVE   Always activates
```

**Sparsity**: 1 inactive / 6 agents = 0.17 (low sparsity - many engaged)

### Phase 2: Circuit Firing

Each active agent fires its circuits:

```
┌──────────────────────────────────────────────────────┐
│ KRUDI (0.95)                                         │
├──────────────────────────────────────────────────────┤
│ Circuits Fired:                                      │
│   • reality_anchor                                   │
│   • embodied_grounding (detected "build")            │
│   • sovereignty_alignment (detected "community")     │
│                                                      │
│ Response:                                            │
│   "Ground this in concrete technical constraints.   │
│    Blockchain is complex - what's the minimal       │
│    viable implementation?"                           │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│ PARVA (0.50)                                         │
├──────────────────────────────────────────────────────┤
│ Circuits Fired:                                      │
│   • consequence_modeling                             │
│   • temporal_flow                                    │
│                                                      │
│ Response:                                            │
│   "Consider long-term maintenance burden and        │
│    governance evolution over time."                  │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│ RUDI (0.35)                                          │
├──────────────────────────────────────────────────────┤
│ Circuits Fired:                                      │
│   • adaptation_pathway                               │
│                                                      │
│ Response:                                            │
│   "This represents significant organizational       │
│    transformation. Plan the change pathway."         │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│ MAYA (0.90)                                          │
├──────────────────────────────────────────────────────┤
│ Circuits Fired:                                      │
│   • forward_model                                    │
│   • scenario_generation                              │
│                                                      │
│ Response:                                            │
│   "Model scenarios: centralized, federated, and     │
│    fully decentralized options."                     │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│ SMRITI (0.60)                                        │
├──────────────────────────────────────────────────────┤
│ Circuits Fired:                                      │
│   • history_retrieval                                │
│   • pattern_recognition                              │
│                                                      │
│ Response:                                            │
│   "Historical pattern: Blockchain projects often    │
│    over-promise and under-deliver. Learn from this." │
└──────────────────────────────────────────────────────┘
```

### Phase 3: Conflict Measurement

```python
activation_strengths = [0.95, 0.50, 0.25, 0.35, 0.90, 0.60]
variance = 0.084
conflict_score = 0.336  # Low-medium conflict
```

**Interpretation**: Some disagreement but not high. Shanti stays inactive (correct).

### Phase 4: Kshana Synthesis

```
┌──────────────────────────────────────────────────────┐
│ KSHANA (1.00) - DECISION COLLAPSE                   │
├──────────────────────────────────────────────────────┤
│ Circuits Fired:                                      │
│   • synthesis                                        │
│   • decision_collapse                                │
│   • presence_anchor                                  │
│                                                      │
│ Integrated Perspectives:                             │
│   ✓ Krudi: Ground in reality                        │
│   ✓ Parva: Consider long-term consequences          │
│   ✓ Rudi: Plan transformation carefully             │
│   ✓ Maya: Model multiple scenarios                  │
│   ✓ Smriti: Learn from blockchain history           │
│                                                      │
│ FINAL DECISION:                                      │
│   "Before committing to blockchain, explore simpler │
│   alternatives. If proceeding, start with minimal   │
│   viable implementation, model scenarios carefully, │
│   and learn from past blockchain projects that      │
│   failed due to over-engineering."                   │
└──────────────────────────────────────────────────────┘
```

### Phase 5: Dharmic Validation

```
Checking dharmic principles...

✓ Kshana last?         YES  (kshana is final in sequence)
✓ Krudi before Maya?   YES  (krudi activated first)
✓ Shanti on conflict?  N/A  (conflict not high enough)
○ Smriti with Rudi?    YES  (both activated)

Dharmic Alignment: 3.0 / 3.0 = 1.00 (100%)
Status: ✓ EXCELLENT
```

### Phase 6: Pattern Detection

```
Analyzing activation patterns...

⚠ LOW_SPARSITY: Many agents activated (83%) - decision may be overly complex

No other concerning patterns detected.
```

### Phase 7: Lineage Extraction

Agents with activation > 0.5:

```
Lineage Path:
  1. krudi.reality_anchor
  2. krudi.embodied_grounding
  3. krudi.sovereignty_alignment
  4. parva.consequence_modeling
  5. parva.temporal_flow
  6. maya.forward_model
  7. maya.scenario_generation
  8. smriti.history_retrieval
  9. smriti.pattern_recognition
 10. kshana.synthesis
 11. kshana.decision_collapse
 12. kshana.presence_anchor
```

### Complete Trace Summary

```
╔══════════════════════════════════════════════════════════╗
║              PARLIAMENT DECISION TRACE                   ║
╚══════════════════════════════════════════════════════════╝

Decision ID:        a7c9f2e1-8b4d-4f6a-9e3c-1d5b7a8f9c2e
Kshana Index:       #15
Query:              "Maybe we should theoretically build a
                    blockchain-based voting system for the
                    community?"

METRICS:
  Total Activation:    4.25
  Sparsity Ratio:      17% (low - many agents)
  Confidence:          72%
  Dharmic Alignment:   100% ✓ EXCELLENT

ACTIVE AGENTS (5/6):
  • Krudi   (0.95) ✓✓✓
  • Maya    (0.90) ✓✓✓
  • Smriti  (0.60) ✓✓
  • Parva   (0.50) ✓
  • Rudi    (0.35) ✓

PATTERN FLAGS (1):
  ⚠ LOW_SPARSITY: Many agents activated

LINEAGE DEPTH: 12 circuits

DECISION: Proceed cautiously with simpler alternatives first.
```

---

## Design Principles

### 1. Sparse Activation Over Dense Processing

**Principle**: Only relevant agents should activate.

**Implementation**: Each agent computes activation strength independently. Threshold-based engagement.

**Benefit**: Efficiency and clarity.

### 2. Traceability Over Opacity

**Principle**: Every decision must be fully traceable.

**Implementation**: CircuitActivation records every activation with timestamp and context.

**Benefit**: Auditability, learning, debugging.

### 3. Validation Over Assumption

**Principle**: Decision quality should be measurable.

**Implementation**: Dharmic alignment scoring and pattern detection.

**Benefit**: Quality assurance and continuous improvement.

### 4. Synthesis Over Voting

**Principle**: Kshana synthesizes perspectives rather than voting.

**Implementation**: Integration of all active agent perspectives into coherent decision.

**Benefit**: Holistic decisions that honor multiple viewpoints.

### 5. Embodiment Over Abstraction

**Principle**: Grounding (Krudi) comes before simulation (Maya).

**Implementation**: Dharmic validation enforces this ordering.

**Benefit**: Realistic plans grounded in constraints.

### 6. Memory Over Amnesia

**Principle**: Learn from history (Smriti) when transforming (Rudi).

**Implementation**: Historical context provided to all agents, pattern flags for ahistorical decisions.

**Benefit**: Avoid repeating mistakes.

### 7. Equilibrium Over Chaos

**Principle**: Restore balance (Shanti) when conflict arises.

**Implementation**: Conflict measurement and adaptive Shanti activation.

**Benefit**: Stable, harmonious decisions.

---

## Conclusion

The Sacred QA Audits architecture implements a principled, traceable, and adaptive decision-making system. Through sparse activation, circuit tracing, and dharmic validation, it ensures that decisions are:

- **Efficient**: Only relevant agents engage
- **Transparent**: Full traceability of reasoning
- **Quality-Assured**: Validated against dharmic principles
- **Adaptive**: Learns from decision history
- **Holistic**: Synthesizes multiple perspectives

The three-layer architecture (Circuit → Agent → Parliament) provides clear separation of concerns while maintaining coherent operation.

---

**Version**: 0.1.0
**Last Updated**: 2024-11-17
**Authors**: Sacred QA Team
