"""
Sprint 67.4: Rate Limiting Implementation

Provides sliding window rate limiting with:
- Per-API limits (Pixabay, Ollama, Telegram)
- Exponential backoff
- Circuit breaker pattern
- Metrics tracking
"""

import time
import logging
import asyncio
from typing import Optional, Dict, Any
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class RateLimitStrategy(Enum):
    """Rate limiting algorithm strategies"""
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    FIXED_WINDOW = "fixed_window"


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting"""
    max_requests: int  # Max requests in window
    window_seconds: int  # Time window in seconds
    strategy: RateLimitStrategy = RateLimitStrategy.SLIDING_WINDOW
    enable_backoff: bool = True  # Enable exponential backoff
    backoff_factor: float = 2.0  # Exponential backoff multiplier
    max_backoff: float = 60.0  # Maximum backoff time


class SlidingWindowLimiter:
    """Sliding window rate limiter"""
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.requests: deque = deque()  # (timestamp,) tuples
        self.blocked_until = 0.0
        self.backoff_count = 0
    
    def _cleanup_old_requests(self) -> None:
        """Remove requests outside the window"""
        cutoff = time.time() - self.config.window_seconds
        
        while self.requests and self.requests[0] < cutoff:
            self.requests.popleft()
    
    def is_allowed(self) -> bool:
        """Check if request is allowed"""
        now = time.time()
        
        # Check if still in backoff
        if now < self.blocked_until:
            return False
        
        self._cleanup_old_requests()
        
        # Check if limit exceeded
        if len(self.requests) >= self.config.max_requests:
            return False
        
        return True
    
    async def acquire(self, timeout: float = 5.0) -> bool:
        """Acquire token, waiting if necessary (with timeout)"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.is_allowed():
                self.requests.append(time.time())
                return True
            
            # Wait before retrying
            await asyncio.sleep(0.1)
        
        return False
    
    def record_rejection(self) -> None:
        """Record a rejection and apply backoff"""
        if self.config.enable_backoff:
            backoff_time = min(
                self.config.backoff_factor ** self.backoff_count,
                self.config.max_backoff
            )
            self.blocked_until = time.time() + backoff_time
            self.backoff_count += 1
            
            logger.warning(f"Rate limited, backoff {backoff_time}s")
    
    def reset_backoff(self) -> None:
        """Reset backoff counter on success"""
        self.backoff_count = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get limiter statistics"""
        self._cleanup_old_requests()
        return {
            "current_requests": len(self.requests),
            "max_requests": self.config.max_requests,
            "window_seconds": self.config.window_seconds,
            "backoff_count": self.backoff_count,
            "blocked_until": self.blocked_until,
            "backoff_enabled": self.config.enable_backoff,
        }


class CircuitBreaker:
    """Circuit breaker for handling API failures"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        """Initialize circuit breaker"""
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half_open
    
    def record_success(self) -> None:
        """Record successful call"""
        self.failure_count = 0
        self.state = "closed"
    
    def record_failure(self) -> None:
        """Record failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")
    
    def is_available(self) -> bool:
        """Check if service is available"""
        if self.state == "closed":
            return True
        
        if self.state == "open":
            # Check if recovery timeout has passed
            if (time.time() - self.last_failure_time) > self.recovery_timeout:
                self.state = "half_open"
                logger.info("Circuit breaker entering half-open state")
                return True
            return False
        
        # half_open state
        return True
    
    def get_state(self) -> str:
        """Get current state"""
        return self.state


class APIRateLimiter:
    """Rate limiter for external APIs"""
    
    def __init__(self):
        self.limiters: Dict[str, SlidingWindowLimiter] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        
        # Configure API limits
        self._configure_apis()
    
    def _configure_apis(self) -> None:
        """Configure rate limits for known APIs"""
        apis = {
            "pixabay": RateLimitConfig(
                max_requests=100,
                window_seconds=3600,  # 100 req/hour
                enable_backoff=True,
                backoff_factor=2.0,
                max_backoff=300.0  # 5 min max backoff
            ),
            "ollama": RateLimitConfig(
                max_requests=10,
                window_seconds=1,  # 10 concurrent
                enable_backoff=True,
                backoff_factor=1.5,
                max_backoff=60.0
            ),
            "telegram": RateLimitConfig(
                max_requests=30,
                window_seconds=1,  # 30 msg/sec
                enable_backoff=True,
                backoff_factor=1.2,
                max_backoff=30.0
            ),
            "remanga": RateLimitConfig(
                max_requests=50,
                window_seconds=60,  # 50 req/min
                enable_backoff=True,
                backoff_factor=2.0,
                max_backoff=120.0
            ),
        }
        
        for api_name, config in apis.items():
            self.limiters[api_name] = SlidingWindowLimiter(config)
            self.circuit_breakers[api_name] = CircuitBreaker(
                failure_threshold=5,
                recovery_timeout=60
            )
    
    async def acquire(self, api_name: str, timeout: float = 5.0) -> bool:
        """Acquire token for API call"""
        if api_name not in self.limiters:
            logger.warning(f"Unknown API: {api_name}, allowing request")
            return True
        
        # Check circuit breaker first
        breaker = self.circuit_breakers[api_name]
        if not breaker.is_available():
            logger.warning(f"Circuit breaker open for {api_name}")
            return False
        
        # Check rate limit
        limiter = self.limiters[api_name]
        allowed = await limiter.acquire(timeout)
        
        if not allowed:
            limiter.record_rejection()
            logger.warning(f"Rate limit exceeded for {api_name}")
        
        return allowed
    
    def record_success(self, api_name: str) -> None:
        """Record successful API call"""
        if api_name in self.limiters:
            self.limiters[api_name].reset_backoff()
        
        if api_name in self.circuit_breakers:
            self.circuit_breakers[api_name].record_success()
        
        logger.debug(f"API call success: {api_name}")
    
    def record_failure(self, api_name: str) -> None:
        """Record failed API call"""
        if api_name in self.circuit_breakers:
            self.circuit_breakers[api_name].record_failure()
        
        logger.warning(f"API call failed: {api_name}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiter statistics"""
        stats = {}
        
        for api_name in self.limiters:
            limiter_stats = self.limiters[api_name].get_stats()
            breaker = self.circuit_breakers[api_name]
            
            stats[api_name] = {
                **limiter_stats,
                "circuit_breaker_state": breaker.state,
                "failure_count": breaker.failure_count,
            }
        
        return stats


# Global rate limiter instance
_rate_limiter: Optional[APIRateLimiter] = None


def get_rate_limiter() -> APIRateLimiter:
    """Get global rate limiter instance"""
    global _rate_limiter
    
    if _rate_limiter is None:
        _rate_limiter = APIRateLimiter()
    
    return _rate_limiter


def rate_limit_call(api_name: str, timeout: float = 5.0):
    """Decorator for rate-limited API calls"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            limiter = get_rate_limiter()
            
            # Acquire token
            if not await limiter.acquire(api_name, timeout):
                logger.error(f"Rate limit acquisition failed for {api_name}")
                raise RuntimeError(f"Rate limit exceeded for {api_name}")
            
            try:
                result = await func(*args, **kwargs)
                limiter.record_success(api_name)
                return result
            
            except Exception as e:
                limiter.record_failure(api_name)
                raise
        
        return wrapper
    return decorator


# Example usage:
"""
from backend.core.rate_limiter import rate_limit_call

@rate_limit_call("pixabay", timeout=10.0)
async def search_pixabay_video(query: str) -> Dict[str, Any]:
    # API call here
    pass

@rate_limit_call("ollama", timeout=5.0)
async def call_llm(prompt: str) -> str:
    # LLM call here
    pass
"""
