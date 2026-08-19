import pathlib, py_compile

f = pathlib.Path('./backend/app/api/v1/health.py')

# Создаём новый файл health.py (если нет)
if not f.exists():
    content = '''"""Health check endpoints."""
import requests
import os
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
        - models: список доступных моделей
        - response_time_ms: время ответа
    """
    ollama_url = os.environ.get("OLLAMA_URL", "http://host.docker.internal:11434")
    
    import time
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
            message=f"Ollama доступен. {len(models)} моделей"
        )
        
    except requests.exceptions.Timeout:
        return OllamaHealthResponse(
            status="error",
            url=ollama_url,
            message=f"Timeout: Ollama не отвечает за 5 секунд"
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
            message=f"Ошибка: {str(e)}"
        )


@router.get("/postgres")
async def check_postgres_health():
    """Проверяет доступность PostgreSQL."""
    from core.database import SessionLocal
    start = time.time()
    
    try:
        db = SessionLocal()
        # Простой запрос для проверки соединения
        db.execute("SELECT 1")
        db.close()
        response_time_ms = int((time.time() - start) * 1000)
        return {
            "status": "ok",
            "message": "PostgreSQL доступен",
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
            "message": "Redis доступен",
            "response_time_ms": response_time_ms
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Ошибка: {str(e)}"
        }
'''
    f.write_text(content, encoding='utf-8')
    print("✅ Создан backend/app/api/v1/health.py")
else:
    print("ℹ️ health.py уже существует")

# Регистрируем router в main router (если ещё не зарегистрирован)
router_file = pathlib.Path('./backend/app/api/v1/router.py')
if router_file.exists():
    rs = router_file.read_text(encoding='utf-8')
    if 'health' not in rs:
        # Добавляем импорт и include
        rs = rs.replace(
            'from .workflows import router as workflows_router',
            'from .workflows import router as workflows_router\nfrom .health import router as health_router',
            1
        )
        rs = rs.replace(
            'api_router.include_router(workflows_router)',
            'api_router.include_router(workflows_router)\napi_router.include_router(health_router)',
            1
        )
        router_file.write_text(rs, encoding='utf-8')
        print("✅ Health router зарегистрирован в api_router")

# Проверяем синтаксис
try:
    py_compile.compile(str(f), doraise=True)
    print("✅✅✅ Синтаксис health.py валиден! ✅✅✅")
except py_compile.PyCompileError as e:
    print(f"❌ Ошибка: {e}")