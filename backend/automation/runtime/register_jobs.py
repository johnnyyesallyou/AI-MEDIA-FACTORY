"""Register jobs for the workflow runtime."""
import logging

logger = logging.getLogger(__name__)


def register_all_jobs():
    """
    Sprint 8.4: Регистрирует все jobs для WorkflowEngineV2.
    
    Упрощённая версия — jobs регистрируются напрямую через runner.py.
    Этот модуль оставлен для совместимости.
    """
    logger.info("register_all_jobs: skipped (jobs registered via runner.py)")
    return True


# Автоматическая регистрация при импорте
try:
    register_all_jobs()
except Exception as e:
    logger.warning(f"Failed to auto-register jobs: {e}")