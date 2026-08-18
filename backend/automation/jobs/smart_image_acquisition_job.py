"""Smart Image Acquisition Job - Sprint 21.

Автоматически находит изображения для контента через SmartImageResolver.
Использует channel_profile для определения приоритетов.

Интегрируется в ResearchJob/PipelineJob.
"""
import logging
from typing import Dict, Any, List

from core.database import SessionLocal
from core.models.content_orm import ContentORM
from core.models.channel_orm import ChannelORM
from engines.smart_image_resolver import SmartImageResolver
import json

logger = logging.getLogger(__name__)


class SmartImageAcquisitionJob:
    """
    Автоматический резолвер изображений для контента.
    
    Sprint 21: Smart Image Acquisition
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.resolver = SmartImageResolver()

    def run(self, channel: ChannelORM = None, limit: int = 20) -> Dict[str, Any]:
        """
        Обрабатывает items без asset_id.
        
        Args:
            channel: Обрабатывать только этот канал (None = все)
            limit: Максимум items для обработки
        
        Returns:
            Статистика обработки
        """
        self.logger.info(f"SmartImageAcquisitionJob started (limit={limit})")
        
        db = SessionLocal()
        
        try:
            # Query items без asset_id
            query = db.query(ContentORM).filter(ContentORM.asset_id == None)
            
            if channel:
                query = query.filter(ContentORM.channel_id == channel.id)
            
            items = query.limit(limit).all()
            
            if not items:
                return {"status": "ok", "processed": 0, "resolved": 0, "message": "No items"}
            
            processed = 0
            resolved = 0
            sources = {}
            
            for item in items:
                processed += 1
                
                # Получаем channel для item
                item_channel = db.query(ChannelORM).filter(
                    ChannelORM.id == item.channel_id
                ).first()
                
                if not item_channel:
                    self.logger.warning(f"Channel not found for item {item.id}")
                    continue
                
                # Извлекаем metadata
                try:
                    metadata = json.loads(item.source_text) if item.source_text else {}
                except:
                    metadata = {}
                
                # Resolvим изображение
                result = self.resolver.resolve(
                    content_id=item.id,
                    source_url=item.source_url,
                    channel=item_channel,
                    metadata=metadata
                )
                
                if result:
                    resolved += 1
                    item.asset_id = result.asset_id
                    item.image_url = result.url
                    
                    source_key = result.source
                    sources[source_key] = sources.get(source_key, 0) + 1
                    
                    self.logger.info(
                        f"Resolved {source_key} for {item.headline[:50]}: "
                        f"confidence={result.confidence}"
                    )
                
                # Commit после каждого item
                db.commit()
            
            stats = {
                "status": "ok",
                "processed": processed,
                "resolved": resolved,
                "sources": sources,
                "success_rate": resolved / processed if processed > 0 else 0
            }
            
            self.logger.info(f"SmartImageAcquisitionJob finished: {stats}")
            return stats
        
        except Exception as e:
            db.rollback()
            self.logger.exception(f"SmartImageAcquisitionJob failed: {e}")
            return {"status": "failed", "error": str(e)}
        finally:
            db.close()