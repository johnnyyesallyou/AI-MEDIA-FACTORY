"""URL Shortener - укорачивает длинные URL для Telegram постов."""
import logging
import requests
from typing import Dict, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class URLShortener:
    """
    URL Shortener с кэшем и fallback.
    
    Sprint 15: Интеграция с TinyURL (без API ключа).
    
    Features:
    - In-memory cache (5 min TTL)
    - Fallback на оригинальный URL при ошибке
    - Timeout protection (5 sec)
    
    Usage:
        shortener = URLShortener()
        short_url = shortener.shorten("https://very-long-url.com/...")
    """
    
    TIMEOUT = 5  # seconds
    CACHE_TTL = 300  # 5 minutes
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.cache: Dict[str, tuple] = {}  # url -> (short_url, expires_at)
    
    def shorten(self, long_url: str) -> str:
        """
        Укорачивает URL.
        
        Returns:
            Short URL если успешно, иначе оригинальный URL (fallback)
        """
        if not long_url:
            return long_url
        
        # Проверяем кэш
        cached = self._get_from_cache(long_url)
        if cached:
            self.logger.debug(f"URL cached: {long_url[:50]}... -> {cached}")
            return cached
        
        # Пробуем укоротить через TinyURL
        short_url = self._shorten_tinyurl(long_url)
        
        if short_url and len(short_url) < len(long_url):
            # Сохраняем в кэш
            self._set_to_cache(long_url, short_url)
            self.logger.info(
                f"URL shortened: {len(long_url)} -> {len(short_url)} chars"
            )
            return short_url
        
        # Fallback: возвращаем оригинал
        self.logger.warning(
            f"URL shortening failed, using original: {long_url[:80]}..."
        )
        return long_url
    
    def _shorten_tinyurl(self, long_url: str) -> Optional[str]:
        """TinyURL API (без ключа)."""
        try:
            url = "https://tinyurl.com/api-create.php"
            params = {"url": long_url}
            
            response = requests.get(
                url,
                params=params,
                timeout=self.TIMEOUT
            )
            
            if response.status_code == 200:
                short = response.text.strip()
                if short.startswith("https://tinyurl.com/"):
                    return short
            
            self.logger.warning(
                f"TinyURL failed: status={response.status_code}, "
                f"response={response.text[:100]}"
            )
            return None
        
        except requests.exceptions.Timeout:
            self.logger.error(f"TinyURL timeout for {long_url[:50]}...")
            return None
        except Exception as e:
            self.logger.error(f"TinyURL error: {type(e).__name__}: {e}")
            return None
    
    def _get_from_cache(self, long_url: str) -> Optional[str]:
        """Возвращает short URL из кэша или None."""
        if long_url not in self.cache:
            return None
        
        short_url, expires_at = self.cache[long_url]
        
        if datetime.utcnow() < expires_at:
            return short_url
        
        # Кэш истёк
        del self.cache[long_url]
        return None
    
    def _set_to_cache(self, long_url: str, short_url: str) -> None:
        """Сохраняет в кэш."""
        expires_at = datetime.utcnow() + timedelta(seconds=self.CACHE_TTL)
        self.cache[long_url] = (short_url, expires_at)
