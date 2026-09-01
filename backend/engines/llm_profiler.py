"""
Sprint 67.1: LLM Performance Profiling & Caching

Tracks and optimizes LLM generation performance with:
- Request duration tracking
- Response caching with TTL
- Fallback mechanisms for timeouts
- Token counting and analysis
"""

import time
import json
import hashlib
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)


@dataclass
class LLMProfile:
    """Profile data for an LLM generation request"""
    request_id: str
    channel_id: Optional[str]
    model: str
    prompt_hash: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    duration_seconds: float = 0.0
    status: str = "pending"  # pending, success, timeout, error
    error_message: Optional[str] = None
    cached: bool = False
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['cached'] = self.cached
        return data


@dataclass
class LLMCacheEntry:
    """Cache entry for LLM response"""
    response: str
    model: str
    token_count: int
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(hours=1))
    hit_count: int = 0
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired"""
        return datetime.utcnow() > self.expires_at
    
    def touch(self) -> None:
        """Update hit count and extend TTL"""
        self.hit_count += 1
        self.expires_at = datetime.utcnow() + timedelta(hours=1)


class LLMProfiler:
    """Profiles LLM generation performance"""
    
    def __init__(self):
        self.profiles: Dict[str, LLMProfile] = {}
        self.cache: Dict[str, LLMCacheEntry] = {}
        self.stats = {
            "total_requests": 0,
            "successful": 0,
            "cached": 0,
            "timeouts": 0,
            "errors": 0,
            "total_duration": 0.0,
            "total_tokens": 0,
        }
    
    def create_profile(self, request_id: str, channel_id: Optional[str], 
                      model: str, prompt: str) -> LLMProfile:
        """Create a new profile for tracking"""
        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:16]
        
        profile = LLMProfile(
            request_id=request_id,
            channel_id=channel_id,
            model=model,
            prompt_hash=prompt_hash
        )
        
        self.profiles[request_id] = profile
        self.stats["total_requests"] += 1
        
        logger.debug(f"Created profile for {request_id}", extra={
            "request_id": request_id,
            "channel_id": channel_id,
            "model": model,
            "prompt_hash": prompt_hash
        })
        
        return profile
    
    def get_cache_key(self, channel_id: str, prompt: str, model: str) -> str:
        """Generate cache key for a request"""
        combined = f"{channel_id}:{model}:{prompt}"
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def get_cached(self, cache_key: str) -> Optional[str]:
        """Get cached response if available and not expired"""
        if cache_key not in self.cache:
            return None
        
        entry = self.cache[cache_key]
        
        if entry.is_expired():
            del self.cache[cache_key]
            logger.debug(f"Cache entry expired: {cache_key}")
            return None
        
        entry.touch()
        self.stats["cached"] += 1
        
        logger.debug(f"Cache hit for {cache_key}", extra={
            "cache_key": cache_key,
            "hit_count": entry.hit_count
        })
        
        return entry.response
    
    def set_cached(self, cache_key: str, response: str, model: str, 
                   token_count: int = 0, ttl_hours: int = 1) -> None:
        """Cache an LLM response"""
        entry = LLMCacheEntry(
            response=response,
            model=model,
            token_count=token_count,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=ttl_hours)
        )
        
        self.cache[cache_key] = entry
        
        logger.debug(f"Cached response: {cache_key}", extra={
            "cache_key": cache_key,
            "token_count": token_count,
            "ttl_hours": ttl_hours
        })
    
    def mark_success(self, request_id: str, duration: float, 
                    prompt_tokens: int = 0, completion_tokens: int = 0,
                    cached: bool = False) -> None:
        """Mark request as successful"""
        if request_id not in self.profiles:
            logger.warning(f"Profile not found for {request_id}")
            return
        
        profile = self.profiles[request_id]
        profile.status = "success"
        profile.duration_seconds = duration
        profile.prompt_tokens = prompt_tokens
        profile.completion_tokens = completion_tokens
        profile.total_tokens = prompt_tokens + completion_tokens
        profile.cached = cached
        
        self.stats["successful"] += 1
        self.stats["total_duration"] += duration
        self.stats["total_tokens"] += profile.total_tokens
        
        logger.info(f"LLM generation successful", extra={
            "request_id": request_id,
            "duration_seconds": duration,
            "total_tokens": profile.total_tokens,
            "cached": cached
        })
    
    def mark_timeout(self, request_id: str, duration: float) -> None:
        """Mark request as timed out"""
        if request_id not in self.profiles:
            return
        
        profile = self.profiles[request_id]
        profile.status = "timeout"
        profile.duration_seconds = duration
        profile.error_message = f"Request exceeded {duration}s timeout"
        
        self.stats["timeouts"] += 1
        
        logger.warning(f"LLM generation timeout", extra={
            "request_id": request_id,
            "duration_seconds": duration,
            "channel_id": profile.channel_id
        })
    
    def mark_error(self, request_id: str, error: Exception, duration: float = 0.0) -> None:
        """Mark request as errored"""
        if request_id not in self.profiles:
            return
        
        profile = self.profiles[request_id]
        profile.status = "error"
        profile.duration_seconds = duration
        profile.error_message = str(error)
        
        self.stats["errors"] += 1
        
        logger.error(f"LLM generation error", extra={
            "request_id": request_id,
            "error": str(error),
            "duration_seconds": duration,
            "channel_id": profile.channel_id
        })
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get aggregated statistics"""
        total = self.stats["total_requests"]
        success_rate = (self.stats["successful"] / total * 100) if total > 0 else 0
        avg_duration = (self.stats["total_duration"] / self.stats["successful"]) if self.stats["successful"] > 0 else 0
        avg_tokens = (self.stats["total_tokens"] / self.stats["successful"]) if self.stats["successful"] > 0 else 0
        
        return {
            "total_requests": total,
            "successful": self.stats["successful"],
            "cached_hits": self.stats["cached"],
            "timeouts": self.stats["timeouts"],
            "errors": self.stats["errors"],
            "success_rate": round(success_rate, 2),
            "average_duration_seconds": round(avg_duration, 2),
            "average_tokens": round(avg_tokens, 0),
            "cache_size": len(self.cache),
            "profiles_count": len(self.profiles),
        }
    
    def cleanup_expired_cache(self) -> None:
        """Remove expired cache entries"""
        expired = [k for k, v in self.cache.items() if v.is_expired()]
        
        for key in expired:
            del self.cache[key]
        
        if expired:
            logger.debug(f"Cleaned {len(expired)} expired cache entries")
    
    def clear_old_profiles(self, max_age_hours: int = 24) -> None:
        """Remove old profile entries"""
        cutoff = datetime.utcnow() - timedelta(hours=max_age_hours)
        old = [k for k, v in self.profiles.items() if v.timestamp < cutoff]
        
        for key in old:
            del self.profiles[key]
        
        if old:
            logger.debug(f"Cleaned {len(old)} old profile entries")


# Global profiler instance
_profiler = LLMProfiler()


def get_profiler() -> LLMProfiler:
    """Get the global LLM profiler instance"""
    return _profiler


def profile_llm_call(channel_id: Optional[str] = None, model: str = "gemma2:9b"):
    """Decorator for profiling LLM generation calls"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            import uuid
            request_id = str(uuid.uuid4())
            
            # Get prompt from kwargs or first positional arg
            prompt = kwargs.get('prompt') or (args[0] if args else "")
            
            profiler = get_profiler()
            profiler.create_profile(request_id, channel_id, model, prompt)
            
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Try to extract token counts from result
                token_count = 0
                if isinstance(result, dict):
                    token_count = result.get('token_count', 0)
                
                profiler.mark_success(
                    request_id, 
                    duration, 
                    completion_tokens=token_count,
                    cached=False
                )
                
                return result
            
            except TimeoutError:
                duration = time.time() - start_time
                profiler.mark_timeout(request_id, duration)
                raise
            
            except Exception as e:
                duration = time.time() - start_time
                profiler.mark_error(request_id, e, duration)
                raise
        
        return wrapper
    return decorator


# Example usage in llm_generator.py:
"""
from backend.engines.llm_profiler import profile_llm_call, get_profiler

class LLMGenerator:
    @profile_llm_call(channel_id="news-channel", model="gemma2:9b")
    async def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        # Generation logic here
        pass
    
    def get_stats(self):
        profiler = get_profiler()
        return profiler.get_statistics()
"""
