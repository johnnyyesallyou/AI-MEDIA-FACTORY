"""Hermetic tests for Autonomous Optimization (Sprint 45)."""
from unittest.mock import MagicMock, patch

from engines.content_optimization.auto_apply import OptimizationApplier


def test_applier_init():
    applier = OptimizationApplier()
    assert applier.headline_optimizer is not None
    assert applier.posting_time_optimizer is not None
    assert applier.ab_framework is not None


@patch("engines.content_optimization.auto_apply.SessionLocal")
def test_apply_headline_no_posts(mock_session):
    mock_db = MagicMock()
    mock_session.return_value = mock_db
    mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
    
    applier = OptimizationApplier()
    result = applier.apply_headline_optimizations(1)
    assert result["applied"] == 0
    assert "No posts" in result["message"]


@patch("engines.content_optimization.auto_apply.SessionLocal")
def test_apply_posting_time_no_data(mock_session):
    mock_db = MagicMock()
    mock_session.return_value = mock_db
    mock_db.query.return_value.filter.return_value.group_by.return_value.all.return_value = []
    
    applier = OptimizationApplier()
    result = applier.apply_posting_time_optimizations(1)
    assert result["applied"] is False
    assert "No engagement data" in result["message"]