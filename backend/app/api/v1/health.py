"""Health check endpoints."""
import requests
import os
import time
from sqlalchemy import text
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/health", tags=["health"])


class OllamaHealthResponse(BaseModel):
    """Ответ проверки здоровья Ollama."""
    status: str  # "ok" | "error"
    url: str
    models: list[str] = []
    message: Optional[str] = None
    response_time_ms: Optional[int] = None


@router.get("/ollama", response_model=OllamaHealthResponse)
async def check_ollama_health():
    """
    Sprint 10: Проверяет доступность локального Ollama сервера.
    
    Возвращает:
        - status: "ok" или "error"
        - url: URL Ollama
        - models: список доступных models
        - response_time_ms: время ответа
    """
    ollama_url = os.environ.get("OLLAMA_URL", "http://host.docker.internal:11434")
    
    start = time.time()
    
    try:
        # Проверяем доступность Ollama
        r = requests.get(f"{ollama_url}/api/tags", timeout=5)
        r.raise_for_status()
        
        response_time_ms = int((time.time() - start) * 1000)
        data = r.json()
        models = [m.get("name", "unknown") for m in data.get("models", [])]
        
        return OllamaHealthResponse(
            status="ok",
            url=ollama_url,
            models=models,
            response_time_ms=response_time_ms,
            message=f"Ollama is available. {len(models)} models"
        )
        
    except requests.exceptions.Timeout:
        return OllamaHealthResponse(
            status="error",
            url=ollama_url,
            message=f"Timeout: Ollama not responding within 5s"
        )
    except requests.exceptions.ConnectionError as e:
        return OllamaHealthResponse(
            status="error",
            url=ollama_url,
            message=f"ConnectionError: {str(e)}"
        )
    except Exception as e:
        return OllamaHealthResponse(
            status="error",
            url=ollama_url,
            message=f"Error: {str(e)}"
        )


@router.get("/postgres")
async def check_postgres_health():
    """Проверяет доступность PostgreSQL."""
    from core.database import SessionLocal
    start = time.time()
    
    try:
        db = SessionLocal()
        # Простой запрос для проверки соединения
        db.execute(text("SELECT 1"))
        db.close()
        response_time_ms = int((time.time() - start) * 1000)
        return {
            "status": "ok",
            "message": "PostgreSQL is available",
            "response_time_ms": response_time_ms
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Ошибка: {str(e)}"
        }


@router.get("/redis")
async def check_redis_health():
    """Проверяет доступность Redis."""
    start = time.time()
    try:
        import redis
        r = redis.Redis(
            host=os.environ.get("REDIS_HOST", "redis"),
            port=int(os.environ.get("REDIS_PORT", 6379)),
            socket_timeout=3
        )
        r.ping()
        response_time_ms = int((time.time() - start) * 1000)
        return {
            "status": "ok",
            "message": "Redis is available",
            "response_time_ms": response_time_ms
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Ошибка: {str(e)}"
        }
