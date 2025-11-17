# Sacred QA Audits

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Development Status](https://img.shields.io/badge/status-alpha-orange.svg)](https://github.com/anthropologenie/sacred-qa-audits)

> Circuit-traced Kragentic Parliament implementing mechanistically interpretable dharmic AI.

## Overview

Sacred QA Audits is a **parliamentary multi-agent decision-making system** where specialized agents deliberate on queries through sparse activation. Every decision is fully traced through circuit activations, validated against dharmic (proper flow) principles, and recorded for complete auditability.

**Key Innovation**: Mechanistic interpretability through circuit tracing + dharmic validation = transparent, principled AI decision-making.

## Architecture

The system implements a **three-layer architecture** for transparent, traceable decision-making:

### 1. Circuit Layer (`src/circuits/`)
**Foundation for traceability**
- `CircuitActivation`: Records each agent's activation with timestamp, strength, and context
- `ParliamentDecisionTrace`: Complete decision audit trail with lineage path

### 2. Agent Layer (`src/agents/`)
**Specialized perspectives**

| Agent | Role | Activation Logic |
|-------|------|------------------|
| **Krudi** | Reality grounding, embodied constraints | High when implementation/building mentioned |
| **Parva** | Temporal causality, consequences | High when time/causality involved |
| **Shanti** | Equilibrium, conflict resolution | High when agent conflict detected |
| **Rudi** | Transformation, adaptation | High when change/learning needed |
| **Kshana** | Synthesis, decision collapse | **Always active** (final synthesis) |
| **Maya** | Simulation, forward modeling | High when scenario modeling needed |
| **Smriti** | Memory, pattern recognition | High when history/patterns relevant |

### 3. Parliament Layer (`src/parliament/`)
**Orchestration & validation**
- Coordinates multi-agent deliberation
- Enforces dharmic ordering (e.g., grounding before simulation)
- Computes sparsity, confidence, and alignment metrics
- Maintains complete decision history

**📖 [Full Architecture Documentation →](docs/architecture.md)**

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/anthropologenie/sacred-qa-audits.git
cd sacred-qa-audits

# Install in development mode
pip install -e .

# Optional: Install development dependencies
pip install -e ".[dev]"
```

### Requirements

- Python 3.10 or higher
- Pydantic 2.0+

## Quick Start

```python
from src.parliament.kragentic_parliament import KragenticParliament

# Initialize parliament
parliament = KragenticParliament()

# Deliberate on a query
query = "Should we implement decentralized governance?"
decision, trace = parliament.deliberate(query)

# View decision
print(decision)

# Inspect trace
print(f"Active Agents: {len([a for a in trace.activations.values()
                              if a.activation_strength >= 0.3])}")
print(f"Sparsity: {trace.sparsity_ratio:.1%}")
print(f"Dharmic Alignment: {trace.dharmic_alignment:.1%}")
print(f"Confidence: {trace.confidence:.1%}")
print(f"Lineage: {trace.lineage_path}")
```

### Run Example

```bash
python3 examples/traced_decision.py
```

**Output**: Fully formatted decision trace with agent activations, circuit paths, pattern flags, and dharmic validation.

## Phase 1 Status ✅

The foundation is complete and operational:

- ✅ **Circuit Tracing Infrastructure**
  - `CircuitActivation` records every activation
  - `ParliamentDecisionTrace` provides complete audit trail
  - Timestamps, context, and lineage tracking

- ✅ **7 Specialized Agents**
  - Sparse activation (only relevant agents fire)
  - Domain-specific circuits (18+ unique circuits)
  - Context extraction for each perspective

- ✅ **Parliament Orchestration**
  - Multi-agent deliberation flow
  - Kshana synthesis (decision collapse)
  - Conflict detection and Shanti activation
  - Decision history maintenance

- ✅ **Dharmic Pattern Detection**
  - Grounding before simulation validation
  - Synthesis-last enforcement
  - Memory-informed transformation checks
  - 6 pattern flag types

- ✅ **Complete Decision Lineage**
  - Circuit path extraction
  - Activation sequence tracking
  - Sparsity and confidence metrics
  - Full traceability for audits

## Roadmap

### Phase 2: Ablation Testing (Necessity Validation)
**Goal**: Validate that each agent is necessary

- Systematic agent removal experiments
- Performance impact measurement
- Necessity scoring per agent
- Redundancy detection

### Phase 3: Pattern Recognition (Dharmic Verification)
**Goal**: Verify dharmic principles through data

- Historical decision analysis
- Pattern clustering and classification
- Dharmic principle validation
- Optimal activation patterns

### Phase 4: SmritiTree L0-L6 Mapping
**Goal**: Hierarchical memory and pattern storage

- L0: Raw decision traces
- L1: Circuit patterns
- L2: Agent collaboration patterns
- L3: Dharmic archetypes
- L4: Decision templates
- L5: Meta-patterns (patterns of patterns)
- L6: Wisdom layer (synthesized principles)

## Architecture Principles

### 1. Sparse Activation
**Only relevant agents activate for a given query**
- Efficiency: No wasted computation
- Clarity: High activation signals true relevance
- Biological inspiration: Neural sparse coding

### 2. Mechanistic Interpretability
**Every decision pathway is traceable**
- Circuit-level granularity
- Timestamp and context capture
- Complete lineage extraction
- No black boxes

### 3. Dharmic Alignment Validation
**Decisions follow proper ordering principles**
- Grounding before simulation (Krudi → Maya)
- Synthesis last (Kshana finality)
- Equilibrium when needed (Shanti on conflict)
- Memory informs transformation (Smriti + Rudi)

### 4. Complete Lineage Traceability
**Full audit trail for every decision**
- Decision ID (UUID) tracking
- Kshana index (temporal ordering)
- Activation sequence recording
- Pattern flag detection

## Project Structure

```
sacred-qa-audits/
├── src/
│   ├── circuits/          # Circuit tracing infrastructure
│   │   └── activation_tracker.py
│   ├── agents/            # 7 specialized agents
│   │   ├── base_agent.py
│   │   ├── krudi_agent.py
│   │   ├── parva_agent.py
│   │   ├── shanti_agent.py
│   │   ├── rudi_agent.py
│   │   ├── kshana_agent.py
│   │   ├── maya_agent.py
│   │   └── smriti_agent.py
│   ├── parliament/        # Orchestration layer
│   │   └── kragentic_parliament.py
│   ├── qa/                # QA utilities (Phase 2+)
│   └── utils/             # Shared utilities
├── examples/
│   └── traced_decision.py # Working example
├── docs/
│   └── architecture.md    # Comprehensive architecture docs
├── tests/                 # Test suite (Phase 2+)
└── pyproject.toml        # Project configuration
```

## Contributing

Sacred QA Audits is in active development. Contributions are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use Sacred QA Audits in your research or project, please cite:

```bibtex
@software{sacred_qa_audits,
  title = {Sacred QA Audits: Circuit-traced Kragentic Parliament},
  author = {Sacred QA Team},
  year = {2024},
  url = {https://github.com/anthropologenie/sacred-qa-audits},
  version = {0.1.0}
}
```

## Links

- **Documentation**: [Architecture Guide](docs/architecture.md)
- **Repository**: [GitHub](https://github.com/anthropologenie/sacred-qa-audits)
- **Issues**: [Issue Tracker](https://github.com/anthropologenie/sacred-qa-audits/issues)

---

**Status**: Phase 1 Complete ✅ | **Version**: 0.1.0 | **Python**: 3.10+
