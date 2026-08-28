"""LLM Generator - Sprint 60.

Использует Ollama для генерации текста на основе промпта.
"""
import requests
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class LLMGenerator:
    """Генерация текста через Ollama."""

    def __init__(self, ollama_url: str = "http://host.docker.internal:11434"):
        self.ollama_url = ollama_url
        self.model = "gemma2:9b"  # или другой

    def generate(self, prompt: str, max_tokens: int = 500, temperature: float = 0.7) -> Optional[str]:
        """Сгенерировать текст по промпту."""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                    },
                },
                timeout=120,
            )
            response.raise_for_status()
            result = response.json()
            text = result.get("response", "").strip()
            logger.info(f"Generated {len(text)} chars via {self.model}")
            return text
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return None