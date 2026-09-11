"""
Sprint 75.1: Profile → Pipeline runtime contract — smoke test.

Проверяет:
1. load_profile_config приоритеты (Profile > content_profile > legacy)
2. ResearchEngine принимает sources_override (профильные источники)
3. ResearchJob/WritingJob/EvaluatorJob wiring через profile_config
   (проверяем через реальный ResearchJob.run с in-memory SQLite)

ChannelProfileORM аудитория — JSONB dict; style_profile собирается
в строку _audience_to_str().
"""
import asyncio
from unittest.mock import patch

import pytest

from core.database import Base, SessionLocal
from core.models.channel_orm import ChannelORM
from core.models.channel_profile_orm import ChannelProfileORM


@pytest.fixture()
def session():
    from sqlalchemy import create_engine
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    s = SessionLocal(bind=engine)
    yield s
    s.close()
    engine.dispose()


PROFILE_SOURCES = [
    {"name": "MIT Tech Review", "url": "https://technologyreview.com/feed", "type": "rss"},
    {"name": "Hacker News", "url": "https://hnrss.org/newest", "type": "rss"},
]


@pytest.fixture()
def profile(session):
    p = ChannelProfileORM(
        id="prof-75-1",
        name="Analytical AI Weekly",
        archetype="analytical",
        theme="technology",
        audience={"age": "25-45", "interests": ["AI", "startups"]},
        language="ru",
        tone="analytical",
        content={"max_length": 1400, "formats": ["deep_dive"]},
        research={
            "freshness_hours": 24,
            "sources": PROFILE_SOURCES,
        },
    )
    session.add(p)
    session.commit()
    return p


@pytest.fixture()
def channel_with_profile(session, profile):
    ch = ChannelORM(id="ch-75-1", name="AI Weekly", profile_id=profile.id)
    session.add(ch)
    session.commit()
    return ch


@pytest.fixture()
def channel_cp_only(session):
    ch = ChannelORM(
        id="ch-cp-1", name="CP Channel",
        content_profile={
            "topic": "AI digest",
            "audience": "Wide audience",
            "tone": "simple",
            "max_length": 800,
            "sources": [{"name": "The Verge", "url": "https://theverge.com/rss/index.xml", "type": "rss"}],
        },
    )
    session.add(ch)
    session.commit()
    return ch


@pytest.fixture()
def channel_no_profile(session):
    ch = ChannelORM(id="ch-legacy-1", name="Legacy Channel")
    session.add(ch)
    session.commit()
    return ch


@pytest.fixture()
def _isolated_db(session):
    """
    Sprint 75.1: перепривязывает automation_jobs.SessionLocal к in-memory
    test engine, чтобы jobs не трогали рабочую SQLite ai_media_factory.db
    (иначе WritingJob обработает реальные 50 research items!).
    """
    import backend.automation.jobs.automation_jobs as aj
    original = aj.SessionLocal
    aj.SessionLocal = lambda: session
    yield session
    aj.SessionLocal = original



def test_profile_priority(session, channel_with_profile):
    from backend.automation.profile_config import load_profile_config
    cfg = load_profile_config(session, channel_with_profile)
    assert cfg["source"] == "profile"
    assert cfg["profile_name"] == "Analytical AI Weekly"
    assert cfg["tone"] == "analytical"
    assert cfg["language"] == "ru"
    assert cfg["content_length"] == 1400
    assert cfg["freshness_hours"] == 24
    assert len(cfg["sources"]) == 2
    assert cfg["sources"][0]["name"] == "MIT Tech Review"
    assert "Analytical AI Weekly" in cfg["target_style"]
    assert "analytical" in cfg["target_style"]
    assert "Аудитория" in cfg["audience"]


def test_content_profile_fallback(session, channel_cp_only):
    from backend.automation.profile_config import load_profile_config
    cfg = load_profile_config(session, channel_cp_only)
    assert cfg["source"] == "content_profile"
    assert cfg["topic"] == "AI digest"
    assert cfg["content_length"] == 800
    assert len(cfg["sources"]) == 1
    assert cfg["style_profile"]["length_chars"] == 800


def test_legacy_fallback(session, channel_no_profile):
    from backend.automation.profile_config import load_profile_config
    from engines.writing.styles.profiles import TELEGRAM_AI_EXPERT
    cfg = load_profile_config(session, channel_no_profile)
    assert cfg["source"] == "legacy"
    assert cfg["style_profile"] == TELEGRAM_AI_EXPERT
    assert cfg["target_style"] == "Telegram expert IT channel"


def test_research_engine_sources_override():
    """Sprint 75.1: ResearchEngine использует профильные источники."""
    from engines.research.engine import ResearchEngine
    engine = ResearchEngine()
    engine.initialize(sources_override=PROFILE_SOURCES)
    assert len(engine.sources) == 2
    assert engine._initialized is True


def test_research_engine_no_profile_fallback():
    """Без профиля ResearchEngine работает как раньше (fallback)."""
    from engines.research.engine import ResearchEngine
    from engines.research.config import RSS_SOURCES
    engine = ResearchEngine()
    engine.initialize(channel=None)
    assert len(engine.sources) == len(RSS_SOURCES)
    assert engine._initialized is True


def test_research_job_uses_profile_sources(session, channel_with_profile, _isolated_db):
    """Sprint 75.1 end-to-end: ResearchJob.run читает sources из Channel Profile."""
    from backend.automation.jobs.automation_jobs import ResearchJob

    class _StubEngine:
        def run(self, channel=None, sources_override=None):
            # Захватываем sources_override, который передал ResearchJob
            assert sources_override == PROFILE_SOURCES
            assert sources_override[0]["name"] == "MIT Tech Review"
            return {
                "topics": [{
                    "title": "Profile-driven topic",
                    "summary": "s",
                    "urls": ["https://example.com/profile-topic"],
                }],
                "total_raw_articles": 1,
            }

    with patch(
        "backend.automation.jobs.automation_jobs.ResearchEngine",
        return_value=_StubEngine(),
    ):
        result = ResearchJob().run(channel=channel_with_profile, execution_id="exec-75-1")  # Sprint 75.1: ResearchJob.run синхронный

    assert result["status"] == "ok"
    assert result["created"] == 1
    from core.models.content_orm import ContentORM
    item = session.query(ContentORM).filter_by(headline="Profile-driven topic").first()
    assert item is not None
    assert item.status == "research"


def test_writing_job_uses_profile_style(session, channel_with_profile, _isolated_db):
    """WritingJob применяет style_profile из Channel Profile."""
    from backend.automation.jobs.automation_jobs import WritingJob
    from core.models.content_orm import ContentORM

    session.add(ContentORM(
        channel_id=channel_with_profile.id,
        source_url="https://example.com/src-75-1",
        headline="Profile style topic",
        source_text="Facts about profile style",
        status="research",
    ))
    session.commit()

    captured = {}

    class _StubWriter:
        async def generate(self, brief, style_profile=None):
            captured["audience"] = brief.audience
            captured["tone"] = brief.tone
            captured["length_chars"] = brief.length_chars
            captured["style_profile"] = style_profile
            return {"generated_text": "x" * 120, "draft": None}

    with patch(
        "backend.automation.jobs.automation_jobs.WritingEngine",
        return_value=_StubWriter(),
    ):
        result = asyncio.run(WritingJob().run(channel=channel_with_profile, execution_id="exec-75-1w"))

    assert result["status"] == "ok"
    assert result["items_processed"] == 1
    assert captured["audience"] == "Аудитория: 25-45, AI, startups"
    assert captured["tone"] == "analytical"
    assert captured["length_chars"] == 1400
    assert captured["style_profile"]["name"] == "Analytical AI Weekly"

    item = session.query(ContentORM).filter_by(headline="Profile style topic").first()
    assert item.status == "draft"


def test_evaluator_job_uses_profile_target_style(session, channel_with_profile, _isolated_db):
    """EvaluatorJob передаёт target_style из Channel Profile (не hardcoded)."""
    from backend.automation.jobs.automation_jobs import EvaluatorJob
    from core.models.content_orm import ContentORM

    session.add(ContentORM(
        channel_id=channel_with_profile.id,
        source_url="https://example.com/src-eval-75-1",
        headline="Eval profile topic",
        source_text="Facts",
        draft_text="x" * 120,
        status="draft",
    ))
    session.commit()

    captured = {}

    class _StubEvaluator:
        async def evaluate(self, source_facts, generated_post, target_style):
            captured["target_style"] = target_style
            from engines.evaluator.models import EvaluationResult
            return EvaluationResult(
                accuracy=85, clarity=85, clickability=85,
                telegram_style=85, engagement_prediction=85,
                overall=85, is_approved=True, feedback_for_regeneration="",
            )

    with patch(
        "backend.automation.jobs.automation_jobs.LLMEvaluatorEngine",
        return_value=_StubEvaluator(),
    ):
        result = asyncio.run(EvaluatorJob().run(channel=channel_with_profile, execution_id="exec-75-1e"))

    assert result["status"] == "ok"
    assert result["approved"] == 1
    assert "Analytical AI Weekly" in captured["target_style"]
    assert "analytical" in captured["target_style"]
    assert "Telegram expert IT channel" not in captured["target_style"]


def test_jobs_legacy_fallback_when_no_profile(session, channel_no_profile, _isolated_db):
    """Без профиля все jobs работают через legacy fallback (не ломаются)."""
    from backend.automation.jobs.automation_jobs import ResearchJob

    class _StubEngine:
        def run(self, channel=None, sources_override=None):
            # Legacy: sources_override None -> engine сам делает fallback
            assert sources_override is None
            return {"topics": []}

    with patch(
        "backend.automation.jobs.automation_jobs.ResearchEngine",
        return_value=_StubEngine(),
    ):
        result = ResearchJob().run(channel=channel_no_profile, execution_id="exec-legacy")

    assert result["status"] == "ok"
    assert result["created"] == 0
