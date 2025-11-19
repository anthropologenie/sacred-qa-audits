"""Base integration interface for external data sources.

This module defines the abstract base class that all integrations must implement.
Integrations provide bidirectional data flow between the Parliament and external
systems, enabling grounded decision-making and outcome-based learning.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from ..circuits.activation_tracker import ParliamentDecisionTrace


class BaseIntegration(ABC):
    """Abstract base class for external data integrations.

    Integrations serve three primary purposes:
        1. Fetch external context to ground parliamentary decisions
        2. Enrich agent-specific context with relevant data
        3. Validate decisions against real-world outcomes for learning

    Subclasses must implement all abstract methods to provide:
        - Context fetching for different query types
        - Agent-specific context enrichment
        - Decision validation against outcomes
        - Threshold calibration based on accuracy

    Attributes:
        name: Unique identifier for this integration
        connected: Whether the integration is currently connected
    """

    def __init__(self, name: str) -> None:
        """Initialize the base integration.

        Args:
            name: Unique identifier for this integration
        """
        self.name = name
        self.connected = False

    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to the external data source.

        Returns:
            True if connection successful, False otherwise

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement connect()"
        )

    @abstractmethod
    def disconnect(self) -> None:
        """Close connection to the external data source.

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement disconnect()"
        )

    @abstractmethod
    def fetch_context(
        self, query_type: str, **kwargs: Any
    ) -> Dict[str, Any]:
        """Fetch relevant context from external source for a query type.

        This method retrieves external data needed to ground parliamentary
        deliberation. Different query types require different data.

        Args:
            query_type: Type of query being made (e.g., 'job_evaluation')
            **kwargs: Additional parameters specific to the query type

        Returns:
            Dictionary containing relevant context data

        Raises:
            ValueError: If query_type is not supported
            ConnectionError: If integration is not connected
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement fetch_context()"
        )

    @abstractmethod
    def enrich_agent_context(
        self, agent_name: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add agent-specific external data to context.

        Each agent has different information needs. This method enriches
        the context with data relevant to a specific agent's domain.

        Args:
            agent_name: Name of the agent to enrich context for
            context: Existing context dictionary

        Returns:
            Enriched context dictionary with agent-specific data

        Raises:
            ValueError: If agent_name is not recognized
            ConnectionError: If integration is not connected
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement enrich_agent_context()"
        )

    @abstractmethod
    def validate_decision(
        self, decision_trace: ParliamentDecisionTrace
    ) -> Dict[str, Any]:
        """Validate a parliamentary decision against real-world outcomes.

        This method enables learning by comparing parliamentary predictions
        with actual outcomes. The validation data can be used to calibrate
        agent activation thresholds and improve decision quality.

        Args:
            decision_trace: The decision trace to validate

        Returns:
            Dictionary containing validation metrics:
                - 'outcome': Actual outcome (if available)
                - 'accuracy': How well the decision matched reality
                - 'confidence_accuracy': How well confidence matched certainty
                - 'agent_accuracies': Per-agent accuracy scores

        Raises:
            ValueError: If decision_trace is invalid
            ConnectionError: If integration is not connected
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement validate_decision()"
        )

    @abstractmethod
    def calibrate_thresholds(
        self, agent_stats: Dict[str, Dict[str, Any]]
    ) -> Dict[str, float]:
        """Suggest threshold adjustments based on outcome data.

        Analyzes historical decision accuracy to recommend new activation
        thresholds for agents. Agents that are too conservative should have
        lower thresholds; agents that are too aggressive should have higher
        thresholds.

        Args:
            agent_stats: Statistics about agent activation patterns

        Returns:
            Dictionary mapping agent names to suggested threshold values

        Raises:
            ValueError: If agent_stats is invalid
            ConnectionError: If integration is not connected
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement calibrate_thresholds()"
        )

    def get_supported_query_types(self) -> List[str]:
        """Get list of query types supported by this integration.

        Returns:
            List of supported query type strings
        """
        return []

    def get_supported_agents(self) -> List[str]:
        """Get list of agent names that can be enriched by this integration.

        Returns:
            List of supported agent names
        """
        return []

    def health_check(self) -> Dict[str, Any]:
        """Check the health status of this integration.

        Returns:
            Dictionary containing health metrics:
                - 'connected': Connection status
                - 'latency_ms': Response time in milliseconds
                - 'errors': Recent error count
                - 'last_query': Timestamp of last successful query
        """
        return {
            "connected": self.connected,
            "latency_ms": None,
            "errors": 0,
            "last_query": None,
        }

    def __repr__(self) -> str:
        """Return string representation of the integration."""
        status = "connected" if self.connected else "disconnected"
        return f"{self.__class__.__name__}(name='{self.name}', status='{status}')"
