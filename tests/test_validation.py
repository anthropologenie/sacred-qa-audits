"""Tests for Parliament validation and accuracy tracking."""

import pytest
from unittest.mock import Mock, MagicMock
from src.integrations.validation import ParliamentValidator


class TestParliamentValidator:
    """Test the ParliamentValidator class."""

    def test_validator_requires_connected_db(self):
        """Validator should raise error if DB not connected."""
        mock_db = Mock()
        mock_db.connected = False

        with pytest.raises(ConnectionError):
            ParliamentValidator(mock_db)

    def test_validator_initialization(self):
        """Validator should initialize with connected DB."""
        mock_db = Mock()
        mock_db.connected = True

        validator = ParliamentValidator(mock_db)
        assert validator.db == mock_db

    def test_calculate_accuracy_metrics_no_outcomes(self):
        """Should return note when no decisions have outcomes."""
        mock_db = Mock()
        mock_db.connected = True
        mock_db.cursor = Mock()

        # Mock empty results
        mock_db.cursor.fetchall.return_value = []

        validator = ParliamentValidator(mock_db)
        metrics = validator.calculate_accuracy_metrics()

        assert 'note' in metrics
        assert metrics['total_decisions'] == 0
        assert metrics['decisions_with_outcomes'] == 0

    def test_generate_accuracy_report_no_data(self):
        """Should generate report even with no data."""
        mock_db = Mock()
        mock_db.connected = True
        mock_db.cursor = Mock()
        mock_db.cursor.fetchall.return_value = []

        validator = ParliamentValidator(mock_db)
        report = validator.generate_accuracy_report()

        assert 'PARLIAMENT ACCURACY REPORT' in report
        assert 'Total Decisions: 0' in report

    def test_suggest_threshold_adjustments_no_data(self):
        """Should return note when no data available."""
        mock_db = Mock()
        mock_db.connected = True
        mock_db.cursor = Mock()
        mock_db.cursor.fetchall.return_value = []

        validator = ParliamentValidator(mock_db)
        adjustments = validator.suggest_threshold_adjustments()

        assert 'note' in adjustments

    def test_calculate_decision_accuracy_perfect_match(self):
        """High confidence + positive outcome = high accuracy."""
        mock_db = Mock()
        mock_db.connected = True

        validator = ParliamentValidator(mock_db)

        # High confidence (0.9) + strong outcome (interview + offer)
        accuracy = validator._calculate_decision_accuracy(
            confidence=0.9,
            applied=True,
            callback=True,
            interview=True,
            offer=True
        )

        # Confidence 0.9, outcome score 3/3 = 1.0, difference = 0.1
        # accuracy = 1.0 - 0.1 = 0.9
        assert accuracy >= 0.8  # Should be high

    def test_calculate_decision_accuracy_mismatch(self):
        """High confidence + negative outcome = low accuracy."""
        mock_db = Mock()
        mock_db.connected = True

        validator = ParliamentValidator(mock_db)

        # High confidence (0.9) + no outcome at all
        accuracy = validator._calculate_decision_accuracy(
            confidence=0.9,
            applied=True,
            callback=False,
            interview=False,
            offer=False
        )

        # Confidence 0.9, outcome score 0/3 = 0.0, difference = 0.9
        # accuracy = 1.0 - 0.9 = 0.1
        assert accuracy <= 0.2  # Should be low


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
