"""Monitoring API endpoints for Dashboard integration."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging

from core.database import get_db
from backend.automation.jobs.monitoring_job import MonitoringJob

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@router.get("/status")
async def get_monitoring_status(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get current health status of all external services.
    
    Returns:
        {
            "overall": "ok" | "down",
            "down_services": ["ollama", ...],
            "checks": [
                {"name": "ollama", "status": "ok", "latency_ms": 12, "detail": "models=8"},
                ...
            ],
            "sla": {
                "window_hours": 24,
                "total": 27,
                "success": 27,
                "failed": 0,
                "success_rate": 1.0
            }
        }
    """
    try:
        job = MonitoringJob()
        result = job.run()
        return {
            "status": "ok",
            "health": result["health"],
            "sla": result["sla"],
            "runtime_ms": result["runtime_ms"]
        }
    except Exception as e:
        logger.exception("Monitoring status failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def get_prometheus_metrics(db: Session = Depends(get_db)) -> str:
    """Get monitoring metrics in Prometheus format.
    
    Returns plain text with metrics:
        amf_health_status{service="ollama"} 1
        amf_health_latency_ms{service="ollama"} 12
        amf_sla_success_rate 1.0
        amf_sla_total_jobs 27
        ...
    """
    try:
        job = MonitoringJob()
        result = job.run()
        
        lines = []
        
        # Health metrics
        for check in result["health"]["checks"]:
            status_value = 1 if check["status"] == "ok" else 0
            lines.append(f'amf_health_status{{service="{check["name"]}"}} {status_value}')
            lines.append(f'amf_health_latency_ms{{service="{check["name"]}"}} {check["latency_ms"]}')
        
        # SLA metrics
        sla = result["sla"]
        lines.append(f'amf_sla_success_rate {sla["success_rate"]}')
        lines.append(f'amf_sla_total_jobs {sla["total"]}')
        lines.append(f'amf_sla_success_jobs {sla["success"]}')
        lines.append(f'amf_sla_failed_jobs {sla["failed"]}')
        lines.append(f'amf_sla_window_hours {sla["window_hours"]}')
        
        # Alerts
        lines.append(f'amf_alerts_sent_total {result["alerts_sent"]}')
        lines.append(f'amf_alerts_suppressed_total {result["alerts_suppressed"]}')
        
        return "\n".join(lines)
    
    except Exception as e:
        logger.exception("Prometheus metrics failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-alert")
async def send_test_alert(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Send a test alert to verify notification system.
    
    Returns:
        {"status": "sent", "message_id": "..."}
    """
    import os
    from engines.notifications.engine import NotificationEngine
    
    bot_token = os.environ.get("ALERT_BOT_TOKEN")
    chat_id = os.environ.get("ALERT_CHAT_ID")
    
    if not bot_token or not chat_id:
        raise HTTPException(
            status_code=400,
            detail="ALERT_BOT_TOKEN and ALERT_CHAT_ID must be set in environment"
        )
    
    try:
        notifier = NotificationEngine(bot_token=bot_token, chat_id=chat_id)
        message_id = notifier.send(
            "🧪 AI Media Factory Test Alert\n\n"
            "Notification system is working correctly.\n"
            f"Time: {datetime.utcnow().isoformat()} UTC\n\n"
            "Dashboard: http://localhost:3000"
        )
        
        if message_id:
            return {"status": "sent", "message_id": message_id}
        else:
            raise HTTPException(status_code=500, detail="Failed to send test alert")
    
    except Exception as e:
        logger.exception("Test alert failed")
        raise HTTPException(status_code=500, detail=str(e))