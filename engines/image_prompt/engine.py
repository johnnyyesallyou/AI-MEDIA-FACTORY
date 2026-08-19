"""Image Prompt Generator Engine - создает КОРОТКИЕ английские промпты."""
import logging
import requests
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ImagePromptEngine:
    """
    Sprint 11: Генерирует КОРОТКИЕ английские промпты для Image Generator.
    
    ВАЖНО: Промпты должны быть короткими (< 100 символов) и на английском,
    чтобы URL не был слишком длинным для Pollinations AI.
    """
    
    OLLAMA_URL = "http://host.docker.internal:11434/api/generate"
    
    def __init__(self, model: str = "mistral-nemo:12b"):
        self.model = model
    
    def _call_ollama(self, prompt: str) -> str:
        """Прямой вызов Ollama API."""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 50
                }
            }
            
            response = requests.post(self.OLLAMA_URL, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            return data.get("response", "").strip()
        
        except Exception as e:
            logger.error(f"Ollama call failed: {e}")
            raise
    
    def generate_prompt(
        self,
        headline: str,
        text: str,
        platform: str = "telegram",
        language: str = "en",
        style: str = "anime"
    ) -> Dict[str, Any]:
        """
        Генерирует КОРОТКИЙ английский промпт (< 100 символов).
        """
        try:
            # Переводим headline на английский и сокращаем
            translation_prompt = f"""Translate this Russian anime news headline to English and create a SHORT image prompt (max 10 words). Output ONLY the prompt, no explanations.

Headline: {headline}

Short English image prompt:"""
            
            prompt = self._call_ollama(translation_prompt)
            
            # Очищаем и ограничиваем длину
            prompt = prompt.strip().strip('"').strip("'")
            if len(prompt) > 100:
                prompt = prompt[:100]
            
            # Добавляем стиль
            prompt = f"{prompt}, anime style, high quality"
            
            logger.info(f"Generated SHORT prompt: {prompt}")
            
            return {
                "prompt": prompt,
                "negative_prompt": "text, letters, watermark, blurry",
                "style": style,
                "platform": platform,
                "language": "en"
            }
        
        except Exception as e:
            logger.exception(f"ImagePromptEngine failed: {e}")
            # Fallback: очень короткий промпт
            return {
                "prompt": "anime scene, high quality",
                "negative_prompt": "text, letters, watermark",
                "style": style,
                "platform": platform,
                "language": "en"
            }
    
    def generate_anime_prompt(self, anime_title: str, context: str = "") -> Dict[str, Any]:
        """Специализированный промпт для аниме."""
        return {
            "prompt": f"{anime_title}, anime poster, high quality",
            "negative_prompt": "text, letters, watermark",
            "style": "anime",
            "platform": "telegram",
            "language": "en"
        }