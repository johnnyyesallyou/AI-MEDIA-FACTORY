"""Image Prompt Generator Engine - создает промпты для генерации картинок."""
import logging
from typing import Optional, Dict, Any
from engines.llm_client import LLMClient

logger = logging.getLogger(__name__)


class ImagePromptEngine:
    """
    Sprint 11: Генерирует промпты для Image Generator на основе текста поста.
    
    Использует Ollama (mistral-nemo:12b) для создания детальных промптов.
    
    Примеры промптов:
    - "A futuristic AI robot reading digital news, blue neon lighting, clean minimal illustration, telegram cover, 16:9, high quality, no text"
    - "Аниме-девушка держит мангу, яркие цвета, современный японский стиль, без текста, обложка для Telegram"
    """
    
    def __init__(self, model: str = "mistral-nemo:12b"):
        self.llm = LLMClient(model=model)
        self.model = model
    
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
        
        Args:
            headline: Заголовок поста
            text: Текст поста
            platform: Платформа (telegram/vk/youtube)
            language: Язык промпта (en/ru)
            style: Стиль (minimal/anime/cinematic)
        
        Returns:
            {"prompt": str, "negative_prompt": str, "style": str}
        """
        try:
            # Формируем системный промпт
            system_prompt = f"""You are an expert image prompt engineer for {platform} posts.

Generate a detailed, high-quality image prompt based on the post content.

Requirements:
- Language: {language}
- Style: {style}
- Aspect ratio: 16:9 for {platform}
- NO TEXT in the image (text will be added separately)
- High quality, professional illustration
- Relevant to the post topic

Output ONLY the image prompt (no explanations, no markdown).
"""
            
            # Формируем user prompt
            user_prompt = f"""Post headline: {headline}

Post text: {text[:500]}

Generate an image prompt that visually represents this content."""
            
            # Генерируем промпт через LLM
            response = self.llm.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=200,
                temperature=0.7
            )
            
            prompt = response.strip()
            
            # Добавляем технические параметры
            if "no text" not in prompt.lower():
                prompt += ", no text, no letters, no words"
            
            if "high quality" not in prompt.lower():
                prompt += ", high quality, detailed, professional"
            
            # Negative prompt (что НЕ должно быть в картинке)
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