from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/settings", tags=["settings"])

# === МОДЕЛИ ===

class GlobalSettings(BaseModel):
    ui_language: str = "ru"
    ui_theme: str = "dark" # dark, light
    timezone: str = "Europe/Moscow"
    auto_backup_enabled: bool = True
    backup_cron: str = "0 3 * * *" # Каждый день в 3:00
    check_updates: bool = True

class EnvVarItem(BaseModel):
    key: str
    value_masked: str # Реальное значение не отдается в API из соображений безопасности
    description: str = ""

class BackupResponse(BaseModel):
    status: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# === ЗАГЛУШКИ ДАННЫХ ===
_current_settings = GlobalSettings()

_env_vars_db = [
    EnvVarItem(key="OPENAI_API_KEY", value_masked="sk-...****", description="Ключ для OpenAI API"),
    EnvVarItem(key="TELEGRAM_BOT_TOKEN", value_masked="712...****", description="Токен бота"),
    EnvVarItem(key="POSTGRES_URL", value_masked="postgresql://...****", description="Строка подключения к БД")
]

# === ENDPOINTS ===

@router.get("/", response_model=GlobalSettings)
async def get_global_settings():
    '''Получить глобальные настройки интерфейса и системы.'''
    return _current_settings

@router.put("/", response_model=GlobalSettings)
async def update_global_settings(settings: GlobalSettings):
    '''Обновить глобальные настройки.'''
    global _current_settings
    _current_settings = settings
    return _current_settings

@router.get("/env", response_model=List[EnvVarItem])
async def list_env_variables():
    '''Получить список переменных окружения (значения замаскированы).'''
    return _env_vars_db

@router.post("/backup", response_model=BackupResponse)
async def trigger_backup():
    '''Вручную запустить резервное копирование базы данных.'''
    # В реальности здесь будет вызов скрипта pg_dump
    return BackupResponse(status="started", message="Backup process initiated successfully")
