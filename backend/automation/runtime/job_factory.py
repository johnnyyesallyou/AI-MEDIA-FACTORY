"""
Job Factory — реестр node_type -> Job class.

Runtime получает jobs ТОЛЬКО через фабрику:
    job = JobFactory.create("writing")

Добавить новый движок = зарегистрировать класс. Runtime не меняется.
Aliases поддерживают исторические имена нод (brief, evaluator, publisher).
"""
import logging
from typing import Dict, List, Optional, Type

logger = logging.getLogger(__name__)


class JobFactory:
    _registry: Dict[str, Type] = {}

    @classmethod
    def register(cls, node_type: str, job_class: Type = None, aliases: List[str] = None):
        """
        Регистрация job class. Можно как декоратор или прямым вызовом:
            JobFactory.register("research", ResearchJob)
            JobFactory.register("writing", WritingJob, aliases=["brief"])
        """
        def _register(kls: Type) -> Type:
            cls._registry[node_type] = kls
            for alias in (aliases or []):
                cls._registry[alias] = kls
            logger.info(
                "JobFactory registered: %s -> %s (aliases: %s)",
                node_type, kls.__name__, aliases or []
            )
            return kls

        if job_class is not None:
            return _register(job_class)
        return _register

    @classmethod
    def create(cls, node_type: str):
        """Создаёт instance job по node_type. None если тип неизвестен."""
        job_class = cls._registry.get(node_type)
        if not job_class:
            return None
        return job_class()

    @classmethod
    def is_known(cls, node_type: str) -> bool:
        return node_type in cls._registry

    @classmethod
    def known_types(cls) -> List[str]:
        return sorted(set(cls._registry.keys()))