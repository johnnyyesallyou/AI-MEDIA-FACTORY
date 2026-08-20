"""CI tests for Channel Templates (Sprint 46.2)."""
import pytest
from core.models.channel_templates import get_template, list_templates


def test_list_templates():
    templates = list_templates()
    assert len(templates) >= 3
    ids = [t["id"] for t in templates]
    assert "news" in ids
    assert "anime" in ids
    assert "manga" in ids


def test_get_template_news():
    t = get_template("news")
    assert t is not None
    assert t["platform"] == "telegram"
    assert len(t["sources"]) > 0
    assert "schedule" in t
    assert t["image_policy"]["fallback"] == "ai_generated"


def test_get_template_anime():
    t = get_template("anime")
    assert t is not None
    assert t["image_policy"]["fallback"] == "none"  # AI запрещён


def test_get_template_manga():
    t = get_template("manga")
    assert t is not None
    assert t["image_policy"]["fallback"] == "none"  # AI запрещён
    assert len(t["sources"]) >= 2  # ReManga + MangaDex


def test_get_template_not_found():
    t = get_template("nonexistent")
    assert t is None