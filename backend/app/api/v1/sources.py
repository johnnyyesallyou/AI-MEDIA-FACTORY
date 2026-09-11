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