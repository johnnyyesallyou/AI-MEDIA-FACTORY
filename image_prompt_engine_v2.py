"""Image Prompt Generator Engine - создает промпты для генерации картинок."""
import logging
import requests
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ImagePromptEngine:
    """
    Sprint 11: Генерирует промпты для Image Generator через Ollama API.
    
    Использует Ollama (mistral-nemo:12b) для создания детальных промптов.
    """
    
    OLLAMA_URL = "http://host.docker.internal:11434/api/generate"
    
    def __init__(self, model: str = "mistral-nemo:12b"):
        self.model = model
    
    def _call_ollama(self, system_prompt: str, user_prompt: str) -> str:
        """Прямой вызов Ollama API."""
        try:
            payload = {
                "model": self.model,
                "prompt": f"{system_prompt}\n\n{user_prompt}",
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 200
                }
            }
            
            response = requests.post(self.OLLAMA_URL, json=payload, timeout=60)
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
        style: str = "minimal"
    ) -> Dict[str, Any]:
        """
        Генерирует промпт для Image Generator.
        """
        try:
            system_prompt = f"""You are an expert image prompt engineer for {platform} posts.

Generate a detailed, high-quality image prompt based on the post content.

Requirements:
- Language: {language}
- Style: {style}
- Aspect ratio: 16:9 for {platform}
- NO TEXT in the image (text will be added separately)
- High quality, professional illustration
- Relevant to the post topic

Output ONLY the image prompt (no explanations, no markdown)."""
            
            user_prompt = f"""Post headline: {headline}

Post text: {text[:500]}

Generate an image prompt that visually represents this content."""
            
            prompt = self._call_ollama(system_prompt, user_prompt)
            
            # Добавляем технические параметры
            if "no text" not in prompt.lower():
                prompt += ", no text, no letters, no words"
            
            if "high quality" not in prompt.lower():
                prompt += ", high quality, detailed, professional"
            
            negative_prompt = "text, letters, words, watermark, signature, blurry, low quality, distorted, ugly, deformed"
            
            logger.info(f"Generated prompt for '{headline[:50]}...': {prompt[:100]}...")
            
            return {
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "style": style,
                "platform": platform,
                "language": language
            }
        
        except Exception as e:
            logger.exception(f"ImagePromptEngine failed: {e}")
            # Fallback: базовый промпт
            return {
                "prompt": f"{headline}, high quality illustration, no text, professional",
                "negative_prompt": "text, letters, watermark, blurry, low quality",
                "style": style,
                "platform": platform,
                "language": language
            }
    
    def generate_anime_prompt(self, anime_title: str, context: str = "") -> Dict[str, Any]:
        """Специализированный промпт для аниме контента."""
        headline = f"{anime_title} anime"
        text = context or f"Official anime artwork for {anime_title}"
        
        return self.generate_prompt(
            headline=headline,
            text=text,
            platform="telegram",
            language="en",
            style="anime"
        )