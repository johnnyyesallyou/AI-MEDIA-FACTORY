from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime

router = APIRouter(prefix="/ai", tags=["ai_models"])

# === МОДЕЛИ ===

class ModelInfo(BaseModel):
    id: str
    name: str
    provider: str
    context_window: int
    is_active: bool = True

class TaskRoutingUpdate(BaseModel):
    '''Схема для изменения модели для конкретной задачи без изменения кода.'''
    task_name: str # research, writing, fact_check, evaluator
    model_id: str
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)

class RoutingConfigResponse(BaseModel):
    task_name: str
    current_model_id: str
    fallback_model_id: Optional[str]
    temperature: float
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# === IN-MEMORY БД ДЛЯ ДЕМО ===
_available_models = {
    "qwen3-32b": ModelInfo(id="qwen3-32b", name="Qwen3 32B", provider="ollama", context_window=32768),
    "gpt-oss": ModelInfo(id="gpt-oss", name="GPT OSS Mini", provider="openai", context_window=8192),
    "gemma-27b": ModelInfo(id="gemma-27b", name="Gemma 27B", provider="ollama", context_window=8192),
    "deepseek-chat": ModelInfo(id="deepseek-chat", name="DeepSeek Chat", provider="deepseek", context_window=32768)
}

_current_routing = {
    "research": {"model_id": "gpt-oss", "fallback": "deepseek-chat", "temperature": 0.2},
    "writing": {"model_id": "qwen3-32b", "fallback": "gpt-oss", "temperature": 0.7},
    "fact_check": {"model_id": "gemma-27b", "fallback": "qwen3-32b", "temperature": 0.1},
    "evaluator": {"model_id": "deepseek-chat", "fallback": "gemma-27b", "temperature": 0.3}
}

# === ENDPOINTS ===

@router.get("/models", response_model=List[ModelInfo])
async def list_available_models():
    '''Получить список всех доступных LLM моделей.'''
    return list(_available_models.values())

@router.get("/routing", response_model=Dict[str, RoutingConfigResponse])
async def get_current_routing():
    '''Посмотреть, какая модель используется для каждой задачи прямо сейчас.'''
    return {
        task: RoutingConfigResponse(
            task_name=task,
            current_model_id=cfg["model_id"],
            fallback_model_id=cfg["fallback"],
            temperature=cfg["temperature"]
        )
        for task, cfg in _current_routing.items()
    }

@router.put("/routing", response_model=RoutingConfigResponse)
async def update_task_routing(update: TaskRoutingUpdate):
    '''
    Изменить модель для задачи (например, переключить Writing с Qwen3 на GPT-4o).
    Вступает в силу мгновенно, без перезапуска системы.
    '''
    if update.task_name not in _current_routing:
        raise HTTPException(status_code=404, detail="Task not found")
    if update.model_id not in _available_models:
        raise HTTPException(status_code=400, detail="Model not available")
    
    _current_routing[update.task_name] = {
        "model_id": update.model_id,
        "fallback": _current_routing[update.task_name]["fallback"],
        "temperature": update.temperature
    }
    
    return RoutingConfigResponse(
        task_name=update.task_name,
        current_model_id=update.model_id,
        fallback_model_id=_current_routing[update.task_name]["fallback"],
        temperature=update.temperature
    )
