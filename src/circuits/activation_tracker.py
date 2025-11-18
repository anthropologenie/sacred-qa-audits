"""Circuit activation tracking for QA audit workflows.

This module provides dataclasses for tracking circuit activations and parliamentary
decision traces throughout the QA audit process.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List
from uuid import uuid4


@dataclass
class CircuitActivation:
    """Represents a single circuit activation event.

    Tracks which agent fired, the strength of activation, and the context
    in which the activation occurred.

    Attributes:
        agent_name: Name of the agent that was activated
        activation_strength: Strength of activation (0.0-1.0, where 1.0 is maximum)
        circuits_fired: List of circuit identifiers that were triggered
        timestamp: When this activation occurred
        context: Additional contextual information about the activation
    """

    agent_name: str
    activation_strength: float
    circuits_fired: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate activation strength is within valid range."""
        if not 0.0 <= self.activation_strength <= 1.0:
            raise ValueError(
                f"activation_strength must be between 0.0 and 1.0, "
                f"got {self.activation_strength}"
            )


@dataclass
class ParliamentDecisionTrace:
    """Traces a complete parliamentary decision cycle.

    Captures the full decision-making process including all circuit activations,
    the sparsity of activation, the sequence of events, and the final decision
    with its confidence and alignment scores.

    Attributes:
        decision_id: Unique identifier for this decision (UUID string)
        kshana_index: Index representing the decision moment in time
        query: The question or query being decided upon
        activations: Mapping of agent names to their activation records
        sparsity_ratio: Ratio of active vs inactive circuits (0.0-1.0)
        total_activation: Sum of all activation strengths
        activation_sequence: Ordered list of agent names in activation order
        decision: The final decision or recommendation
        confidence: Confidence level in the decision (0.0-1.0)
        dharmic_alignment: Alignment with dharmic principles (0.0-1.0)
        pattern_flags: List of detected patterns or anomalies
        lineage_path: Hierarchical path showing decision ancestry
    """

    decision_id: str = field(default_factory=lambda: str(uuid4()))
    kshana_index: int = 0
    query: str = ""
    activations: Dict[str, CircuitActivation] = field(default_factory=dict)
    agent_responses: Dict[str, str] = field(default_factory=dict)
    sparsity_ratio: float = 0.0
    total_activation: float = 0.0
    activation_sequence: List[str] = field(default_factory=list)
    decision: str = ""
    confidence: float = 0.0
    dharmic_alignment: float = 0.0
    pattern_flags: List[str] = field(default_factory=list)
    lineage_path: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate numeric fields are within valid ranges."""
        if not 0.0 <= self.sparsity_ratio <= 1.0:
            raise ValueError(
                f"sparsity_ratio must be between 0.0 and 1.0, "
                f"got {self.sparsity_ratio}"
            )

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                f"confidence must be between 0.0 and 1.0, "
                f"got {self.confidence}"
            )

        if not 0.0 <= self.dharmic_alignment <= 1.0:
            raise ValueError(
                f"dharmic_alignment must be between 0.0 and 1.0, "
                f"got {self.dharmic_alignment}"
            )

        if self.total_activation < 0.0:
            raise ValueError(
                f"total_activation must be non-negative, "
                f"got {self.total_activation}"
            )

        if self.kshana_index < 0:
            raise ValueError(
                f"kshana_index must be non-negative, "
                f"got {self.kshana_index}"
            )

    def add_activation(self, activation: CircuitActivation) -> None:
        """Add a circuit activation to this decision trace.

        Args:
            activation: The circuit activation to add
        """
        self.activations[activation.agent_name] = activation
        self.activation_sequence.append(activation.agent_name)
        self.total_activation += activation.activation_strength

    def compute_sparsity(
        self, total_agents: int, activation_threshold: float = 0.5
    ) -> None:
        """Calculate the sparsity ratio based on active vs total agents.

        Args:
            total_agents: Total number of agents in the parliament
            activation_threshold: Threshold for considering an agent "active"
        """
        if total_agents <= 0:
            raise ValueError("total_agents must be positive")

        # Count only agents that activated above threshold
        active_agents = sum(
            1
            for act in self.activations.values()
            if act.activation_strength >= activation_threshold
        )
        self.sparsity_ratio = 1.0 - (active_agents / total_agents)
