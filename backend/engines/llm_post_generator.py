"""Sprint 69.4: LLM-based post generation для NewsGenerationStrategy."""
import logging
import os
import json
import requests
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
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
            },
            timeout=60,
        )
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