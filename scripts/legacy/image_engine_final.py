"""Image Engine - генерация картинок через Pollinations AI."""
import logging
import urllib.parse
from typing import Dict, Any
from engines.image_prompt.engine import ImagePromptEngine

logger = logging.getLogger(__name__)


class ImageEngine:
    """
    Sprint 11: Генерирует картинки через Pollinations AI.
    
    Использует ImagePromptEngine для создания КОРОТКИХ английских промптов,
    чтобы URL не был слишком длинным.
    """
    
    BASE_URL = "https://image.pollinations.ai/prompt/"
    
    def __init__(self):
        self.prompt_engine = ImagePromptEngine()
    
    def generate(
        self,
        headline: str,
        text: str,
        platform: str = "telegram",
        style: str = "anime",
        width: int = 1024,
        height: int = 576,
        model: str = "flux"
    ) -> Dict[str, Any]:
        """
        Генерирует URL для Pollinations AI.
        
        Args:
            headline: Заголовок поста
            text: Текст поста
            platform: Платформа
            style: Стиль
            width: Ширина
            height: Высота
            model: Модель
        
        Returns:
            {"image_url": str, "prompt": str, "style": str}
        """
        try:
            # Генерируем короткий промпт через ImagePromptEngine
            prompt_result = self.prompt_engine.generate_prompt(
                headline=headline,
                text=text,
                platform=platform,
                language="en",
                style=style
            )
            
            prompt = prompt_result["prompt"]
            
            # URL-encode промпта
            encoded_prompt = urllib.parse.quote(prompt, safe='')
            
            # Параметры
            params = {
                "width": width,
                "height": height,
                "model": model,
                "nologo": "true"
            }
            
            query_string = urllib.parse.urlencode(params)
            image_url = f"{self.BASE_URL}{encoded_prompt}?{query_string}"
            
            logger.info(f"ImageEngine: Generated URL (prompt: {len(prompt)} chars, URL: {len(image_url)} chars)")
            logger.info(f"   Prompt: {prompt}")
            logger.info(f"   URL: {image_url[:100]}...")
            
            return {
                "image_url": image_url,
                "prompt": prompt,
                "style": style,
                "platform": platform
            }
        
        except Exception as e:
            logger.exception(f"ImageEngine generation failed: {e}")
            # Fallback: очень короткий промпт
            fallback_prompt = "anime scene, high quality"
            encoded = urllib.parse.quote(fallback_prompt, safe='')
            fallback_url = f"{self.BASE_URL}{encoded}?width={width}&height={height}&model={model}&nologo=true"
            
            return {
                "image_url": fallback_url,
                "prompt": fallback_prompt,
                "style": style,
                "platform": platform
            }