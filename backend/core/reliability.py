"""
Sprint 74.1: Reliability Core — Retry Logic with Exponential Backoff

Асинхронный retry-движок для внешних вызовов (Telegram/VK API, sources).

Принципы:
- Retry только для TRANSIENT/NETWORK ошибок (классификация core.error_taxonomy)
- PERMANENT/CONFIGURATION ошибки не ретраются (fail fast + alert)
- Exponential backoff с jitter, поддержка Retry-After (429)
- Per-platform политики (telegram, vk, external_api)
- Запись финальных ошибок в pipeline_failures через error_logger
"""
import asyncio
import logging
import random
from dataclasses import dataclass
from typing import Callable, Any, Optional, Dict, Tuple

from core.error_taxonomy import classify_error, ClassifiedError, ErrorType

logger = logging.getLogger(__name__)


class VKError(Exception):
    """Ошибка VK API (body содержит error.error_code)."""

    # error_code → ErrorType
    CODE_MAP = {
        1: ErrorType.TRANSIENT,      # Unknown — occasional internal
        6: ErrorType.TRANSIENT,      # Too many requests per second
        9: ErrorType.TRANSIENT,      # Flood control
        10: ErrorType.TRANSIENT,     # Internal server error
        29: ErrorType.TRANSIENT,     # Rate limit reached
        5: ErrorType.CONFIGURATION,  # User authorization failed
        7: ErrorType.CONFIGURATION,  # Permission denied
        17: ErrorType.CONFIGURATION, # Validation required
        15: ErrorType.PERMANENT,     # Access denied
        100: ErrorType.PERMANENT,    # Incorrect request params
        200: ErrorType.PERMANENT,    # Access denied (wall)
    }

    def __init__(self, error_code: int, error_msg: str):
        self.error_code = error_code
        self.error_msg = error_msg
        super().__init__(f"VK error {error_code}: {error_msg}")

    @property
    def error_type(self) -> ErrorType:
        return self.CODE_MAP.get(self.error_code, ErrorType.UNKNOWN)


# Severity строкой (упрощённая сигнализация)
_ERROR_SEVERITY = {
    ErrorType.TRANSIENT: "low",
    ErrorType.NETWORK: "medium",
    ErrorType.PERMANENT: "medium",
    ErrorType.CONFIGURATION: "high",
    ErrorType.UNKNOWN: "medium",
}


@dataclass
class RetryPolicy:
    """Политика retry для платформы/сервиса."""
    name: str
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    backoff_factor: float = 2.0
    jitter: float = 0.2  # ±20% от задержки
    retry_on: Tuple[ErrorType, ...] = (ErrorType.TRANSIENT, ErrorType.NETWORK)

    def should_retry(self, error_type: ErrorType) -> bool:
        return error_type in self.retry_on

    def delay_for(self, attempt: int, retry_after: Optional[int] = None) -> float:
        """Задержка перед следующей попыткой (attempt — 0-based)."""
        if retry_after is not None:
            return float(min(retry_after, self.max_delay))
        delay = min(self.base_delay * (self.backoff_factor ** attempt), self.max_delay)
        jittered = delay * (1 + random.uniform(-self.jitter, self.jitter))
        return max(0.0, jittered)


# Per-platform политики (Sprint 74.1)
RETRY_POLICIES: Dict[str, RetryPolicy] = {
    "telegram": RetryPolicy(
        name="telegram", max_attempts=4, base_delay=1.0,
        max_delay=60.0, backoff_factor=2.0,
    ),
    "vk": RetryPolicy(
        name="vk", max_attempts=4, base_delay=2.0,
        max_delay=120.0, backoff_factor=2.0,
    ),
    "external_api": RetryPolicy(
        name="external_api", max_attempts=3, base_delay=1.0,
        max_delay=30.0, backoff_factor=2.0,
    ),
}


@dataclass
class BreakerConfig:
    """Конфигурация circuit breaker'а для платформы."""
    failure_threshold: int = 5        # N подряд TRANSIENT/NETWORK failures → open
    recovery_timeout: float = 300.0   # секунд до перехода open → half-open
    half_open_max_calls: int = 1      # пробных вызовов в half-open


class CircuitState:
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitOpenError(Exception):
    """Circuit breaker открыт — вызов заблокирован без обращения к API."""


class CircuitBreaker:
    """
    Sprint 74.2: Circuit Breaker (closed/open/half-open) per-platform.

    - closed:  нормальный режим; подряд failure_threshold TRANSIENT/NETWORK
               ошибок → open
    - open:    вызовы блокируются сразу (CircuitOpenError), API не долбится;
               после recovery_timeout → half-open
    - half_open: пропускает до half_open_max_calls пробных вызовов;
               успех → closed, провал → open снова
    """

    def __init__(self, name: str, config: Optional[BreakerConfig] = None):
        self.name = name
        self.config = config or BreakerConfig()
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.half_open_calls = 0
        self.opened_at: Optional[float] = None
        self.last_error: Optional[str] = None
        self.total_opens = 0

    @staticmethod
    def _now() -> float:
        import time
        return time.monotonic()

    def is_available(self) -> bool:
        """Можно ли выполнить вызов сейчас?"""
        if self.state == CircuitState.CLOSED:
            return True
        if self.state == CircuitState.OPEN:
            if self.opened_at is not None and \
                    (self._now() - self.opened_at) >= self.config.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                # consume one probe slot on transition
                self.half_open_calls = 1
                logger.info(f"[{self.name}] circuit breaker: open → half_open (probe allowed)")
                return True
            return False
        # half_open: ограниченное число пробных вызовов
        if self.half_open_calls < self.config.half_open_max_calls:
            self.half_open_calls += 1
            return True
        return False

    def record_success(self) -> None:
        if self.state == CircuitState.HALF_OPEN:
            logger.info(f"[{self.name}] circuit breaker: half_open probe OK → closed")
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count += 1
        self.half_open_calls = 0
        self.opened_at = None

    def record_failure(self, error_msg: str = "") -> None:
        self.last_error = error_msg
        if self.state == CircuitState.HALF_OPEN:
            self._open("probe failed in half_open")
            return
        self.failure_count += 1
        if self.failure_count >= self.config.failure_threshold:
            self._open(f"{self.failure_count} consecutive failures")

    def _open(self, reason: str) -> None:
        self.state = CircuitState.OPEN
        self.opened_at = self._now()
        self.total_opens += 1
        logger.error(
            f"[{self.name}] circuit breaker OPENED ({reason}); "
            f"retry allowed after {self.config.recovery_timeout:.0f}s"
        )
        # Sprint 74.5: Telegram alert при открытии breaker (fire-and-forget)
        try:
            from backend.core.alerts import send_alert
            import threading
            msg = (
                f"🔴 <b>Circuit Breaker OPEN</b>\n"
                f"Platform: <code>{self.name}</code>\n"
                f"Consecutive failures: {self.failure_count}\n"
            )
            if self.last_error:
                msg += f"Last error: <code>{self.last_error[:200]}</code>"
            threading.Thread(
                target=lambda: __import__("asyncio").run(send_alert(msg)),
                daemon=True,
            ).start()
        except Exception:  # pragma: no cover — защита основного потока
            pass

    def snapshot(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "state": self.state,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "total_opens": self.total_opens,
            "last_error": self.last_error,
            "recovery_timeout": self.config.recovery_timeout,
        }


def get_policy(name: str) -> RetryPolicy:
    """Получить политику по имени (fallback — external_api)."""
    return RETRY_POLICIES.get(name, RETRY_POLICIES["external_api"])


# Per-platform breaker конфиги и реестр (Sprint 74.2)
BREAKER_CONFIGS: Dict[str, BreakerConfig] = {
    "telegram": BreakerConfig(failure_threshold=5, recovery_timeout=300.0),
    "vk": BreakerConfig(failure_threshold=5, recovery_timeout=600.0),
    "external_api": BreakerConfig(failure_threshold=8, recovery_timeout=120.0),
}

_CIRCUIT_BREAKERS: Dict[str, CircuitBreaker] = {}


def get_breaker(platform: str) -> CircuitBreaker:
    """Получить (создать при необходимости) breaker для платформы."""
    if platform not in _CIRCUIT_BREAKERS:
        config = BREAKER_CONFIGS.get(platform, BREAKER_CONFIGS["external_api"])
        _CIRCUIT_BREAKERS[platform] = CircuitBreaker(platform, config)
    return _CIRCUIT_BREAKERS[platform]


def all_breakers() -> Dict[str, CircuitBreaker]:
    return dict(_CIRCUIT_BREAKERS)


def reset_breakers() -> None:
    """Сброс всех breakers (для тестов/админ-действий)."""
    _CIRCUIT_BREAKERS.clear()


# ---------------------------------------------------------------------------
# Sprint 74.2: Channel-wide pause (rate limiter ↔ retry)
# ---------------------------------------------------------------------------

class ChannelPausedError(Exception):
    """Весь канал на паузе после 429 — публикации приостановлены."""


_channel_pauses: Dict[str, float] = {}  # channel_id → monotonic until


def pause_channel(channel_id: str, seconds: float) -> None:
    """Пауза всех публикаций канала (например, после Telegram 429)."""
    until = CircuitBreaker._now() + max(0.0, seconds)
    _channel_pauses[channel_id] = max(_channel_pauses.get(channel_id, 0.0), until)
    logger.warning(f"[{channel_id}] channel-wide pause for {seconds:.1f}s (rate limit)")


def channel_paused(channel_id: Optional[str]) -> float:
    """Сколько секунд канал ещё на паузе (0 — не на паузе)."""
    if not channel_id or channel_id not in _channel_pauses:
        return 0.0
    remaining = _channel_pauses[channel_id] - CircuitBreaker._now()
    if remaining <= 0:
        _channel_pauses.pop(channel_id, None)
        return 0.0
    return remaining


def channel_pause_key(channel) -> Optional[str]:
    """
    Sprint 74.3: ключ паузы для канала (UUID → chat_id / vk_group_id).

    Пауза в reliability.py ключуется по тому же идентификатору, что publisher
    передаёт как channel_id в with_retry:
    - Telegram: chat_id (например "@chan" или "-100...")
    - VK:       vk_group_id (нормализованный, с "-" перед числом)
    Возвращает None, если ключ не определен — тогда паузу проверить нельзя.
    """
    platform = getattr(channel, "platform", None) or ""
    if str(platform).lower() == "vk":
        gid = getattr(channel, "vk_group_id", None)
        if not gid:
            return None
        gid = str(gid).replace("club", "").replace("public", "").replace("event", "")
        if not gid.startswith("-"):
            gid = f"-{gid}"
        return gid
    # Telegram (и по умолчанию)
    return getattr(channel, "chat_id", None)


def channel_paused_for(channel) -> float:
    """
    Sprint 74.3: сколько секунд канал ещё на паузе (0 — не на паузе).

    Принимает объект ChannelORM и сопоставляет UUID канала с ключом паузы
    (chat_id / vk_group_id), который используется publisher'ами при 429.
    Позволяет automation/scheduler пропускать канал до запуска пайплайна.
    """
    key = channel_pause_key(channel)
    if not key:
        return 0.0
    return channel_paused(key)


def channel_pauses_snapshot() -> Dict[str, float]:
    """Активные паузы каналов: {channel_id: remaining_seconds}."""
    return {
        cid: channel_paused(cid)
        for cid in list(_channel_pauses.keys())
        if channel_paused(cid) > 0
    }


def reset_channel_pauses(channel_id: Optional[str] = None) -> None:
    """Сброс пауз каналов. Если channel_id указан — снять паузу только с одного канала."""
    if channel_id is None:
        _channel_pauses.clear()
    else:
        _channel_pauses.pop(channel_id, None)


def _classify(exc: Exception) -> ClassifiedError:
    """Классификация ошибки с поддержкой VKError."""
    if isinstance(exc, VKError):
        etype = exc.error_type
        action = {
            ErrorType.TRANSIENT: "retry",
            ErrorType.CONFIGURATION: "alert_disable",
            ErrorType.PERMANENT: "fail",
        }.get(etype, "log")
        return ClassifiedError(
            error_type=etype,
            severity=_ERROR_SEVERITY.get(etype, "medium"),
            message=str(exc),
            original_error=exc,
            action=action,
            metadata={"error_code": exc.error_code, "platform": "vk"},
        )
    return classify_error(exc)


async def with_retry(
    func: Callable,
    *args,
    policy: Optional[RetryPolicy] = None,
    context: Optional[str] = None,
    on_final_failure: Optional[Callable[[Exception], None]] = None,
    sleep: Callable = asyncio.sleep,
    channel_id: Optional[str] = None,
    platform: Optional[str] = None,
    **kwargs,
) -> Any:
    """
    Выполняет async func с retry по политике.

    Retry только для TRANSIENT/NETWORK ошибок. PERMANENT/CONFIGURATION — fail сразу.
    Учитывает Retry-After из 429-ответов.

    Sprint 74.2:
    - Circuit Breaker per-platform: open → вызовы блокируются сразу (CircuitOpenError)
    - Channel-wide pause: 429 ставит на паузу весь канал (ChannelPausedError)
    - CONFIGURATION финальная ошибка → авто-disable канала (is_active=False)

    Args:
        channel_id: идентификатор канала (для channel-wide pause / alert-disable)
        platform: платформа ('telegram'/'vk'/...) — выбирает circuit breaker
    """
    pol = policy or RETRY_POLICIES["external_api"]
    last_exc: Optional[Exception] = None
    label = context or getattr(func, '__name__', 'call')
    breaker = get_breaker(platform or pol.name)

    # Channel-wide pause: fail fast, не долбим API
    paused_for = channel_paused(channel_id)
    if paused_for > 0:
        raise ChannelPausedError(
            f"Channel {channel_id} paused for another {paused_for:.1f}s (rate limit)"
        )

    # Circuit breaker: open → блокируем вызов без обращения к API
    if not breaker.is_available():
        raise CircuitOpenError(
            f"[{breaker.name}] circuit breaker is {breaker.state} "
            f"(last error: {breaker.last_error})"
        )

    for attempt in range(pol.max_attempts):
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                # sync funcs run in thread pool (requests-based publishers)
                result = await asyncio.to_thread(func, *args, **kwargs)
            breaker.record_success()
            return result
        except Exception as exc:
            classified = _classify(exc)
            last_exc = exc

            if not pol.should_retry(classified.error_type):
                logger.error(
                    f"[{pol.name}] {label}: "
                    f"{classified.error_type.value} error — no retry: {classified.message}"
                )
                if classified.error_type == ErrorType.CONFIGURATION:
                    breaker.record_failure(classified.message)
                    _alert_disable_channel(channel_id, classified.message)
                if on_final_failure:
                    on_final_failure(exc)
                raise

            if attempt == pol.max_attempts - 1:
                logger.error(
                    f"[{pol.name}] {label}: "
                    f"max attempts ({pol.max_attempts}) exhausted: {classified.message}"
                )
                breaker.record_failure(classified.message)
                if on_final_failure:
                    on_final_failure(exc)
                raise

            breaker.record_failure(classified.message)

            # 429 / Retry-After → пауза на весь канал, а не только на запрос
            if channel_id and classified.retry_after is not None:
                pause_channel(channel_id, float(classified.retry_after))
                # текущий запрос ждёт Retry-After (последняя попытка уже учтена выше)
                await sleep(float(classified.retry_after))
                raise ChannelPausedError(
                    f"Channel {channel_id} hit rate limit (Retry-After "
                    f"{classified.retry_after}s); publication aborted"
                )

            delay = pol.delay_for(attempt, classified.retry_after)
            logger.warning(
                f"[{pol.name}] {label}: "
                f"{classified.error_type.value} error (attempt {attempt + 1}/{pol.max_attempts}): "
                f"{classified.message}. Retrying in {delay:.1f}s..."
            )
            await sleep(delay)

    raise last_exc  # pragma: no cover — недостижимо при корректном цикле


def _alert_disable_channel(channel_id: Optional[str], error_msg: str) -> None:
    """
    Sprint 74.2: авто-disable канала при CONFIGURATION-ошибке (alert_disable).

    Ставит ChannelORM.is_active=False, чтобы планировщик больше не выбирал канал,
    и пишет запись в pipeline_failures через error_logger.
    Ошибки не пробрасываются — disable не должен ломать основной поток.
    """
    if not channel_id:
        return
    logger.error(f"[alert_disable] disabling channel {channel_id}: {error_msg}")
    try:
        from core.models.channel_orm import ChannelORM
        from core.database import SessionLocal
        from backend.core.error_logger import get_error_logger, ErrorType as DBErrorType

        db = SessionLocal()
        try:
            ch = db.query(ChannelORM).filter(ChannelORM.id == channel_id).first()
            if ch is None:
                # допускаем передачу chat_id вместо id
                ch = db.query(ChannelORM).filter(ChannelORM.chat_id == channel_id).first()
            if ch is None:
                logger.warning(f"[alert_disable] channel {channel_id} not found in DB")
                return
            if ch.is_active:
                ch.is_active = False
                db.commit()
                logger.error(f"[alert_disable] channel {channel_id} ({ch.name}) disabled")
                # Sprint 74.5: Telegram alert при auto-disable (fire-and-forget)
                try:
                    from backend.core.alerts import send_alert
                    import threading
                    msg = (
                        f"⚠️ <b>Channel Auto-Disabled</b>\n"
                        f"Channel: <code>{ch.name}</code> ({ch.id})\n"
                        f"Reason: <code>{error_msg[:200]}</code>"
                    )
                    threading.Thread(
                        target=lambda: __import__("asyncio").run(send_alert(msg)),
                        daemon=True,
                    ).start()
                except Exception:  # pragma: no cover
                    pass
            get_error_logger(db).log_error(
                channel_id=ch.id,
                pipeline="publishing",
                job="alert_disable",
                error_type=DBErrorType.EXCEPTION,
                error_message=f"Channel auto-disabled (CONFIGURATION error): {error_msg}",
                error_code="alert_disable",
            )
        finally:
            db.close()
    except Exception as e:  # pragma: no cover — защита основного потока
        logger.error(f"[alert_disable] failed to disable channel {channel_id}: {e}")


def retry_async(policy_name: str, context: Optional[str] = None):
    """Декоратор: оборачивает async-функцию в with_retry с named policy."""
    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            return await with_retry(
                func, *args, policy=get_policy(policy_name),
                context=context or func.__name__, **kwargs,
            )
        return wrapper
    return decorator
