from backend.engines import register_all  # Sprint 69.21: регистрирует все стратегии
from backend.engines.vk_publishing_strategy import VkPublishingStrategy
"""Sprint 67.3: Universal Content Pipeline.

Единый движок для всех типов каналов.
Принимает Channel + ChannelProfile → выбирает стратегии → выполняет pipeline.

Заменяет отдельные pipelines (news/manga/anime) через Strategy Registry.
"""
import logging
import time
from backend.engines.deduplicator import filter_new_topics
from typing import Optional, Dict, Any, List, Protocol
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


class ResearchStrategy(Protocol):
    """Протокол для стратегии research."""
    def __init__(self, profile: Any): ...
    async def collect_sources(self) -> List[Dict[str, Any]]: ...
    async def extract_topics(self, sources: List[Dict]) -> List[Dict[str, Any]]: ...


class GenerationStrategy(Protocol):
    """Протокол для стратегии генерации контента."""
    def __init__(self, profile: Any): ...
    async def generate_post(self, topic: Dict[str, Any]) -> Optional[Dict[str, Any]]: ...


class MediaStrategy(Protocol):
    """Протокол для стратегии медиа."""
    def __init__(self, profile: Any): ...
    async def select_media(self, post: Dict[str, Any]) -> Optional[str]: ...


class PublishingStrategy(Protocol):
    """Протокол для стратегии публикации."""
    def __init__(self, profile: Any): ...
    async def publish(self, post: Dict[str, Any], media_url: Optional[str]) -> Dict[str, Any]: ...


@dataclass
class PipelineResult:
    """Результат выполнения pipeline."""
    success: bool
    posts_generated: int = 0
    posts_published: int = 0
    errors: List[str] = field(default_factory=list)
    duration_seconds: float = 0.0
    topics_found: int = 0
    # Sprint 73.1: тайминги по стадиям (секунды)
    stage_timings: Dict[str, float] = field(default_factory=dict)
    # Sprint 73.3: сквозной execution_id + агрегированные LLM-метрики
    execution_id: str = ""
    llm_metrics: Dict[str, Any] = field(default_factory=dict)

    def stage_summary(self) -> str:
        """Sprint 73.1: человекочитаемая сводка по стадиям с процентами."""
        total = sum(self.stage_timings.values()) or 1.0
        parts = [
            f"{name}={secs:.1f}s ({secs / total * 100:.1f}%)"
            for name, secs in self.stage_timings.items()
        ]
        return " | ".join(parts)


class UniversalContentPipeline:
    """
    Универсальный pipeline для любого типа канала.
    
    Архитектура:
        Channel + ChannelProfile
              ↓
        ResearchStrategy → GenerationStrategy → MediaStrategy → PublishingStrategy
    """
    
    def __init__(self, channel: Any, profile: Any):
        self.channel = channel
        self.profile = profile
        self._strategies: Dict[str, Any] = {}
    
    def set_strategy(self, name: str, strategy: Any) -> None:
        """Установить стратегию по имени (research/generation/media/publishing)."""
        self._strategies[name] = strategy
        logger.info(f"Strategy '{name}' set: {type(strategy).__name__}")
    
    def get_strategy(self, name: str) -> Optional[Any]:
        """Получить стратегию по имени."""
        return self._strategies.get(name)
    
    async def run(self) -> PipelineResult:
        """Выполнить полный pipeline: research → generation → media → publish."""
        start_time = datetime.utcnow()
        result = PipelineResult(success=True)

        # Sprint 73.3: сквозной execution_id (совместим с execution_logs) + LLM-метрики
        from core.metrics.llm_metrics import start_llm_collection
        channel_key = str(getattr(self.channel, "id", ""))[:8]
        result.execution_id = f"{start_time.strftime('%Y%m%d-%H%M%S')}-{channel_key}"
        llm_collector = start_llm_collection()

        try:
            # 1. Research phase
            logger.info(f"[1/4] Research for channel {self.channel.name}")
            research = self.get_strategy("research")
            if not research:
                raise ValueError("ResearchStrategy not set")
            
            _stage_start = time.perf_counter()
            sources = await research.collect_sources()
            topics = await research.extract_topics(sources)
            
            # Sprint 69.6: дедупликация — пропускаем уже опубликованные темы
            original_count = len(topics)
            topics = filter_new_topics(channel_id=self.channel.id, topics=topics)
            result.stage_timings["research"] = time.perf_counter() - _stage_start
            logger.info(f"Dedup: {original_count} topics → {len(topics)} new")
            result.topics_found = len(topics)
            logger.info(f"[1/4] Research done: {len(topics)} topics")
            
            # 2. Generation phase
            logger.info(f"[2/4] Generation for {len(topics)} topics")
            generation = self.get_strategy("generation")
            if not generation:
                raise ValueError("GenerationStrategy not set")
            
            posts = []
            _stage_start = time.perf_counter()
            for topic in topics:
                try:
                    post = await generation.generate_post(topic)
                    if post:
                        posts.append(post)
                except Exception as e:
                    logger.error(f"Generation failed: {e}")
                    result.errors.append(f"generation: {str(e)}")
            result.stage_timings["writing"] = time.perf_counter() - _stage_start
            
            result.posts_generated = len(posts)
            logger.info(f"[2/4] Generation done: {len(posts)} posts")
            
            # 3. Media phase
            logger.info(f"[3/4] Media selection for {len(posts)} posts")
            media = self.get_strategy("media")
            if not media:
                raise ValueError("MediaStrategy not set")
            
            _stage_start = time.perf_counter()
            for post in posts:
                try:
                    media_url = await media.select_media(post)
                    post["media_url"] = media_url
                except Exception as e:
                    logger.warning(f"Media selection failed: {e}")
            result.stage_timings["media"] = time.perf_counter() - _stage_start
            
            # 4. Publishing phase
            logger.info(f"[4/4] Publishing for {len(posts)} posts")
            publishing = self.get_strategy("publishing")
            if not publishing:
                raise ValueError("PublishingStrategy not set")
            
            published_count = 0
            _stage_start = time.perf_counter()
            for post in posts:
                try:
                    pub_result = await publishing.publish(post, post.get("media_url"))
                    if pub_result.get("success"):
                        published_count += 1
                except Exception as e:
                    logger.error(f"Publishing failed: {e}")
                    result.errors.append(f"publishing: {str(e)}")
            result.stage_timings["publishing"] = time.perf_counter() - _stage_start
            
            result.posts_published = published_count
            logger.info(f"[4/4] Publishing done: {published_count} published")
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            result.success = False
            result.errors.append(f"pipeline: {str(e)}")
        
        result.duration_seconds = (datetime.utcnow() - start_time).total_seconds()
        # Sprint 73.3: агрегированные LLM-метрики прогона
        result.llm_metrics = llm_collector.to_dict()
        logger.info(
            f"Pipeline completed in {result.duration_seconds:.1f}s: "
            f"{result.topics_found} topics, {result.posts_generated} generated, "
            f"{result.posts_published} published, {len(result.errors)} errors"
        )
        # Sprint 73.1: разбивка по стадиям
        if result.stage_timings:
            logger.info(f"Pipeline stage timings [{self.channel.name}]: {result.stage_summary()}")
        # Sprint 73.3: LLM-сводка
        logger.info(
            f"Pipeline LLM metrics [{result.execution_id}]: "
            f"calls={llm_collector.llm_calls}, avg={llm_collector.avg_latency_ms}ms, "
            f"tokens_in={llm_collector.tokens_in}, tokens_out={llm_collector.tokens_out}, "
            f"model={llm_collector.llm_model}, errors={llm_collector.llm_errors}"
        )
        
        return result