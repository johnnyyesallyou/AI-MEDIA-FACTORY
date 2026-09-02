"""Sprint 69.6: PipelineLock — предотвращает параллельные запуски pipeline для одного канала."""
import threading
import logging
from typing import Dict
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Глобальный реестр locks по channel_id
_channel_locks: Dict[str, threading.Lock] = {}
_locks_mutex = threading.Lock()


@contextmanager
def pipeline_lock(channel_id: str, timeout: float = 30.0):
    """
    Context manager для получения эксклюзивного доступа к pipeline канала.
    
    Использование:
        with pipeline_lock(channel_id):
            # только один pipeline для этого канала может работать
            await run_pipeline()
    
    Raises:
        TimeoutError: если lock не получен за timeout секунд
    """
    # Получаем или создаём lock для этого канала
    with _locks_mutex:
        if channel_id not in _channel_locks:
            _channel_locks[channel_id] = threading.Lock()
        lock = _channel_locks[channel_id]
    
    acquired = lock.acquire(timeout=timeout)
    if not acquired:
        logger.warning(f"Pipeline lock timeout for channel {channel_id} after {timeout}s")
        raise TimeoutError(f"Pipeline already running for channel {channel_id}")
    
    try:
        logger.debug(f"Pipeline lock acquired for {channel_id}")
        yield
    finally:
        lock.release()
        logger.debug(f"Pipeline lock released for {channel_id}")

def release_all_locks():
    """Sprint 69.15: принудительное освобождение всех locks (после падений)."""
    global _channel_locks
    released = 0
    for ch_id, lock in list(_channel_locks.items()):
        # Попытаться освободить (если занят)
        if lock.locked():
            try:
                lock.release()
                released += 1
                logger.info(f"Force-released lock for {ch_id}")
            except Exception:
                pass
    # Очистить реестр
    _channel_locks.clear()
    return released
