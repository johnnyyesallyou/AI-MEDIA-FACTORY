"""Alerting - Sprint 44.

Monitoring → AlertEvaluator → NotificationService → Telegram / log.

Правила:
- component_down   : health компонент == error        → CRITICAL
- component_degraded: health компонент == degraded    → WARNING
- high_error_rate  : rate(amf_errors_total[5m]) > 0.5 → CRITICAL
- job_failures     : increase(failed jobs, 1h) > 5    → WARNING

Dedup: cooldown 30 минут на каждый alert key (не спамим).
Если Telegram не настроен — alert пишется в log (graceful degradation).
"""
import asyncio
import logging
import os
import time
from typing import Callable, Dict, List, Optional

import requests

from core.database import SessionLocal
from core.models.channel_orm import ChannelORM


logger = logging.getLogger(__name__)

DASHBOARD_URL = os.getenv("DASHBOARD_URL", "http://localhost:3001")


class Alert:
    def __init__(self, key: str, severity: str, title: str, body: str):
        self.key = key
        self.severity = severity  # critical | warning
        self.title = title
        self.body = body

    def format(self) -> str:
        icon = "🔴" if self.severity == "critical" else "🟡"
        return (
            f"{icon} <b>AI MEDIA FACTORY</b>\n\n"
            f"<b>{self.title}</b>\n"
            f"{self.body}\n\n"
            f"<i>{time.strftime('%Y-%m-%d %H:%M:%S')}</i>"
        )


def get_bot_token() -> str:
    """Токен из env или из первого подключённого telegram-канала."""
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    if token and "here" not in token:
        return token
    try:
        db = SessionLocal()
        try:
            channels = db.query(ChannelORM).all()
            for ch in channels:
                for attr in ("bot_token", "telegram_bot_token", "access_token"):
                    v = getattr(ch, attr, None)
                    if v:
                        return v
        finally:
            db.close()
    except Exception as e:
        logger.debug(f"token lookup failed: {e}")
    return ""


class NotificationService:
    """Отправка алертов в Telegram (fallback: log)."""

    def __init__(self, cooldown_sec: int = 1800):
        self.cooldown_sec = cooldown_sec
        self._sent_at: Dict[str, float] = {}
        self.sent_count = 0
        self.logged_count = 0

    def should_send(self, key: str) -> bool:
        last = self._sent_at.get(key, 0)
        return (time.time() - last) >= self.cooldown_sec

    def send(self, alert: Alert) -> bool:
        if not self.should_send(alert.key):
            return False
        self._sent_at[alert.key] = time.time()

        text = alert.format()
        token = get_bot_token()
        chat_id = os.getenv("ALERTS_CHAT_ID", "")

        if not token or not chat_id:
            # Graceful degradation: в log
            logger.warning(f"ALERT [{alert.severity}] {alert.title} | {alert.body}")
            self.logged_count += 1
            return False

        try:
            r = requests.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": "HTML",
                    "reply_markup": {
                        "inline_keyboard": [[
                            {"text": "📊 Dashboard", "url": DASHBOARD_URL},
                            {"text": "️ Automation", "url": f"{DASHBOARD_URL}/automation"},
                            {"text": "📺 Channels", "url": f"{DASHBOARD_URL}/channels"},
                        ]]
                    },
                },
                timeout=10,
            )
            if r.status_code == 200:
                self.sent_count += 1
                logger.info(f"Alert sent to Telegram: {alert.title}")
                return True
            logger.error(f"Telegram send failed: {r.status_code}")
        except Exception as e:
            logger.error(f"Telegram send error: {e}")
        return False


class AlertEvaluator:
    """Оценка правил. health_fn/prom_fn инжектятся для тестируемости."""

    def __init__(
        self,
        health_fn: Optional[Callable] = None,
        prom_fn: Optional[Callable] = None,
    ):
        self.health_fn = health_fn or self._default_health
        self.prom_fn = prom_fn or self._default_prom

    @staticmethod
    def _default_health() -> Dict:
        from core.health_unified import UnifiedHealthService
        return UnifiedHealthService().get_overall_status()

    @staticmethod
    def _default_prom(expr: str) -> float:
        for base in ("http://prometheus:9090", "http://localhost:9090"):
            try:
                r = requests.get(
                    f"{base}/api/v1/query", params={"query": expr}, timeout=5
                )
                if r.status_code == 200:
                    res = r.json().get("data", {}).get("result", [])
                    if res:
                        return float(res[0]["value"][1])
            except Exception:
                continue
        return 0.0

    def evaluate(self) -> List[Alert]:
        alerts: List[Alert] = []

        # 1. Health компоненты
        try:
            health = self.health_fn()
            for name, comp in (health.get("components") or {}).items():
                status = comp.get("status") if isinstance(comp, dict) else comp
                if status == "error":
                    alerts.append(Alert(
                        key=f"component_down:{name}",
                        severity="critical",
                        title=f"Component down: {name}",
                        body=f"Статус: ERROR. Детали: {comp.get('error', 'n/a') if isinstance(comp, dict) else ''}",
                    ))
                elif status == "degraded":
                    alerts.append(Alert(
                        key=f"component_degraded:{name}",
                        severity="warning",
                        title=f"Component degraded: {name}",
                        body="Компонент работает в ограниченном режиме.",
                    ))
        except Exception as e:
            logger.error(f"health eval failed: {e}")

        # 2. Error rate
        try:
            err_rate = self.prom_fn("sum(rate(amf_errors_total[5m]))")
            if err_rate > 0.5:
                alerts.append(Alert(
                    key="high_error_rate",
                    severity="critical",
                    title="High error rate",
                    body=f"Error rate: {err_rate:.2f}/sec (порог 0.5) за последние 5 минут.",
                ))
        except Exception as e:
            logger.error(f"error rate eval failed: {e}")

        # 3. Job failures
        try:
            failed = self.prom_fn('sum(increase(amf_jobs_total{status="failed"}[1h]))')
            if failed > 5:
                alerts.append(Alert(
                    key="job_failures",
                    severity="warning",
                    title="Multiple job failures",
                    body=f"{failed:.0f} failed jobs за последний час (порог 5).",
                ))
        except Exception as e:
            logger.error(f"job failures eval failed: {e}")

        return alerts


# ---------- Background loop ----------

_notifier = NotificationService()
_evaluator = AlertEvaluator()


def run_evaluation_once() -> int:
    """Одна итерация оценки. Возвращает число отправленных/залогированных алертов."""
    alerts = _evaluator.evaluate()
    fired = 0
    for a in alerts:
        if _notifier.send(a):
            fired += 1
    return fired


async def start_alerts_loop(interval_sec: int = 60):
    """Фоновая задача: оценка правил каждые interval_sec."""
    logger.info(f"Alerts loop started (interval={interval_sec}s)")
    while True:
        try:
            await asyncio.get_event_loop().run_in_executor(None, run_evaluation_once)
        except Exception as e:
            logger.error(f"alerts loop error: {e}")
        await asyncio.sleep(interval_sec)