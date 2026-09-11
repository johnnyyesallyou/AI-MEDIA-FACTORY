"""Sources Registry API - Sprint 53.

Эндпоинты для получения списка доступных источников.
"""
from fastapi import APIRouter, Query
from typing import List, Optional
from pydantic import BaseModel

from engines.source_registry import SourceRegistry, SourceDefinition

router = APIRouter(prefix="/sources", tags=["sources"])


class SourceResponse(BaseModel):
    id: str
    name: str
    content_types: List[str]
    topics: List[str]
    languages: List[str]
    capabilities: List[str]
    requires_api_key: bool
    rate_limit: int

    @classmethod
    def from_definition(cls, src: SourceDefinition) -> "SourceResponse":
        return cls(
            id=src.id,
            name=src.name,
            content_types=list(src.content_types),
            topics=list(src.topics),
            languages=list(src.languages),
            capabilities=list(src.capabilities),
            requires_api_key=src.requires_api_key,
            rate_limit=src.rate_limit,
        )


@router.get("/", response_model=List[SourceResponse])
def list_sources(
    content_type: Optional[str] = Query(None, description="Filter by content type"),
    topic: Optional[str] = Query(None, description="Filter by topic"),
    language: Optional[str] = Query(None, description="Filter by language"),
):
    """
    Получить список всех доступных источников.
    
    Можно фильтровать по content_type, topic, language.
    """
    if content_type:
        sources = SourceRegistry.get_sources_for(content_type, topic, language)
    else:
        sources = SourceRegistry.list_all()
    
    return [SourceResponse.from_definition(s) for s in sources]


@router.get("/{source_id}", response_model=SourceResponse)
def get_source(source_id: str):
    """Получить информацию о конкретном источнике."""
    source = SourceRegistry.get_source(source_id)
    if not source:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Source '{source_id}' not found")
    return SourceResponse.from_definition(source)


@router.post("/validate")
def validate_sources(source_ids: List[str]):
    """Валидировать список source IDs."""
    valid, invalid = SourceRegistry.validate_sources(source_ids)
    return {
        "valid": valid,
        "invalid": invalid,
        "all_valid": len(invalid) == 0,
    }


# ---------------------------------------------------------------------------
# Sprint 76.1: Source Discovery — scoring, рекомендации, RSS-валидация
# ---------------------------------------------------------------------------

class RecommendSource(BaseModel):
    source_id: str
    name: str
    score: float
    content_type: str
    capabilities: List[str]
    matched_capabilities: List[str]
    reason: str


class DiscoverRecommendResponse(BaseModel):
    content_type: str
    topic: Optional[str] = None
    language: Optional[str] = None
    results: List[RecommendSource]


class FeedValidationResponse(BaseModel):
    url: str
    is_valid: bool
    feed_type: str
    title: Optional[str] = None
    item_count: int = 0
    error: Optional[str] = None


class DiscoverValidateRequest(BaseModel):
    urls: List[str]


class DiscoverValidateResponse(BaseModel):
    results: List[FeedValidationResponse]


@router.get("/discover/recommend", response_model=DiscoverRecommendResponse)
def discover_recommend(
    content_type: str = Query(..., description="Content type (e.g. 'news', 'manga', 'anime')"),
    topic: Optional[str] = Query(None, description="Topic filter"),
    language: Optional[str] = Query(None, description="Language filter"),
    top_k: Optional[int] = Query(None, ge=1, le=30, description="Limit results"),
):
    """Автоматические рекомендации источников под content_type (source scoring)."""
    from engines.source_scoring import SourceDiscoveryEngine
    results = SourceDiscoveryEngine.recommend(
        content_type=content_type, topic=topic, language=language, top_k=top_k,
    )
    return DiscoverRecommendResponse(
        content_type=content_type,
        topic=topic,
        language=language,
        results=[
            RecommendSource(
                source_id=r.source_id,
                name=r.name,
                score=r.score,
                content_type=r.content_type,
                capabilities=list(r.capabilities),
                matched_capabilities=list(r.matched_capabilities),
                reason=r.reason,
            )
            for r in results
        ],
    )


@router.post("/discover/validate", response_model=DiscoverValidateResponse)
def discover_validate(req: DiscoverValidateRequest):
    """Проверить список URL как RSS/Atom фиды."""
    from engines.source_validation import validate_feed
    results = [validate_feed(url) for url in req.urls]
    return DiscoverValidateResponse(
        results=[FeedValidationResponse(
            url=r.url,
            is_valid=r.is_valid,
            feed_type=r.feed_type,
            title=r.title,
            item_count=r.item_count,
            error=r.error,
        ) for r in results],
    )


# ---------------------------------------------------------------------------
# Sprint 76.2: Smart Source Selection — quality / rotation / diversity
# ---------------------------------------------------------------------------

class SelectSourceItem(BaseModel):
    source_id: str
    name: str
    base_score: float
    quality_adjustment: float
    final_score: float
    languages: List[str]
    matched_capabilities: List[str]
    reasons: List[str]


class SourceSelectResponse(BaseModel):
    content_type: str
    topic: Optional[str] = None
    language: Optional[str] = None
    results: List[SelectSourceItem]


class SourceMetricsRequest(BaseModel):
    source_id: str
    outcome: str  # "success" | "failure"
    items: int = 0


class SourceMetricsResponse(BaseModel):
    source_id: str
    success_count: int
    failure_count: int
    success_rate: Optional[float]
    quality_adjustment: float


class SourceRecordPickRequest(BaseModel):
    source_id: str


@router.get("/discover/select", response_model=SourceSelectResponse)
def source_select(
    content_type: str = Query(..., description="Content type (e.g. 'news', 'manga')"),
    topic: Optional[str] = Query(None),
    language: Optional[str] = Query(None),
    top_k: Optional[int] = Query(None, ge=1, le=30),
    diversity: bool = Query(True),
    rotation: bool = Query(True),
):
    """Smart Source Selection: score + quality + rotation + diversity."""
    from engines.source_selection import SmartSourceSelector
    results = SmartSourceSelector().select(
        content_type=content_type, topic=topic, language=language,
        top_k=top_k, diversity=diversity, rotation=rotation,
    )
    return SourceSelectResponse(
        content_type=content_type,
        topic=topic,
        language=language,
        results=[
            SelectSourceItem(
                source_id=r.source_id,
                name=r.name,
                base_score=r.base_score,
                quality_adjustment=r.quality_adjustment,
                final_score=r.final_score,
                languages=list(r.languages),
                matched_capabilities=list(r.matched_capabilities),
                reasons=list(r.reasons),
            )
            for r in results
        ],
    )


@router.post("/metrics", response_model=SourceMetricsResponse)
def source_metrics(req: SourceMetricsRequest):
    """Записать результат обращения к источнику (для quality scoring)."""
    from engines.source_selection import DEFAULT_REGISTRY
    q = DEFAULT_REGISTRY.record(req.source_id, req.outcome, req.items)
    return SourceMetricsResponse(
        source_id=req.source_id,
        success_count=q.success_count,
        failure_count=q.failure_count,
        success_rate=q.success_rate,
        quality_adjustment=DEFAULT_REGISTRY.quality_adjustment(req.source_id),
    )


@router.post("/select/record-pick")
def source_record_pick(req: SourceRecordPickRequest):
    """Учесть выбор источника (для ротации). Сообщить новый selection_count."""
    from engines.source_selection import DEFAULT_REGISTRY
    q = DEFAULT_REGISTRY.bump_selection(req.source_id)
    return {"source_id": req.source_id, "selection_count": q.selection_count}


# ---------------------------------------------------------------------------
# Sprint 76.3: Subscribe.ru Discovery Integration
# ---------------------------------------------------------------------------

class DiscoveredSourceResponse(BaseModel):
    url: str
    name: str
    source_type: str  # "subscribe_ru", "known_sources"
    language: str
    category: Optional[str] = None
    description: Optional[str] = None
    is_rss_validated: bool
    feed_type: Optional[str] = None
    item_count: int
    quality_score: float


class SubscribeRuDiscoverRequest(BaseModel):
    topic: str = Query(..., description="Search query (e.g. 'python', 'новости')")
    language: str = Query("ru", description="Language code")
    content_type: Optional[str] = Query(None, description="Content type filter")
    validate_feeds: bool = Query(True, description="Validate feeds as RSS/Atom")
    top_k: Optional[int] = Query(None, ge=1, le=50, description="Limit results")


class SubscribeRuDiscoverResponse(BaseModel):
    topic: str
    language: str
    content_type: Optional[str] = None
    discovered_count: int
    validated_count: int
    results: List[DiscoveredSourceResponse]


@router.post("/discover/subscribe-ru", response_model=SubscribeRuDiscoverResponse)
def discover_subscribe_ru(
    topic: str = Query(..., description="Search query"),
    language: str = Query("ru", description="Language"),
    content_type: Optional[str] = Query(None, description="Content type"),
    validate_feeds: bool = Query(True, description="Validate as RSS"),
    top_k: Optional[int] = Query(None, ge=1, le=50, description="Limit"),
):
    """Discover источники через Subscribe.ru.

    Находит RSS-фиды через Subscribe.ru, валидирует их и возвращает отсортированный список.
    При ошибке Subscribe.ru использует fallback на известные источники.
    """
    from engines.source_discovery_integrator import SourceDiscoveryIntegrator

    discovered = SourceDiscoveryIntegrator.discover_and_normalize(
        topic=topic,
        language=language,
        content_type=content_type,
        validate_feeds=validate_feeds,
        top_k=top_k,
    )

    validated_count = sum(1 for s in discovered if s.is_rss_validated)

    return SubscribeRuDiscoverResponse(
        topic=topic,
        language=language,
        content_type=content_type,
        discovered_count=len(discovered),
        validated_count=validated_count,
        results=[
            DiscoveredSourceResponse(
                url=s.url,
                name=s.name,
                source_type=s.source_type,
                language=s.language,
                category=s.category,
                description=s.description,
                is_rss_validated=s.is_rss_validated,
                feed_type=s.feed_type,
                item_count=s.item_count,
                quality_score=s.quality_score,
            )
            for s in discovered
        ],
    )