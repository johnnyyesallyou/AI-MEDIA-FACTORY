from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Literal
from datetime import datetime

router = APIRouter(prefix="/integrations", tags=["integrations"])

# === МОДЕЛИ ===

IntegrationStatus = Literal["connected", "disconnected", "error", "checking"]

class IntegrationItem(BaseModel):
    id: str
    name: str
    category: str # platform, ai_model, infrastructure
    status: IntegrationStatus
    last_checked: datetime = Field(default_factory=datetime.utcnow)
    details: str = ""

class IntegrationListResponse(BaseModel):
    total: int
    items: List[IntegrationItem]

# === ЗАГЛУШКИ ДАННЫХ ===
_integrations_db = [
    IntegrationItem(id="tg", name="Telegram", category="platform", status="connected", details="Bot active"),
    IntegrationItem(id="vk", name="VK", category="platform", status="disconnected", details="Not configured"),
    IntegrationItem(id="yt", name="YouTube", category="platform", status="disconnected", details="Not configured"),
    IntegrationItem(id="ig", name="Instagram", category="platform", status="disconnected", details="Not configured"),
    IntegrationItem(id="ollama", name="Ollama", category="ai_model", status="connected", details="v0.1.45, 4 models loaded"),
    IntegrationItem(id="comfyui", name="ComfyUI", category="ai_model", status="connected", details="Port 8188 OK"),
    IntegrationItem(id="pg", name="Postgres", category="infrastructure", status="connected", details="16.1, 3 connections"),
    IntegrationItem(id="redis", name="Redis", category="infrastructure", status="connected", details="v7.2, 12MB used"),
    IntegrationItem(id="qdrant", name="Qdrant", category="infrastructure", status="connected", details="v1.7.4, 2 collections"),
    IntegrationItem(id="minio", name="MinIO", category="infrastructure", status="connected", details="S3 OK, 450MB used"),
    IntegrationItem(id="openrouter", name="OpenRouter", category="ai_model", status="connected", details="API key valid"),
    IntegrationItem(id="openai", name="OpenAI", category="ai_model", status="error", details="Rate limit exceeded")
]

# === ENDPOINTS ===

@router.get("/", response_model=IntegrationListResponse)
async def list_integrations():
    '''Получить список всех интеграций и их текущий статус.'''
    return IntegrationListResponse(total=len(_integrations_db), items=_integrations_db)

@router.post("/{integration_id}/check", response_model=IntegrationItem)
async def check_integration(integration_id: str):
    '''Принудительно проверить статус конкретного подключения.'''
    for item in _integrations_db:
        if item.id == integration_id:
            item.status = "checking"
            # В реальности здесь будет пинг сервиса
            item.status = "connected" 
            item.last_checked = datetime.utcnow()
            return item
    return {"message": "Integration not found"}
