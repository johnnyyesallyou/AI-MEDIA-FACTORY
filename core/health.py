"""Health Checks - Sprint 34.

Проверка здоровья компонентов системы.
"""
import logging
from typing import Dict, Any
from sqlalchemy import text
from datetime import datetime

logger = logging.getLogger(__name__)


class HealthChecker:
    """Проверяет здоровье всех компонентов."""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def check_all(self) -> Dict[str, Any]:
        """Проверяет все компоненты."""
        checks = {
            "database": self._check_database(),
            "external_apis": self._check_external_apis(),
            "components": self._check_components(),
        }
        
        overall_healthy = all(
            check["status"] == "healthy"
            for check in checks.values()
        )
        
        return {
            "status": "healthy" if overall_healthy else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": checks,
        }
    
    def _check_database(self) -> Dict[str, Any]:
        """Проверяет подключение к БД."""
        try:
            from core.database import SessionLocal
            db = SessionLocal()
            
            # Простой query для проверки
            result = db.execute(text("SELECT 1")).scalar()
            db.close()
            
            if result == 1:
                return {"status": "healthy", "message": "Database connection OK"}
            else:
                return {"status": "unhealthy", "message": "Unexpected result"}
                
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Database error: {type(e).__name__}: {str(e)[:100]}"
            }
    
    def _check_external_apis(self) -> Dict[str, Any]:
        """Проверяет доступность внешних API."""
        from core.network_config import get_http_session
        
        apis = {
            "anilist": "https://graphql.anilist.co",
            "mangadex": "https://api.mangadex.org",
            "habr": "https://habr.com",
        }
        
        results = {}
        session = get_http_session()
        
        for name, url in apis.items():
            try:
                response = session.get(url, timeout=10)
                if response.status_code < 500:  # 2xx, 3xx, 4xx - OK
                    results[name] = {
                        "status": "healthy",
                        "status_code": response.status_code,
                    }
                else:
                    results[name] = {
                        "status": "unhealthy",
                        "status_code": response.status_code,
                    }
            except Exception as e:
                results[name] = {
                    "status": "unhealthy",
                    "error": f"{type(e).__name__}: {str(e)[:100]}"
                }
        
        all_healthy = all(r["status"] == "healthy" for r in results.values())
        
        return {
            "status": "healthy" if all_healthy else "degraded",
            "apis": results,
        }
    
    def _check_components(self) -> Dict[str, Any]:
        """Проверяет внутренние компоненты."""
        components = {}
        
        # Проверяем что можно импортировать основные модули
        try:
            from engines.cross_source_enricher import CrossSourceEnricher
            components["CrossSourceEnricher"] = {"status": "healthy"}
        except Exception as e:
            components["CrossSourceEnricher"] = {
                "status": "unhealthy",
                "error": str(e)[:100]
            }
        
        try:
            from engines.publishing.image_acquisition import ImageAcquisitionPolicy
            components["ImageAcquisitionPolicy"] = {"status": "healthy"}
        except Exception as e:
            components["ImageAcquisitionPolicy"] = {
                "status": "unhealthy",
                "error": str(e)[:100]
            }
        
        all_healthy = all(c["status"] == "healthy" for c in components.values())
        
        return {
            "status": "healthy" if all_healthy else "degraded",
            "components": components,
        }


def health_check_endpoint() -> Dict[str, Any]:
    """Health check endpoint для monitoring tools."""
    checker = HealthChecker()
    return checker.check_all()