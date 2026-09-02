"""Sprint 69.12: Ollama Concurrency Limiter — предотвращает перегрузку LLM."""
import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Semaphore для ограничения параллельных LLM calls
_ollama_semaphore: Optional[asyncio.Semaphore] = None


def get_ollama_semaphore(max_concurrent: int = 2) -> asyncio.Semaphore:
    """
    Возвращает semaphore для ограничения параллельных вызовов Ollama.
    
    Args:
        max_concurrent: максимум параллельных LLM calls (default: 2)
    
    Returns:
        asyncio.Semaphore
    """
    global _ollama_semaphore
    if _ollama_semaphore is None:
        _ollama_semaphore = asyncio.Semaphore(max_concurrent)
        logger.info(f"Ollama concurrency limiter initialized: max_concurrent={max_concurrent}")
    return _ollama_semaphore


async def with_ollama_limit(coro):
    """
    Wrapper для вызова Ollama с concurrency limit.
    
    Usage:
        result = await with_ollama_limit(generate_news_post_llm(topic))
    """
    semaphore = get_ollama_semaphore()
    async with semaphore:
        logger.debug("Acquired Ollama semaphore")
        try:
            result = await coro
            return result
        finally:
            logger.debug("Released Ollama semaphore")