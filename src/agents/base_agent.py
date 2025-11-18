"""Base agent class for QA audit agents.

This module provides the abstract base class for all agents in the Sacred QA
Audits system. Agents use activation-based processing to determine when and
how to respond to queries.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Tuple

from circuits.activation_tracker import CircuitActivation


class BaseAgent(ABC):
    """Abstract base class for all QA audit agents.

    Agents process queries through an activation-based mechanism. Each agent
    computes its activation strength for a given query, and only engages in
    deliberation if the activation exceeds a threshold.

    Subclasses must implement:
        - _compute_activation: Calculate how relevant this agent is to the query
        - _deliberate: Perform the actual reasoning and decision-making
        - _extract_context: Extract relevant context from the query

    Attributes:
        name: The unique name of this agent
        activation_threshold: Minimum activation strength required to engage (default 0.3)
    """

    def __init__(self, name: str) -> None:
        """Initialize the base agent.

        Args:
            name: Unique identifier for this agent
        """
        self.name = name
        self.activation_threshold = 0.3

    def process(
        self, query: str, context: Dict[str, Any]
    ) -> Tuple[str, CircuitActivation]:
        """Process a query and return a response with activation trace.

        This is the main entry point for agent processing. It computes the
        activation strength, determines if the agent should engage, and
        returns both the response and a trace of the activation.

        Args:
            query: The question or task to process
            context: Additional contextual information

        Returns:
            A tuple containing:
                - response: The agent's response (empty string if below threshold)
                - activation: CircuitActivation trace of this processing

        Raises:
            ValueError: If activation strength is outside valid range [0.0, 1.0]
        """
        # Compute activation strength for this query
        activation_strength = self._compute_activation(query, context)

        # Validate activation strength
        if not 0.0 <= activation_strength <= 1.0:
            raise ValueError(
                f"Activation strength must be between 0.0 and 1.0, "
                f"got {activation_strength} from {self.name}"
            )

        # Extract relevant context for tracking
        extracted_context = self._extract_context(query, context)

        # Check if activation is below threshold
        if activation_strength < self.activation_threshold:
            # Create minimal activation trace for non-engaged agent
            activation = CircuitActivation(
                agent_name=self.name,
                activation_strength=activation_strength,
                circuits_fired=[],
                timestamp=datetime.now(),
                context=extracted_context,
            )
            return "", activation

        # Agent is activated - perform deliberation
        circuits_fired = self._identify_circuits(query, context)
        response = self._deliberate(query, context, circuits_fired)

        # Create full activation trace
        activation = CircuitActivation(
            agent_name=self.name,
            activation_strength=activation_strength,
            circuits_fired=circuits_fired,
            timestamp=datetime.now(),
            context=extracted_context,
        )

        return response, activation

    def _identify_circuits(
        self, query: str, context: Dict[str, Any]
    ) -> List[str]:
        """Identify which circuits should fire for this query.

        This is a helper method that can be overridden by subclasses to
        customize circuit identification logic. The default implementation
        returns a single circuit based on the agent's name.

        Args:
            query: The question or task being processed
            context: Additional contextual information

        Returns:
            List of circuit identifiers that should fire
        """
        return [f"{self.name}_primary_circuit"]

    @abstractmethod
    def _compute_activation(
        self, query: str, context: Dict[str, Any]
    ) -> float:
        """Compute the activation strength for this query.

        This method determines how relevant and engaged this agent should be
        for the given query. The activation strength should be in the range
        [0.0, 1.0], where:
            - 0.0 means completely irrelevant
            - 1.0 means maximally relevant
            - Values >= activation_threshold trigger deliberation

        Args:
            query: The question or task to evaluate
            context: Additional contextual information

        Returns:
            Activation strength between 0.0 and 1.0

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement _compute_activation"
        )

    @abstractmethod
    def _deliberate(
        self, query: str, context: Dict[str, Any], circuits: List[str]
    ) -> str:
        """Perform deliberation and generate a response.

        This is the core reasoning method where the agent processes the query
        and generates its response. This method is only called when activation
        strength exceeds the threshold.

        Args:
            query: The question or task to process
            context: Additional contextual information
            circuits: List of circuits that have been activated

        Returns:
            The agent's response to the query

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement _deliberate"
        )

    @abstractmethod
    def _extract_context(
        self, query: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract relevant context for tracking.

        This method filters and extracts the most relevant pieces of context
        for this agent's processing. This extracted context is stored in the
        CircuitActivation for later analysis.

        Args:
            query: The question or task being processed
            context: Full contextual information

        Returns:
            Dictionary of relevant context information

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement _extract_context"
        )

    def __repr__(self) -> str:
        """Return string representation of the agent."""
        return (
            f"{self.__class__.__name__}(name='{self.name}', "
            f"threshold={self.activation_threshold})"
        )
