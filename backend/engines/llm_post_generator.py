"""Sprint 69.4: LLM-based post generation для NewsGenerationStrategy."""
import logging
from backend.engines.ollama_limiter import with_ollama_limit
import os
import json
import requests
import httpx
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://host.docker.internal:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")


async def generate_news_post_llm(topic: Dict[str, Any], tone: str = "informative", max_length: int = 1200) -> Optional[str]:
    """
    Генерирует пост из topic с помощью LLM (Ollama).
    
    Args:
        topic: {"title": "...", "summary": "...", "url": "...", "source": "..."}
        tone: "informative" | "casual" | "analytical"
        max_length: максимальная длина поста
    
    Returns:
        Сгенерированный текст поста или None если LLM недоступен
    """
    prompt = f"""You are a professional news writer. Write a concise news post in Russian based on the following information.

Title: {topic.get('title', '')}
Summary: {topic.get('summary', '')}
Source: {topic.get('source', '')}

Requirements:
- Tone: {tone}
- Language: Russian
- Max length: {max_length} characters
- Include source attribution at the end
- Make it engaging and informative
- Do NOT use markdown formatting
- Do NOT add emojis unless appropriate for the tone

Write the post directly, no explanations:"""

    try:
        # Sprint 69.12: concurrency limit для предотвращения перегрузки Ollama
        async def _make_request():
            async with httpx.AsyncClient(timeout=180.0) as client:
                return await client.post(
                    f"{OLLAMA_URL}/api/generate",
                    json={
                        "model": OLLAMA_MODEL,
                        "prompt": prompt,
                        "stream": False,
                    },
                )
        
        response = await with_ollama_limit(_make_request())
        response.raise_for_status()
        
        result = response.json()
        generated_text = result.get("response", "").strip()
        
        if generated_text and len(generated_text) > 50:
            logger.info(f"LLM generated {len(generated_text)} chars for: {topic.get('title', '')[:50]}")
            return generated_text
        else:
            logger.warning("LLM returned empty or too short response")
            return None
    
    except requests.exceptions.RequestException as e:
        logger.error(f"LLM request failed: {e}")
        return None
    except Exception as e:
        logger.error(f"LLM generation error: {e}")
        return None

async def generate_generic_post_llm(
    topic: Dict[str, Any],
    archetype: str,
    tone: str = "informative",
    max_length: int = 1200,
    language: str = "Russian"
) -> Optional[str]:
    """
    Sprint 69.21: Универсальная LLM-генерация для всех архетипов.
    
    Args:
        topic: {"title": "...", "summary": "...", "url": "...", "source": "..."}
        archetype: "releases" | "educational" | "entertainment" | "viral" | "reviews" | "community" | "aggregator"
        tone: "informative" | "casual" | "analytical" | "entertaining" | "professional"
        max_length: максимальная длина поста
        language: язык генерации
    
    Returns:
        Сгенерированный текст поста или None если LLM недоступен
    """
    
    # Архетип-специфичные промпты
    archetype_prompts = {
        "releases": "You are a product release specialist. Write an engaging announcement about a new release/update.",
        "educational": "You are an educational content creator. Write an informative post that teaches something interesting.",
        "entertainment": "You are an entertainment content creator. Write a fun, engaging post about entertainment.",
        "viral": "You are a viral content specialist. Write a highly engaging, shareable post.",
        "reviews": "You are a professional reviewer. Write a balanced, informative review.",
        "community": "You are a community manager. Write a post that encourages discussion and engagement.",
        "aggregator": "You are a content curator. Write a concise summary of important information."
    }
    
    role_prompt = archetype_prompts.get(archetype, archetype_prompts["aggregator"])
    
    prompt = f"""{role_prompt}

Write a post in {language} based on the following information.

Title: {topic.get('title', '')}
Summary: {topic.get('summary', '')}
Source: {topic.get('source', '')}

Requirements:
- Tone: {tone}
- Language: {language}
- Max length: {max_length} characters
- Include source attribution at the end if URL provided
- Make it engaging and appropriate for {archetype} content
- Do NOT use markdown formatting
- Do NOT add emojis unless appropriate for the tone
- Write naturally, not like a translation

Write the post directly, no explanations:"""

    try:
        async def _make_request():
            async with httpx.AsyncClient(timeout=180.0) as client:
                return await client.post(
                    f"{OLLAMA_URL}/api/generate",
                    json={
                        "model": OLLAMA_MODEL,
                        "prompt": prompt,
                        "stream": False,
                    },
                )

        response = await with_ollama_limit(_make_request())
        response.raise_for_status()

        result = response.json()
        generated_text = result.get("response", "").strip()

        if generated_text and len(generated_text) > 50:
            logger.info(f"LLM generated {len(generated_text)} chars for {archetype}: {topic.get('title', '')[:50]}")
            return generated_text
        else:
            logger.warning(f"LLM returned empty or too short response for {archetype}")
            return None

    except Exception as e:
        logger.error(f"LLM generation error for {archetype}: {e}")
        return None
