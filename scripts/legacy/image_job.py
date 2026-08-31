"""Image Job — генерация картинок для постов."""
import logging
from typing import Optional, Dict, Any
from core.database import SessionLocal
from core.repositories.content_repository import ContentRepository
from engines.image.engine import ImageEngine

logger = logging.getLogger(__name__)


class ImageJob:
    """
    Sprint 11: Генерирует картинки для постов.
    
    Поддерживает:
    - Анонсы серий: постер аниме + название + дата выхода
    - Общие посты: скриншот из аниме + описание
    
    Использует ImageEngine для генерации через Stable Diffusion / DALL-E.
    """
    
    def run(self, channel=None, execution_id: str = None) -> Dict[str, Any]:
        logger.info("ImageJob started")
        
        db = SessionLocal()
        processed = 0
        generated = 0
        failed = 0
        
        try:
            repo = ContentRepository(db)
            
            # Берём approved посты БЕЗ image_url
            items = repo.list_all(status="approved", limit=10)
            items = [i for i in items if not i.image_url]
            
            logger.info(f"Items without images: {len(items)}")
            
            image_engine = ImageEngine()
            
            for item in items:
                try:
                    processed += 1
                    
                    # Генерируем промпт для картинки на основе headline и draft_text
                    prompt = self._generate_prompt(item.headline, item.draft_text)
                    
                    logger.info(f"Generating image for: {item.headline[:50]}...")
                    
                    # Генерируем картинку
                    result = image_engine.generate(
                        prompt=prompt,
                        style="anime",
                        aspect_ratio="16:9"
                    )
                    
                    if result and result.get("image_url"):
                        item.image_url = result["image_url"]
                        item.image_prompt = prompt
                        db.commit()
                        generated += 1
                        logger.info(f"✅ Image generated: {result['image_url']}")
                    else:
                        logger.warning(f"No image generated for item={item.id}")
                        failed += 1
                
                except Exception as e:
                    logger.exception(f"Image generation failed for item={item.id}: {e}")
                    failed += 1
                    db.rollback()
            
            logger.info(f"ImageJob finished: processed={processed}, generated={generated}, failed={failed}")
            return {
                "status": "ok",
                "processed": processed,
                "generated": generated,
                "failed": failed
            }
        
        except Exception as e:
            logger.exception(f"ImageJob failed: {e}")
            return {"status": "failed", "error": str(e)}
        finally:
            db.close()
    
    def _generate_prompt(self, headline: str, draft_text: str) -> str:
        """Генерирует промпт для Stable Diffusion на основе текста поста."""
        # Извлекаем ключевые слова из headline
        keywords = []
        
        # Паттерны для аниме
        anime_keywords = [
            "anime", "manga", "series", "episode", "season",
            "character", "studio", "director", "release"
        ]
        
        headline_lower = headline.lower()
        for kw in anime_keywords:
            if kw in headline_lower:
                keywords.append(kw)
        
        # Базовый промпт
        base_prompt = "anime style, high quality, detailed, vibrant colors"
        
        # Добавляем контекст из headline
        if "release" in headline_lower or "episode" in headline_lower:
            base_prompt += ", anime poster, official artwork, promotional"
        elif "character" in headline_lower:
            base_prompt += ", character portrait, detailed face, expressive"
        else:
            base_prompt += ", scenic view, anime screenshot, cinematic"
        
        # Извлекаем название аниме (если есть в кавычках)
        import re
        anime_name_match = re.search(r'[""«»]([^""«»]+)[""«»]', headline)
        if anime_name_match:
            anime_name = anime_name_match.group(1)
            base_prompt = f"{anime_name}, {base_prompt}"
        
        return base_prompt