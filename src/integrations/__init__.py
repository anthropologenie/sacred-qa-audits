"""Integration layer for external data sources.

This module provides interfaces for integrating external data sources with the
Kragentic Parliament decision-making system. Integrations allow agents to access
real-world data for grounded decision-making and enable bidirectional learning
from outcomes.

Available integrations:
    - BaseIntegration: Abstract interface for all integrations
    - JobsDBIntegration: SQLite integration with jobs-application-automation system
    - ParliamentValidator: Accuracy tracking and threshold calibration
"""

from .base_integration import BaseIntegration
from .jobs_db_integration import JobsDBIntegration
from .validation import ParliamentValidator

__all__ = [
    "BaseIntegration",
    "JobsDBIntegration",
    "ParliamentValidator",
]
