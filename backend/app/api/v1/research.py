import logging
from backend.core.rate_limiter import rate_limit_call
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session

from core.database import get_db
from core.repositories.channel_repository import ChannelRepository
from core.repositories.content_repository import ContentRepository
from engines.research import ResearchEngine
from engines.writing import WritingEngine, ContentBrief
from engines.telegram import TelegramPublisher
from engines.writing.styles.profiles import TELEGRAM_AI_EXPERT

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/channels", tags=["research"])
content_router = APIRouter(prefix="/content", tags=["writing"])


class TopicResult(BaseModel):
    content_id: str
    title: str
    summary: str
    importance_score: float
    mention_count: int
    max_trust_score: float
    sources: List[str]
    urls: List[str]


class RunResearchResponse(BaseModel):
    channel_id: str
    channel_name: str
    total_raw_articles: int
    unique_topics: int
    high_score_topics: int
    saved_topics: int
    tokens_input: int
    topics: List[TopicResult]


class GenerateDraftResponse(BaseModel):
    content_id: str
    status: str
    draft_text: str
    model_used: str
    tokens_input: int
    tokens_output: int


@rate_limit_call("research_run", timeout=300.0)
@router.post("/{channel_id}/run-research", response_model=RunResearchResponse)
async def run_research(channel_id: str, db: Session = Depends(get_db)):
    channel_repo = ChannelRepository(db)
    channel = channel_repo.get(channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    logger.info(f"Запуск Research Pipeline для канала '{channel.name}' ({channel_id})")

    engine = ResearchEngine()
    result = engine.run()

    content_repo = ContentRepository(db)
    saved_topics = []

    for topic in result["topics"]:
        url = topic["urls"][0] if topic["urls"] else ""
        content_item = content_repo.create(
            channel_id=channel_id,
            source_url=url,
            headline=topic["title"],
            status="research",
            source_text=topic["summary"],
        )
        saved_topics.append(TopicResult(
            content_id=content_item.id,
            title=topic["title"],
            summary=topic["summary"],
            importance_score=topic["importance_score"],
            mention_count=topic["mention_count"],
            max_trust_score=topic["max_trust_score"],
            sources=topic["sources"],
            urls=topic["urls"],
        ))

    return RunResearchResponse(
        channel_id=channel.id,
        channel_name=channel.name,
        total_raw_articles=result["total_raw_articles"],
        unique_topics=result["unique_topics"],
        high_score_topics=result["high_score_topics"],
        saved_topics=len(saved_topics),
        tokens_input=result["tokens_input"],
        topics=saved_topics,
    )


@content_router.post("/{content_id}/generate-draft", response_model=GenerateDraftResponse)
async def generate_draft(content_id: str, db: Session = Depends(get_db)):
    '''
    Превращает тему (status=research) в черновик поста (status=draft) через Ollama.
    Использует headline темы как topic, а ранее сохранённый summary (в draft_text) как key_fact.
    '''
    content_repo = ContentRepository(db)
    item = content_repo.get(content_id)
    if not item:
        raise HTTPException(status_code=404, detail="Content not found")

    if item.status != "research":
        raise HTTPException(
            status_code=400,
            detail=f"Content must be in 'research' status to generate a draft, current status: '{item.status}'"
        )

    brief = ContentBrief(
        topic=item.headline,
        audience=TELEGRAM_AI_EXPERT["audience"],
        goal="Проинформировать аудиторию о новости и вызвать обсуждение",
        tone=TELEGRAM_AI_EXPERT["tone"],
        length_chars=TELEGRAM_AI_EXPERT["length_chars"],
        call_to_action="Что думаете об этом? Делитесь мнением в комментариях.",
        key_facts=[item.source_text] if item.source_text else [item.headline],
    )

    logger.info(f"Генерация черновика для content_id={content_id}, тема: {item.headline[:50]}...")

    writing_engine = WritingEngine()
    result = writing_engine.generate(brief, style_profile=TELEGRAM_AI_EXPERT)

    updated = content_repo.update_status(content_id, "draft")
    updated.draft_text = result["generated_text"]
    db.commit()
    db.refresh(updated)

    return GenerateDraftResponse(
        content_id=updated.id,
        status=updated.status,
        draft_text=updated.draft_text,
        model_used=result["model_used"],
        tokens_input=result["tokens_input"],
        tokens_output=result["tokens_output"],
    )


class PublishResponse(BaseModel):
    content_id: str
    status: str
    message_id: int
    chat_id: str


@content_router.post("/{content_id}/publish", response_model=PublishResponse)
async def publish_content(content_id: str, db: Session = Depends(get_db)):
    '''Публикует черновик (status=draft) в реальный Telegram-канал.'''
    content_repo = ContentRepository(db)
    item = content_repo.get(content_id)
    if not item:
        raise HTTPException(status_code=404, detail="Content not found")

    if item.status != "approved":
        raise HTTPException(status_code=400, detail=f"Content must be in 'approved' status before publish, current: '{item.status}'")

    if not item.channel_id:
        raise HTTPException(status_code=400, detail="Content не привязан к каналу")

    channel_repo = ChannelRepository(db)
    channel = channel_repo.get(item.channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    if not channel.is_connected or not channel.bot_token or not channel.chat_id:
        raise HTTPException(status_code=400, detail="Канал не подключён к Telegram. Сначала вызовите connect-telegram")

    publisher = TelegramPublisher(bot_token=channel.bot_token, chat_id=channel.chat_id)
    result = publisher.publish(item.draft_text or item.headline)

    content_repo.update_status(content_id, "published")

    return PublishResponse(
        content_id=item.id,
        status="published",
        message_id=result["message_id"],
        chat_id=result["chat_id"],
    )
