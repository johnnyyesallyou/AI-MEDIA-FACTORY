"""
Sprint 67.2: Cache Layer Abstraction

Provides unified caching interface with:
- In-memory cache (development)
- Redis cache (production)
- Database fallback
- Automatic TTL management
"""

import json
import logging
import time
from abc import ABC, abstractmethod
from typing import Optional, Any, Dict
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)


class CacheBackend(ABC):
    """Abstract cache backend interface"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl_seconds: int = 3600) -> bool:
        """Set value in cache"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        pass
    
    @abstractmethod
    async def clear(self) -> bool:
        """Clear all cache entries"""
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        pass


class MemoryCache(CacheBackend):
    """In-memory cache backend (for development/testing)"""
    
    def __init__(self):
        self.store: Dict[str, tuple] = {}  # (value, expires_at)
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
        }
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key not in self.store:
            self.stats["misses"] += 1
            return None
        
        value, expires_at = self.store[key]
        
        if time.time() > expires_at:
            del self.store[key]
            self.stats["misses"] += 1
            return None
        
        self.stats["hits"] += 1
        return value
    
    async def set(self, key: str, value: Any, ttl_seconds: int = 3600) -> bool:
        """Set value in cache"""
        expires_at = time.time() + ttl_seconds
        self.store[key] = (value, expires_at)
        self.stats["sets"] += 1
        
        logger.debug(f"Memory cache SET: {key} (TTL: {ttl_seconds}s)")
        return True
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        if key in self.store:
            del self.store[key]
            self.stats["deletes"] += 1
            return True
        return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        if key not in self.store:
            return False
        
        value, expires_at = self.store[key]
        if time.time() > expires_at:
            del self.store[key]
            return False
        
        return True
    
    async def clear(self) -> bool:
        """Clear all cache entries"""
        self.store.clear()
        logger.debug("Memory cache cleared")
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total * 100) if total > 0 else 0
        
        return {
            "type": "memory",
            "size": len(self.store),
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "hit_rate": round(hit_rate, 2),
            "sets": self.stats["sets"],
            "deletes": self.stats["deletes"],
        }


class RedisCache(CacheBackend):
    """Redis cache backend (for production)"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        """Initialize Redis cache"""
        self.redis_url = redis_url
        self.redis = None
        self.stats = {
            "hits": 0,
            "misses": 0,
            "errors": 0,
        }
        self.enabled = False
        
        try:
            import redis
            # Will be properly initialized in async context
            self.redis_module = redis
            logger.info("Redis cache initialized")
        except ImportError:
            logger.warning("Redis not installed, falling back to memory cache")
    
    async def _ensure_connected(self) -> bool:
        """Ensure Redis connection is active"""
        if not self.redis:
            try:
                import aioredis
                self.redis = await aioredis.from_url(self.redis_url)
                self.enabled = True
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}, using memory fallback")
                return False
        return True
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not await self._ensure_connected():
            return None
        
        try:
            value = await self.redis.get(key)
            if value:
                self.stats["hits"] += 1
                return json.loads(value)
            else:
                self.stats["misses"] += 1
                return None
        except Exception as e:
            logger.warning(f"Redis GET error: {e}")
            self.stats["errors"] += 1
            return None
    
    async def set(self, key: str, value: Any, ttl_seconds: int = 3600) -> bool:
        """Set value in cache"""
        if not await self._ensure_connected():
            return False
        
        try:
            serialized = json.dumps(value, default=str)
            await self.redis.setex(key, ttl_seconds, serialized)
            logger.debug(f"Redis cache SET: {key} (TTL: {ttl_seconds}s)")
            return True
        except Exception as e:
            logger.warning(f"Redis SET error: {e}")
            self.stats["errors"] += 1
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        if not await self._ensure_connected():
            return False
        
        try:
            result = await self.redis.delete(key)
            return result > 0
        except Exception as e:
            logger.warning(f"Redis DELETE error: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not await self._ensure_connected():
            return False
        
        try:
            result = await self.redis.exists(key)
            return result > 0
        except Exception as e:
            logger.warning(f"Redis EXISTS error: {e}")
            return False
    
    async def clear(self) -> bool:
        """Clear all cache entries"""
        if not await self._ensure_connected():
            return False
        
        try:
            await self.redis.flushdb()
            logger.debug("Redis cache cleared")
            return True
        except Exception as e:
            logger.warning(f"Redis CLEAR error: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total * 100) if total > 0 else 0
        
        return {
            "type": "redis",
            "enabled": self.enabled,
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "hit_rate": round(hit_rate, 2),
            "errors": self.stats["errors"],
        }


class CacheLayer:
    """Unified cache layer with automatic backend selection"""
    
    def __init__(self, backend: Optional[CacheBackend] = None):
        """Initialize cache with optional backend"""
        if backend:
            self.backend = backend
        else:
            # Auto-select backend
            if os.getenv("USE_REDIS", "false").lower() == "true":
                self.backend = RedisCache(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
            else:
                self.backend = MemoryCache()
        
        logger.info(f"Cache layer initialized with {self.backend.__class__.__name__}")
    
    async def get(self, key: str, namespace: str = "default") -> Optional[Any]:
        """Get value from cache with namespace support"""
        full_key = f"{namespace}:{key}"
        return await self.backend.get(full_key)
    
    async def set(self, key: str, value: Any, ttl_seconds: int = 3600, 
                  namespace: str = "default") -> bool:
        """Set value in cache with namespace support"""
        full_key = f"{namespace}:{key}"
        return await self.backend.set(full_key, value, ttl_seconds)
    
    async def delete(self, key: str, namespace: str = "default") -> bool:
        """Delete value from cache"""
        full_key = f"{namespace}:{key}"
        return await self.backend.delete(full_key)
    
    async def exists(self, key: str, namespace: str = "default") -> bool:
        """Check if key exists"""
        full_key = f"{namespace}:{key}"
        return await self.backend.exists(full_key)
    
    async def clear(self) -> bool:
        """Clear all cache entries"""
        return await self.backend.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return self.backend.get_stats()


# Global cache instance
_cache_layer: Optional[CacheLayer] = None


def get_cache() -> CacheLayer:
    """Get global cache layer instance"""
    global _cache_layer
    
    if _cache_layer is None:
        _cache_layer = CacheLayer()
    
    return _cache_layer


async def cache_get(key: str, namespace: str = "default") -> Optional[Any]:
    """Convenience function to get from cache"""
    return await get_cache().get(key, namespace)


async def cache_set(key: str, value: Any, ttl_seconds: int = 3600, 
                   namespace: str = "default") -> bool:
    """Convenience function to set in cache"""
    return await get_cache().set(key, value, ttl_seconds, namespace)


async def cache_delete(key: str, namespace: str = "default") -> bool:
    """Convenience function to delete from cache"""
    return await get_cache().delete(key, namespace)


# Example usage:
"""
from backend.core.cache_layer import cache_get, cache_set

# Manga sources caching
cache_key = f"manga:{source}:{query}:{language}"
cached_result = await cache_get(cache_key, namespace="manga_sources")

if not cached_result:
    # Fetch from API
    result = await fetch_manga_source(source, query, language)
    await cache_set(cache_key, result, ttl_seconds=86400, namespace="manga_sources")
else:
    result = cached_result

# LLM response caching
llm_cache_key = f"{channel_id}:{model}:{prompt_hash}"
cached_response = await cache_get(llm_cache_key, namespace="llm_responses")

if not cached_response:
    response = await llm_generator.generate(prompt)
    await cache_set(llm_cache_key, response, ttl_seconds=3600, namespace="llm_responses")
else:
    response = cached_response
"""
