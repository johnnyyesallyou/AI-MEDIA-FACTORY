"""Sprint 74.2 compatibility adapter for APIRateLimiter.circuit_breakers.

Переводит APIRateLimiter на использование unified CircuitBreaker из reliability.py,
оставляя старый интерфейс APIRateLimiter.record_success/failure/get_stats неизменным.
"""

from backend.core.reliability import get_breaker, CircuitOpenError, CircuitState
from backend.core.reliability import CircuitBreaker as UnifiedBreaker  # для type hints / совместимости

def _adapter_breaker(api_name: str) -> UnifiedBreaker:
    """Compatibility: APIRateLimiter обращается к одному и тому же breaker'у,
    что и Publisher / Self-Healing."""
    return get_breaker(api_name)