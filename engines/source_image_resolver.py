"""Source Image Resolver - извлекает og:image из source_url для новостей."""
import logging
import re
import urllib.parse
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup

from engines.asset.manager import AssetManager
from core.database import SessionLocal
from core.models.content_orm import ContentORM

logger = logging.getLogger(__name__)


@dataclass
class ImageCandidate:
    """Кандидат изображения с приоритетом."""
    url: str
    source: str
    priority: int


class SourceImageResolver:
    """
    Извлекает изображения из HTML source_url.
    
    Priority:
    1. og:image (Open Graph)
    2. twitter:image (Twitter Cards)
    3. meta image / link image_src
    4. Первое изображение в <article> / <main>
    5. Favicon (низкое качество)
    
    Sprint 17: Image Acquisition Pipeline
    """
    
    TIMEOUT = 10
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru,en;q=0.9",
    }
    SKIP_DOMAINS = ["t.me", "telegram.me", "vk.com/wall"]
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.asset_manager = AssetManager()
    
    def resolve_and_save(self, content_id: str, source_url: str) -> Optional[str]:
        """
        Извлекает og:image, сохраняет через AssetManager, обновляет content.
        
        Returns: asset_id если успешно, иначе None
        """
        if not source_url:
            return None
        
        try:
            domain = urllib.parse.urlparse(source_url).netloc
            if any(skip in domain for skip in self.SKIP_DOMAINS):
                return None
        except Exception:
            pass
        
        candidates = self._extract_candidates(source_url)
        
        if not candidates:
            self.logger.warning(f"No image candidates for {source_url[:80]}")
            return None
        
        candidates.sort(key=lambda c: c.priority)
        
        for candidate in candidates[:3]:
            try:
                asset = self.asset_manager.save_from_url(
                    image_url=candidate.url,
                    content_id=content_id,
                    prompt="",
                    model=f"source_{candidate.source}",
                )
                
                if asset:
                    # Обновляем content.image_url
                    db = SessionLocal()
                    try:
                        content = db.query(ContentORM).filter(ContentORM.id == content_id).first()
                        if content:
                            content.image_url = asset.public_url
                            db.commit()
                            self.logger.info(
                                f"Saved from {candidate.source}: {candidate.url[:60]} -> {asset.public_url}"
                            )
                    finally:
                        db.close()
                    return asset.id
            
            except Exception as e:
                self.logger.warning(f"Failed to save {candidate.source}: {e}")
                continue
        
        return None
    
    def _extract_candidates(self, url: str) -> List[ImageCandidate]:
        try:
            response = requests.get(url, headers=self.HEADERS, timeout=self.TIMEOUT)
            response.raise_for_status()
            
            content_type = response.headers.get("content-type", "")
            if "html" not in content_type and "xhtml" not in content_type:
                return []
            
            soup = BeautifulSoup(response.text, "html.parser")
            candidates = []
            
            og = soup.find("meta", property="og:image")
            if og and og.get("content"):
                resolved = self._resolve_url(og["content"], url)
                if resolved:
                    candidates.append(ImageCandidate(resolved, "og:image", 1))
            
            tw = soup.find("meta", attrs={"name": "twitter:image"}) or \
                 soup.find("meta", attrs={"name": "twitter:image:src"})
            if tw and tw.get("content"):
                resolved = self._resolve_url(tw["content"], url)
                if resolved:
                    candidates.append(ImageCandidate(resolved, "twitter:image", 2))
            
            link_img = soup.find("link", rel="image_src")
            if link_img and link_img.get("href"):
                resolved = self._resolve_url(link_img["href"], url)
                if resolved:
                    candidates.append(ImageCandidate(resolved, "link_image_src", 3))
            
            for container in ["article", "main", "[role='main']"]:
                elem = soup.select_one(container)
                if elem:
                    img = elem.find("img", src=True)
                    if img:
                        resolved = self._resolve_url(img["src"], url)
                        if resolved:
                            candidates.append(ImageCandidate(resolved, "article_img", 5))
                            break
            
            favicon = soup.find("link", rel=lambda x: x and "icon" in x.lower())
            if favicon and favicon.get("href"):
                resolved = self._resolve_url(favicon["href"], url)
                if resolved:
                    candidates.append(ImageCandidate(resolved, "favicon", 10))
            
            seen = set()
            unique = []
            for c in candidates:
                if c.url not in seen:
                    seen.add(c.url)
                    unique.append(c)
            return unique
        
        except Exception as e:
            self.logger.error(f"Extract failed for {url[:60]}: {type(e).__name__}: {e}")
            return []
    
    def _resolve_url(self, url: str, base_url: str) -> Optional[str]:
        if not url:
            return None
        url = url.strip()
        if url.startswith("data:") or url.startswith("javascript:"):
            return None
        if url.startswith("//"):
            url = "https:" + url
        elif not url.startswith(("http://", "https://")):
            url = urllib.parse.urljoin(base_url, url)
        if any(x in url.lower() for x in ["pixel", "beacon", "analytics", "tracking", "1x1", "spacer"]):
            return None
        return url
