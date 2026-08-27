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