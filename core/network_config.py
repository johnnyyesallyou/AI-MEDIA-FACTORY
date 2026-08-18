"""Network Configuration - Sprint 34.

Централизованная конфигурация для всех network operations:
- SSL/TLS settings
- Timeouts
- Connection pooling
- Proxy settings (if needed)
"""
import os
import urllib3
from typing import Dict, Any


# Disable SSL warnings (для self-signed certs в контейнере)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class NetworkConfig:
    """Network configuration for all HTTP requests."""
    
    # Timeouts (seconds)
    TIMEOUT_CONNECT = 10.0
    TIMEOUT_READ = 30.0
    TIMEOUT_TOTAL = 60.0
    
    # SSL settings
    SSL_VERIFY = os.getenv("SSL_VERIFY", "false").lower() == "true"
    
    # Connection pool
    POOL_CONNECTIONS = 10
    POOL_MAXSIZE = 20
    
    # Retry settings
    RETRY_TOTAL = 3
    RETRY_BACKOFF = 0.3
    RETRY_STATUS_FORCELIST = [429, 500, 502, 503, 504]
    
    # User-Agent
    USER_AGENT = "AI-Media-Factory/1.0 (Production)"
    
    @classmethod
    def get_requests_config(cls) -> Dict[str, Any]:
        """Возвращает config для requests library."""
        return {
            "timeout": (cls.TIMEOUT_CONNECT, cls.TIMEOUT_READ),
            "verify": cls.SSL_VERIFY,
            "headers": {"User-Agent": cls.USER_AGENT},
        }
    
    @classmethod
    def get_session(cls):
        """Создаёт requests.Session с connection pooling."""
        import requests
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        session = requests.Session()
        
        # Retry strategy
        retry_strategy = Retry(
            total=cls.RETRY_TOTAL,
            backoff_factor=cls.RETRY_BACKOFF,
            status_forcelist=cls.RETRY_STATUS_FORCELIST,
            allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE"],
            raise_on_status=False,
        )
        
        # HTTP adapter with pooling
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=cls.POOL_CONNECTIONS,
            pool_maxsize=cls.POOL_MAXSIZE,
        )
        
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session


# Global session instance (singleton)
_global_session = None


def get_http_session():
    """Возвращает global HTTP session."""
    global _global_session
    if _global_session is None:
        _global_session = NetworkConfig.get_session()
    return _global_session