"""Image Engine — генерация картинок через Pollinations AI (бесплатно, без ключей)."""
import logging
import requests
import urllib.parse
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class ImageEngine:
    """
    Sprint 11: Генерирует картинки для постов через Pollinations AI.
    
    Pollinations AI: https://pollinations.ai/
    - Бесплатный API
    - Не требует ключей
    - URL: https://image.pollinations.ai/prompt/{prompt}
    - Поддерживает: anime, realistic, cinematic стили
    """
    
    BASE_URL = "https://image.pollinations.ai/prompt/"
    
    def generate(
        self,
        prompt: str,
        style: str = "anime",
        aspect_ratio: str = "16:9",
        width: int = 1024,
        height: int = 576,
        model: str = "flux",
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Генерирует картинку по промпту.
        
        Args:
            prompt: Описание картинки
            style: стиль (anime, realistic, cinematic, digital-art)
            aspect_ratio: соотношение сторон (16:9, 1:1, 9:16)
            width: ширина
            height: высота
            model: модель (flux, turbo)
            seed: seed для воспроизводимости
        
        Returns:
            {"image_url": str, "prompt": str, "model": str}
        """
        try:
            # Добавляем стиль к промпту
            style_prompts = {
                "anime": "anime style, studio ghibli, vibrant colors, detailed, high quality",
                "realistic": "photorealistic, high detail, professional photography",
                "cinematic": "cinematic lighting, movie scene, dramatic, high quality",
                "digital-art": "digital art, concept art, detailed, vibrant"
            }
            
            full_prompt = f"{prompt}, {style_prompts.get(style, style_prompts['anime'])}"
            
            # URL-encode промпта
            encoded_prompt = urllib.parse.quote(full_prompt, safe='')
            
            # Параметры
            params = {
                "width": width,
                "height": height,
                "model": model,
                "nologo": "true",
                "enhance": "true"
            }
            
            if seed:
                params["seed"] = seed
            
            query_string = urllib.parse.urlencode(params)
            image_url = f"{self.BASE_URL}{encoded_prompt}?{query_string}"
            
            logger.info(f"ImageEngine: Generated URL for prompt: {prompt[:50]}...")
            logger.info(f"   URL: {image_url[:100]}...")
            
            # Проверяем что URL доступен (HEAD request)
            try:
                response = requests.head(image_url, timeout=10, allow_redirects=True)
                if response.status_code == 200:
                    logger.info("   ✅ Image URL is accessible")
                else:
                    logger.warning(f"   ⚠️ Image URL returned status {response.status_code}")
            except Exception as e:
                logger.warning(f"   ⚠️ Could not verify image URL: {e}")
            
            return {
                "image_url": image_url,
                "prompt": full_prompt,
                "model": model,
                "width": width,
                "height": height
            }
        
        except Exception as e:
            logger.exception(f"ImageEngine generation failed: {e}")
            return {"error": str(e)}
    
    def generate_anime_poster(self, anime_title: str, context: str = "") -> Dict[str, Any]:
        """Генерирует постер для аниме."""
        prompt = f"{anime_title}, official anime poster, promotional artwork"
        if context:
            prompt += f", {context}"
        return self.generate(prompt=prompt, style="anime", aspect_ratio="16:9")
    
    def generate_character_portrait(self, character_name: str, anime_title: str) -> Dict[str, Any]:
        """Генерирует портрет персонажа."""
        prompt = f"{character_name} from {anime_title}, character portrait, detailed face, expressive, anime style"
        return self.generate(prompt=prompt, style="anime", aspect_ratio="1:1")
    
    def generate_scene(self, description: str, anime_title: str = "") -> Dict[str, Any]:
        """Генерирует сцену из аниме."""
        prompt = description
        if anime_title:
            prompt = f"{anime_title}, {description}"
        return self.generate(prompt=prompt, style="cinematic", aspect_ratio="16:9")