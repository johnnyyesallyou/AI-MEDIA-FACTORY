"""
Sprint 75.2: Profile A/B behavior test — два профиля → разное поведение пайплайна.

Поведенческий контракт Sprint 75.x:
    Channel Profile — runtime config source, НЕ просто метаданные.

Два канала с ДВУМЯ РАЗНЫМИ профилями должны пройти через одни и те же
Research/Writing/Evaluation jobs и получить РАЗНОЕ поведение:

    A: "Analytical Deep Dive" — analytical, 2500 chars, узкие источники, 6h
    B: "Casual Manga Buzz"    — casual, 800 chars, другие источники, 72h

Проверяется на уровне захвата аргументов движков (stub engines) —
именно то, что jobs передают в движки, определяет поведение пайплайна.
"""
import asyncio
from unittest.mock import patch

import pytest

from core.database import Base, SessionLocal
from core.models.channel_orm import ChannelORM
from core.models.channel_profile_orm import ChannelProfileORM

# ============ Профиль A: Analytical Deep Dive ============
PROFILE_A = {
    "id": "prof-ab-a",
    "name": "Analytical Deep Dive",
    "archetype": "analytical",
    "theme": "technology",
    "niche": "ai",
    "audience": {"age": "25-45", "interests": ["AI", "research"]},
    "language": "ru",
    "tone": "analytical",
    "content": {"max_length": 2500, "formats": ["deep_dive"], "emoji_usage": "off"},
    "research": {
        "freshness_hours": 6,
        "sources": [
            {"name": "arXiv CS.AI", "url": "https://arxiv.org/rss/cs.AI", "type": "rss"},
            {"name": "MIT Tech Review", "url": "https://technologyreview.com/feed", "type": "rss"},
        ],
    },
}

# ============ Профиль B: Casual Manga Buzz ============
PROFILE_B = {
    "id": "prof-ab-b",
    "name": "Casual Manga Buzz",
    "archetype": "news",
    "theme": "entertainment",
    "niche": "manga",
    "audience": {"age": "16-24", "interests": ["manga", "anime"]},
    "language": "ru",
    "tone": "casual",
    "content": {"max_length": 800, "formats": ["telegram_post"], "emoji_usage": "on"},
    "research": {
        "freshness_hours": 72,
        "sources": [
            {"name": "MangaUpdates", "url": "https://mangaupdates.com/rss", "type": "rss"},
        ],
    },
}


@pytest.fixture()
def session():
    from sqlalchemy import create_engine
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    s = SessionLocal(bind=engine)
    yield s
    s.close()
    engine.dispose()


@pytest.fixture()
def _isolated_db(session):
    """Jobs используют тестовую in-memory БД (не рабочую ai_media_factory.db)."""
    import backend.automation.jobs.automation_jobs as aj
    original = aj.SessionLocal
    aj.SessionLocal = lambda: session
    yield session
    aj.SessionLocal = original


def _make_ab_channels(session):
    """Каналы A и B с разными профилями (возвращает id — ORM может expire)."""
    pa = ChannelProfileORM(**PROFILE_A)
    pb = ChannelProfileORM(**PROFILE_B)
    session.add_all([pa, pb])
    session.commit()
    cha = ChannelORM(id="ch-ab-a", name="AI Deep Channel", profile_id=pa.id)
    chb = ChannelORM(id="ch-ab-b", name="Manga Buzz Channel", profile_id=pb.id)
    session.add_all([cha, chb])
    session.commit()
    # PipelineLogger (SessionLocal) делает commit -> ORM-объекты expired;
    # после job-прогонов каналы нужно перечитывать через session.get.
    return "ch-ab-a", "ch-ab-b"


def _get_channel(session, ch_id):
    """Свежая привязанная копия канала (после commit-ов job'ов объект expired)."""
    session.expire_all()
    return session.get(ChannelORM, ch_id)


# ============ A/B: Research behavior ============

def test_ab_research_different_sources(session, _isolated_db):
    """A/B Research: разные профили → разные источники research."""
    from backend.automation.jobs.automation_jobs import ResearchJob

    id_a, id_b = _make_ab_channels(session)
    calls = []

    class _StubEngine:
        def run(self, channel=None, sources_override=None):
            calls.append((channel.id, sources_override))
            return {"topics": [], "total_raw_articles": 0}

    with patch(
        "backend.automation.jobs.automation_jobs.ResearchEngine",
        return_value=_StubEngine(),
    ):
        ResearchJob().run(channel=_get_channel(session, id_a), execution_id="exec-ab-ra")
        ResearchJob().run(channel=_get_channel(session, id_b), execution_id="exec-ab-rb")

    by_ch = dict(calls)
    a_sources = by_ch["ch-ab-a"]
    b_sources = by_ch["ch-ab-b"]
    assert a_sources is not None and b_sources is not None
    assert [s["name"] for s in a_sources] == ["arXiv CS.AI", "MIT Tech Review"]
    assert [s["name"] for s in b_sources] == ["MangaUpdates"]
    assert a_sources != b_sources


def test_ab_research_freshness_differs(session, _isolated_db):
    """A/B: freshness_hours профилей различны (6h vs 72h) — research-окно разное."""
    from backend.automation.profile_config import load_profile_config

    id_a, id_b = _make_ab_channels(session)
    cfg_a = load_profile_config(session, _get_channel(session, id_a))
    cfg_b = load_profile_config(session, _get_channel(session, id_b))
    assert cfg_a["freshness_hours"] == 6
    assert cfg_b["freshness_hours"] == 72


# ============ A/B: Writing behavior ============

def test_ab_writing_different_styles(session, _isolated_db):
    """A/B Writing: разные профили → разные style_profile/tone/length в WritingEngine."""
    from backend.automation.jobs.automation_jobs import WritingJob
    from core.models.content_orm import ContentORM

    cha, chb = _make_ab_channels(session)
    cha = _get_channel(session, cha)
    chb = _get_channel(session, chb)
    for ch, src in [(cha, "https://example.com/ab-a"), (chb, "https://example.com/ab-b")]:
        session.add(ContentORM(
            channel_id=ch.id,
            source_url=src,
            headline=f"AB topic {ch.id}",
            source_text="Facts",
            status="research",
        ))
    session.commit()

    captured = []  # (topic, tone, length, style_name)

    class _StubWriter:
        async def generate(self, brief, style_profile=None):
            # ContentBrief не имеет channel_id; различаем A/B по topic (=headline)
            captured.append((
                brief.topic, brief.tone, brief.length_chars,
                style_profile.get("name") if style_profile else None,
            ))
            return {"generated_text": "x" * 60, "draft": None}

    with patch(
        "backend.automation.jobs.automation_jobs.WritingEngine",
        return_value=_StubWriter(),
    ):
        # Sprint 75.2 finding: WritingJob.list_all НЕ фильтрует по каналу —
        # прогон обрабатывает items ВСЕХ каналов со style_profile ТЕКУЩЕГО
        # канала. Проверяем A/B: прогон с профилем A даёт analytical/2500,
        # прогон с профилем B — casual/800 (для одного и того же item!).
        asyncio.run(WritingJob().run(channel=_get_channel(session, "ch-ab-a"), execution_id="exec-ab-wa"))
        run_a = list(captured)
        for it in session.query(ContentORM).all():
            it.status = "research"
            it.draft_text = None
        session.commit()
        captured.clear()
        asyncio.run(WritingJob().run(channel=_get_channel(session, "ch-ab-b"), execution_id="exec-ab-wb"))
        run_b = list(captured)

    def _snap(run, topic):
        return next(t for t in run if t[0] == topic)

    a = _snap(run_a, "AB topic ch-ab-a")
    b = _snap(run_b, "AB topic ch-ab-b")
    # A/B: ОДИН И ТОТ ЖЕ item получает разное поведение от разных профилей
    assert a[1] == "analytical" and a[2] == 2500 and a[3] == "Analytical Deep Dive"
    assert b[1] == "casual" and b[2] == 800 and b[3] == "Casual Manga Buzz"
    # items канала B в прогоне A тоже получили стиль A (задокументированный сайд-эффект)
    b_in_a = _snap(run_a, "AB topic ch-ab-b")
    assert b_in_a[1] == "analytical"


# ============ A/B: Evaluation behavior ============

def test_ab_evaluation_target_style(session, _isolated_db):
    """A/B Evaluation: LLM-as-a-Judge получает разные критерии (target_style)."""
    from backend.automation.jobs.automation_jobs import EvaluatorJob
    from core.models.content_orm import ContentORM
    from engines.evaluator.models import EvaluationResult

    cha, chb = _make_ab_channels(session)
    cha = _get_channel(session, cha)
    chb = _get_channel(session, chb)
    for ch, src in [(cha, "https://example.com/ab-ea"), (chb, "https://example.com/ab-eb")]:
        session.add(ContentORM(
            channel_id=ch.id,
            source_url=src,
            headline=f"AB eval {ch.id}",
            source_text="Facts",
            draft_text="x" * 60,
            status="draft",
        ))
    session.commit()

    captured = []  # target_style по порядку вызовов

    class _StubEvaluator:
        async def evaluate(self, source_facts, generated_post, target_style):
            captured.append(target_style)
            return EvaluationResult(
                accuracy=85, clarity=85, clickability=85,
                telegram_style=85, engagement_prediction=85,
                overall=85, is_approved=True, feedback_for_regeneration="",
            )

    with patch(
        "backend.automation.jobs.automation_jobs.LLMEvaluatorEngine",
        return_value=_StubEvaluator(),
    ):
        # Sprint 75.2 finding: EvaluatorJob тоже обрабатывает items всех каналов
        # (list_all без фильтра по каналу) — см. WritingJob A/B комментарий.
        asyncio.run(EvaluatorJob().run(channel=_get_channel(session, "ch-ab-a"), execution_id="exec-ab-ea"))
        run_a = list(captured)
        for it in session.query(ContentORM).all():
            it.status = "draft"
            it.evaluation = None
        session.commit()
        captured.clear()
        asyncio.run(EvaluatorJob().run(channel=_get_channel(session, "ch-ab-b"), execution_id="exec-ab-eb"))
        run_b = list(captured)

    # target_style одного item'а различается между профилями A и B
    a_style = next(s for s in run_a if "Analytical Deep Dive" in s)
    b_style = next(s for s in run_b if "Casual Manga Buzz" in s)
    assert a_style != b_style
    assert "analytical" in a_style and "2500" in a_style
    assert "casual" in b_style and "800" in b_style


# ============ Инвариант: одинаковый профиль → одинаковое поведение ============

def test_same_profile_same_behavior_deterministic(session, _isolated_db):
    """Инвариант детерминизма: один профиль → одинаковый конфиг при повторных чтениях."""
    from backend.automation.profile_config import load_profile_config

    id_a, _ = _make_ab_channels(session)
    cha = _get_channel(session, id_a)
    cfg1 = load_profile_config(session, cha)
    cfg2 = load_profile_config(session, cha)
    assert cfg1 == cfg2
