"""Hermetic tests for HeadlineOptimizer (Sprint 39)."""
from engines.content_optimization.headline_optimizer import HeadlineOptimizer


def test_suggest_too_short():
    s = HeadlineOptimizer().suggest_improvements("Коротко")
    assert any("короткий" in x.lower() for x in s)


def test_suggest_too_long():
    s = HeadlineOptimizer().suggest_improvements("X" * 150)
    assert any("длинный" in x.lower() for x in s)


def test_suggest_emoji():
    s = HeadlineOptimizer().suggest_improvements("Заголовок средней длины без эмодзи")
    assert any("emoji" in x.lower() for x in s)


def test_variations_contain_emoji_prefix():
    v = HeadlineOptimizer().generate_variations("Тестовый заголовок для проверки")
    strategies = [x["strategy"] for x in v]
    assert "emoji_prefix" in strategies


def test_optimize_structure():
    r = HeadlineOptimizer().optimize("Новый AI агент для задач")
    assert "original" in r
    assert "suggestions" in r
    assert "variations" in r