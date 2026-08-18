"""Monitoring Job - orchestrates health checks + SLA metrics + alerts.

Sprint 12.
- Reads secrets only from env (ALERT_BOT_TOKEN, ALERT_CHAT_ID).
- Never stores credentials.
- Uses HealthCheckEngine (no DB access) for external checks.
- Queries execution_logs for SLA metrics.
- Sends alerts via NotificationEngine with Redis dedup.
"""
import os
import time
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from sqlalchemy import text

from core.database import SessionLocal
from engines.monitoring.engine import HealthCheckEngine
from engines.notifications.engine import NotificationEngine

logger = logging.getLogger(__name__)


class MonitoringJob:
    """Periodic health + SLA monitoring with Telegram alerting."""

    SLA_SUCCESS_THRESHOLD = 0.70
    ALERT_DEDUP_TTL_SECONDS = 3600
    ALERT_DEDUP_PREFIX = "alert:monitoring:"

    def __init__(self):
        self.ollama_url = os.environ.get(
            "OLLAMA_URL", "http://host.docker.internal:11434"
        )
        self.alert_bot_token = os.environ.get("ALERT_BOT_TOKEN")
        self.alert_chat_id = os.environ.get("ALERT_CHAT_ID")

    def _redis_client(self):
        """Best-effort Redis client. Returns None if unavailable."""
        try:
            import redis
            url = os.environ.get("REDIS_URL", "redis://redis:6379/0")
            return redis.from_url(url, socket_timeout=2)
        except Exception as e:
            logger.warning("Redis unavailable (dedup disabled): %s", e)
            return None

    def _should_alert(self, redis_client, key: str, dedup_value: str) -> bool:
        """Returns True if alert should be sent (not deduped).
        
        dedup_value: stable identifier (service name + status), without timestamp.
        """
        if redis_client is None:
            return True
        full_key = f"{self.ALERT_DEDUP_PREFIX}{key}"
        try:
            existing = redis_client.get(full_key)
            if existing and existing.decode("utf-8") == dedup_value:
                return False
            redis_client.setex(full_key, self.ALERT_DEDUP_TTL_SECONDS, dedup_value)
            return True
        except Exception as e:
            logger.warning("Redis dedup failed: %s", e)
            return True

    def _send_alert(self, redis_client, key: str, dedup_value: str, text_msg: str) -> bool:
        """Sends alert if not deduped. Returns True if sent.
        
        dedup_value: stable identifier for dedup (without timestamp).
        text_msg: full message with timestamp for user.
        """
        if not self.alert_bot_token or not self.alert_chat_id:
            logger.info("ALERT_BOT_TOKEN/ALERT_CHAT_ID not set - skipping alert")
            return False
        if not self._should_alert(redis_client, key, dedup_value):
            logger.info("Alert suppressed (dedup): %s", key)
            return False
        try:
            notifier = NotificationEngine(
                bot_token=self.alert_bot_token,
                chat_id=self.alert_chat_id,
            )
            message_id = notifier.send(text_msg)
            return message_id is not None
        except Exception as e:
            logger.error("Alert send failed: %s", e)
            return False

    def _collect_sla_metrics(self) -> Dict[str, Any]:
        """Count success/failed jobs from execution_logs in last 24h."""
        cutoff = datetime.utcnow() - timedelta(hours=24)
        db = SessionLocal()
        try:
            sql = text(
                """
                SELECT
                    COUNT(*) AS total,
                    COUNT(*) FILTER (WHERE status IN ('completed','success','published','ok')) AS success,
                    COUNT(*) FILTER (WHERE status IN ('failed','error')) AS failed
                FROM execution_logs
                WHERE started_at >= :cutoff
                """
            )
            row = db.execute(sql, {"cutoff": cutoff}).first()
            total = int(row.total or 0)
            success = int(row.success or 0)
            failed = int(row.failed or 0)
            rate = (success / total) if total > 0 else 1.0
            return {
                "window_hours": 24,
                "total": total,
                "success": success,
                "failed": failed,
                "success_rate": round(rate, 4),
            }
        except Exception as e:
            logger.warning("SLA metrics query failed: %s", e)
            return {"window_hours": 24, "total": 0, "success": 0, "failed": 0, "success_rate": 1.0, "error": str(e)}
        finally:
            db.close()

    def run(self, channel=None, execution_id: str = None) -> Dict[str, Any]:
        logger.info("MonitoringJob started")
        started = time.time()

        redis_client = self._redis_client()
        alerts_sent = 0
        alerts_suppressed = 0

        # 1. Health checks (no DB access)
        health = HealthCheckEngine(ollama_url=self.ollama_url).run_all(
            telegram_bot_token=self.alert_bot_token
        )

        # 2. Alert on each down service
        for check in health.get("checks", []):
            if check["status"] == "down":
                key = f"down:{check['name']}"
                msg = (
                    f"🚨 AI Media Factory Alert\n\n"
                    f"Service: {check['name']}\n"
                    f"Status: DOWN\n"
                    f"Detail: {check['detail']}\n"
                    f"Latency: {check['latency_ms']}ms\n"
                    f"Time: {datetime.utcnow().isoformat()} UTC\n\n"
                    f"Dashboard: http://localhost:3000"
                )
                dedup_value = f"{check['name']}:{check['status']}:{check['detail']}"
                if self._send_alert(redis_client, key, dedup_value, msg):
                    alerts_sent += 1
                else:
                    alerts_suppressed += 1

        # 3. SLA metrics from execution_logs
        sla = self._collect_sla_metrics()
        if sla["total"] > 0 and sla["success_rate"] < self.SLA_SUCCESS_THRESHOLD:
            key = f"sla:rate:{int(sla['success_rate']*100)}"
            msg = (
                f"📊 AI Media Factory SLA Alert\n\n"
                f"Success rate: {sla['success_rate']*100:.1f}% "
                f"(threshold {self.SLA_SUCCESS_THRESHOLD*100:.0f}%)\n"
                f"Last 24h: {sla['success']}/{sla['total']} jobs succeeded\n"
                f"Failed: {sla['failed']}\n"
                f"Time: {datetime.utcnow().isoformat()} UTC\n\n"
                f"Logs: http://localhost:8000/api/v1/logs"
            )
            if self._send_alert(redis_client, key, msg):
                alerts_sent += 1
            else:
                alerts_suppressed += 1

        result = {
            "status": "ok",
            "health": health,
            "sla": sla,
            "alerts_sent": alerts_sent,
            "alerts_suppressed": alerts_suppressed,
            "runtime_ms": int((time.time() - started) * 1000),
        }
        logger.info(
            "MonitoringJob finished: health=%s sla=%s alerts=%d",
            health["overall"],
            f"{sla['success_rate']*100:.1f}%",
            alerts_sent,
        )
        return result