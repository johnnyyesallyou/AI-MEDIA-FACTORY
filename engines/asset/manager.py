"""Asset Manager - сохраняет сгенерированные медиафайлы."""
import logging
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional
import uuid
import time

from core.database import SessionLocal
from core.models.asset_orm import AssetORM

logger = logging.getLogger(__name__)


class AssetManager:
    """
    Sprint 11: Менеджер для сохранения и управления медиафайлами.
    
    Sprint 13.1:
    - Определение формата файла (PNG/JPEG/WebP) по Content-Type
    - Правильное расширение в filename
    - Retry логика с exponential backoff
    """

    # Маппинг Content-Type → расширение файла
    CONTENT_TYPE_TO_EXT = {
        "image/png": "png",
        "image/jpeg": "jpg",
        "image/jpg": "jpg",
        "image/webp": "webp",
        "image/gif": "gif",
        "application/octet-stream": "png",  # Fallback
    }

    def __init__(self, base_dir: str = "/app/assets"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"AssetManager initialized: {self.base_dir}")

    def _download_with_retry(
        self,
        url: str,
        timeout: int = 120,
        max_retries: int = 3,
        backoff: float = 2.0
    ) -> requests.Response:
        """Скачивает файл с retry логикой."""
        last_error = None

        for attempt in range(max_retries):
            try:
                logger.info(f"Download attempt {attempt+1}/{max_retries}: {url[:80]}...")
                response = requests.get(url, timeout=timeout, stream=True)
                response.raise_for_status()

                content_type = response.headers.get("content-type", "")
                logger.info(f"✅ Download successful ({len(response.content)} bytes, {content_type})")
                return response

            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                last_error = e
                if attempt < max_retries - 1:
                    wait_time = backoff ** attempt
                    logger.warning(f"Download failed (attempt {attempt+1}), retrying in {wait_time}s: {e}")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Download failed after {max_retries} attempts: {e}")

        raise last_error

    def _detect_extension(self, response: requests.Response) -> str:
        """
        Определяет расширение файла по Content-Type header.
        
        Returns:
            Расширение файла (png, jpg, webp, gif)
        """
        content_type = response.headers.get("content-type", "").lower()
        
        # Убираем charset и другие параметры (image/jpeg; charset=utf-8 → image/jpeg)
        if ";" in content_type:
            content_type = content_type.split(";")[0].strip()
        
        ext = self.CONTENT_TYPE_TO_EXT.get(content_type, "png")  # Fallback на PNG
        logger.info(f"Detected extension: {ext} (from Content-Type: {content_type})")
        return ext

    def save_from_url(
        self,
        image_url: str,
        content_id: str,
        prompt: str = "",
        model: str = "pollinations",
        seed: Optional[int] = None,
        width: int = 1024,
        height: int = 576
    ) -> Optional[AssetORM]:
        """
        Скачивает изображение по URL и сохраняет локально.
        
        Sprint 13.1: Определяет формат файла по Content-Type.
        """
        db = SessionLocal()
        try:
            asset_id = str(uuid.uuid4())
            date_path = datetime.utcnow().strftime("%Y/%m")

            start_time = datetime.utcnow()

            # Скачиваем с retry
            response = self._download_with_retry(image_url, timeout=120, max_retries=3)

            # Sprint 13.1: Определяем расширение по Content-Type
            extension = self._detect_extension(response)
            filename = f"{asset_id}.{extension}"
            storage_path = f"assets/{date_path}/{filename}"

            full_path = self.base_dir / date_path
            full_path.mkdir(parents=True, exist_ok=True)
            file_path = full_path / filename

            # Сохраняем файл
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            generation_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            file_size = file_path.stat().st_size

            # Валидация: файл не должен быть пустым
            if file_size == 0:
                logger.error(f"Downloaded file is empty (0 bytes)")
                file_path.unlink()
                raise ValueError("Downloaded file is empty (0 bytes)")

            # Валидация: минимальный размер для изображения (1KB)
            if file_size < 1024:
                logger.warning(f"File too small ({file_size} bytes), might be corrupted")

            public_url = f"/assets/{date_path}/{filename}"

            asset = AssetORM(
                id=asset_id,
                content_id=content_id,
                type="image",
                storage_path=storage_path,
                public_url=public_url,
                prompt=prompt,
                model=model,
                seed=seed,
                width=width,
                height=height,
                generation_time_ms=generation_time_ms,
                status="generated",
                extra_data={
                    "source": "pollinations",
                    "original_url": image_url,
                    "file_size_bytes": file_size,
                    "file_extension": extension,
                    "content_type": response.headers.get("content-type", "")
                }
            )

            db.add(asset)
            db.commit()
            db.refresh(asset)

            logger.info(f"Asset saved: {asset.id} -> {storage_path} ({generation_time_ms}ms, {file_size} bytes, .{extension})")
            return asset

        except Exception as e:
            logger.exception(f"AssetManager.save_from_url failed: {e}")
            db.rollback()
            return None

        finally:
            db.close()

    def get_asset(self, asset_id: str) -> Optional[AssetORM]:
        """Получает asset по ID."""
        db = SessionLocal()
        try:
            return db.query(AssetORM).filter(AssetORM.id == asset_id).first()
        finally:
            db.close()

    def get_assets_for_content(self, content_id: str) -> list:
        """Получает все assets для контента."""
        db = SessionLocal()
        try:
            return db.query(AssetORM).filter(
                AssetORM.content_id == content_id
            ).order_by(AssetORM.created_at.desc()).all()
        finally:
            db.close()
