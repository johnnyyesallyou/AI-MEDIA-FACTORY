from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/automation", tags=["automation"])

# === МОДЕЛИ ===

class EngineToggles(BaseModel):
    research: bool = True
    decision: bool = True
    writing: bool = True
    image: bool = True
    fact_checker: bool = True
    evaluator: bool = True
    auto_publish: bool = False

class AutomationConfig(BaseModel):
    is_global_automation_on: bool = True
    research_interval_minutes: int = Field(default=30, ge=5, le=1440)
    publish_times: List[str] = Field(default=["09:00", "13:00", "17:00", "21:00"])
    max_posts_per_day: int = Field(default=5, ge=1, le=20)
    engines: EngineToggles = EngineToggles()
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# === IN-MEMORY БД ===
_automation_config = AutomationConfig()

# === ENDPOINTS ===

@router.get("/", response_model=AutomationConfig)
async def get_automation_settings():
    '''Получить текущие настройки автоматизации.'''
    return _automation_config

@router.put("/", response_model=AutomationConfig)
async def update_automation_settings(config: AutomationConfig):
    '''
    Обновить настройки автоматизации.
    Позволяет включать/отключать этапы пайплайна и менять расписание.
    '''
    global _automation_config
    _automation_config = config
    _automation_config.updated_at = datetime.utcnow()
    return _automation_config
