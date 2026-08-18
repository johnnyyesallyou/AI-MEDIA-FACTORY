"""Monitoring Engine - external service health checks.

Sprint 12. Architecture rule: engines never access the database.
Only pure HTTP checks here; DB/SLA metrics live in MonitoringJob.
"""
import time
import logging
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)


class HealthCheckEngine:
    """Checks availability of external dependencies."""

    def __init__(self, ollama_url: str = "http://host.docker.internal:11434"):
        self.ollama_url = ollama_url.rstrip("/")

    def _check(self, name: str, fn, timeout: int = 10) -> Dict[str, Any]:
        start = time.time()
        try:
            ok, detail = fn(timeout)
            return {
                "name": name,
                "status": "ok" if ok else "degraded",
                "latency_ms": int((time.time() - start) * 1000),
                "detail": str(detail),
            }
        except Exception as e:
            logger.warning("Health check %s failed: %s", name, e)
            return {
                "name": name,
                "status": "down",
                "latency_ms": int((time.time() - start) * 1000),
                "detail": str(e),
            }

    def check_ollama(self, timeout: int = 10):
        response = requests.get(self.ollama_url + "/api/tags", timeout=timeout)
        response.raise_for_status()
        models = [m.get("name") for m in response.json().get("models", [])]
        return True, "models=%d" % len(models)

    def check_pollinations(self, timeout: int = 20):
        # Memory constraint #1: tiny prompt -> tiny URL, never > 200 chars
        url = "https://image.pollinations.ai/prompt/test?width=64&height=64&nologo=true"
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        size = len(response.content)
        return size > 0, "size=%d" % size

    def check_telegram(self, bot_token: str, timeout: int = 10):
        url = "https://api.telegram.org/bot%s/getMe" % bot_token
        response = requests.get(url, timeout=timeout)
        data = response.json()
        return bool(data.get("ok")), data.get("result", {}).get("username", "")

    def check_vk(self, timeout: int = 10):
        response = requests.get(
            "https://api.vk.com/method/status.get",
            params={"v": "5.199"},
            timeout=timeout,
        )
        return response.status_code == 200, "http=%d" % response.status_code

    def run_all(self, telegram_bot_token: Optional[str] = None) -> Dict[str, Any]:
        checks: List[Dict[str, Any]] = [
            self._check("ollama", self.check_ollama),
            self._check("pollinations", self.check_pollinations, timeout=20),
            self._check("vk_api", self.check_vk),
        ]
        if telegram_bot_token:
            checks.append(
                self._check(
                    "telegram_api",
                    lambda t: self.check_telegram(telegram_bot_token, t),
                )
            )

        down = [c["name"] for c in checks if c["status"] == "down"]
        return {
            "overall": "down" if down else "ok",
            "down_services": down,
            "checks": checks,
        }