"""Image Job - генерация картинок для постов."""
import logging
from typing import Any
from core.database import SessionLocal
from core.repositories.content_repository import ContentRepository
from engines.image.engine import ImageEngine

logger = logging.getLogger(__name__)


class ImageJob:
    """
    Sprint 11: Генерирует картинки для approved постов.
    
    Использует ImageEngine для создания URL через Pollinations AI.
    Сохраняет image_url в content для последующей публикации.
    """
    
    def run(self, channel=None, execution_id: str = None) -> dict[str, Any]:
        logger.info("ImageJob started")
        
        db = SessionLocal()
        processed = 0
        generated = 0
        failed = 0
        
        try:
            repo = ContentRepository(db)
            
            # Берём approved посты БЕЗ image_url
            items = repo.list_all(status="approved", limit=10)
            items = [i for i in items if not getattr(i, 'image_url', None)]
            
            logger.info(f"Items without images: {len(items)}")
            
            if not items:
                logger.info("No items need images")
                return {"status": "ok", "processed": 0, "generated": 0, "failed": 0}
            
            image_engine = ImageEngine()
            
            for item in items:
                try:
                    processed += 1
                    
                    logger.info(f"Generating image for: {item.headline[:50]}...")
                    
                    # Генерируем image_url через ImageEngine
                    result = image_engine.generate(
                        headline=item.headline,
                        text=item.draft_text or "",
                        platform="telegram",
                        style="anime"
                    )
                    
                    if result and result.get("image_url"):
                        item.image_url = result["image_url"]
                        item.image_prompt = result.get("prompt", "")
                        db.commit()
                        generated += 1
                        logger.info(f"✅ Image URL generated for {item.id}")
                        logger.info(f"   URL: {result['image_url'][:80]}...")
                    else:
                        logger.warning(f"Failed to generate image for {item.id}")
                        failed += 1
                
                except Exception as e:
                    logger.exception(f"Image generation failed for {item.id}: {e}")
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