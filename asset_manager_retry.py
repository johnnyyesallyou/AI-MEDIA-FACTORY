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
    
    Скачивает изображения по URL (Pollinations AI и др.) и сохраняет локально.
    Поддержка retry с экспоненциальной задержкой.
    """
    
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
                
                # Проверяем content-type
                content_type = response.headers.get("content-type", "")
                if "image" not in content_type and "octet-stream" not in content_type:
                    logger.warning(f"Unexpected content-type: {content_type}")
                
                logger.info(f"✅ Download successful ({len(response.content)} bytes)")
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
        """Скачивает изображение по URL и сохраняет локально."""
        db = SessionLocal()
        try:
            asset_id = str(uuid.uuid4())
            date_path = datetime.utcnow().strftime("%Y/%m")
            filename = f"{asset_id}.png"
            storage_path = f"assets/{date_path}/{filename}"
            
            full_path = self.base_dir / date_path
            full_path.mkdir(parents=True, exist_ok=True)
            file_path = full_path / filename
            
            start_time = datetime.utcnow()
            
            # Скачиваем с retry
            response = self._download_with_retry(image_url, timeout=120, max_retries=3)
            
            # Сохраняем файл
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            generation_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            file_size = file_path.stat().st_size
            
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
                    "file_size_bytes": file_size
                }
            )
            
            db.add(asset)
            db.commit()
            db.refresh(asset)
            
            logger.info(f"Asset saved: {asset.id} -> {storage_path} ({generation_time_ms}ms, {file_size} bytes)")
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