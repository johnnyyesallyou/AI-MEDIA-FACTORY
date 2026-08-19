"""Image Job - генерация картинок для постов."""
import logging
from typing import Any
from core.database import SessionLocal
from core.models.content_orm import ContentORM
from core.models.channel_orm import ChannelORM
from engines.image.engine import ImageEngine
from engines.asset.manager import AssetManager

logger = logging.getLogger(__name__)

# Маппинг style_profile → style для ImageEngine
STYLE_MAPPING = {
    "minimal": "minimal",
    "anime": "anime",
    "realistic": "realistic",
    "watercolor": "watercolor",
    "cyberpunk": "cyberpunk",
    "fantasy": "fantasy",
}


class ImageJob:
    """
    Sprint 11: Генерирует картинки для approved постов.
    
    Sprint 13.1:
    - Интеграция с AssetManager для локального хранения
    - Фильтрация на уровне БД (не в Python)
    - Параметры style/platform из channel config
    
    Pipeline:
    1. Берёт approved посты БЕЗ image_url (фильтрация на уровне БД)
    2. Загружает параметры канала (style_profile, platform)
    3. Генерирует image_url через ImageEngine с параметрами канала
    4. Скачивает картинку через AssetManager (локальное хранение + БД)
    5. Сохраняет asset_id + локальный public_url в content
    """

    def run(self, channel=None, execution_id: str = None, limit: int = 10) -> dict[str, Any]:
        logger.info(f"ImageJob started (limit={limit})")

        db = SessionLocal()
        processed = 0
        generated = 0
        failed = 0
        assets_created = 0

        try:
            # Sprint 13.1: Фильтрация на уровне БД
            items = db.query(ContentORM).filter(
                ContentORM.status == "approved",
                ContentORM.image_url == None
            ).limit(limit).all()

            logger.info(f"Items without images (limit {limit}): {len(items)}")

            if not items:
                logger.info("No items need images")
                return {
                    "status": "ok",
                    "processed": 0,
                    "generated": 0,
                    "failed": 0,
                    "assets_created": 0
                }

            # Sprint 13.1: Загружаем все уникальные каналы одним запросом
            channel_ids = list(set(item.channel_id for item in items if item.channel_id))
            channels = {}
            
            if channel_ids:
                channel_list = db.query(ChannelORM).filter(
                    ChannelORM.id.in_(channel_ids)
                ).all()
                channels = {ch.id: ch for ch in channel_list}
                logger.info(f"Loaded {len(channels)} channels")

            image_engine = ImageEngine()
            asset_manager = AssetManager()

            for item in items:
                try:
                    processed += 1

                    logger.info(f"Processing {processed}/{len(items)}: {item.headline[:50]}...")

                    # Sprint 13.1: Получаем параметры из канала
                    channel = channels.get(item.channel_id)
                    
                    if channel:
                        # Маппинг style_profile → style
                        style = STYLE_MAPPING.get(channel.style_profile, "anime")
                        platform = channel.platform
                        logger.info(f"Using channel params: platform={platform}, style={style}")
                    else:
                        # Fallback: если канал не найден
                        style = "anime"
                        platform = "telegram"
                        logger.warning(f"Channel not found for {item.channel_id}, using defaults")

                    # Генерируем image_url через ImageEngine с параметрами канала
                    result = image_engine.generate(
                        headline=item.headline,
                        text=item.draft_text or "",
                        platform=platform,
                        style=style
                    )

                    if not result or not result.get("image_url"):
                        logger.warning(f"Failed to generate image for {item.id}")
                        failed += 1
                        continue

                    external_url = result["image_url"]
                    prompt = result.get("prompt", "")

                    # Скачиваем и сохраняем через AssetManager
                    logger.info(f"Downloading image via AssetManager...")
                    asset = asset_manager.save_from_url(
                        image_url=external_url,
                        content_id=item.id,
                        prompt=prompt,
                        model="pollinations",
                        width=1024,
                        height=576
                    )

                    if asset:
                        # AssetManager сработал - используем локальный asset
                        item.asset_id = asset.id
                        item.image_url = asset.public_url
                        item.image_prompt = prompt
                        db.commit()
                        generated += 1
                        assets_created += 1
                        logger.info(f"✅ Asset created: {asset.id} (style={style}, platform={platform})")
                    else:
                        # Fallback: AssetManager упал
                        logger.warning(f"AssetManager failed, using external URL as fallback")
                        item.image_url = external_url
                        item.image_prompt = prompt
                        db.commit()
                        generated += 1
                        logger.info(f"⚠️ External URL saved: {external_url[:80]}...")

                except Exception as e:
                    logger.exception(f"Image generation failed for {item.id}: {e}")
                    failed += 1
                    db.rollback()

            logger.info(
                f"ImageJob finished: processed={processed}, generated={generated}, "
                f"failed={failed}, assets_created={assets_created}"
            )
            return {
                "status": "ok",
                "processed": processed,
                "generated": generated,
                "failed": failed,
                "assets_created": assets_created
            }

        except Exception as e:
            logger.exception(f"ImageJob failed: {e}")
            return {"status": "failed", "error": str(e)}
        finally:
            db.close()
