"""Hermetic tests for Alerting (Sprint 44)."""
import time

from core.alerts import Alert, AlertEvaluator, NotificationService


def fake_health():
    return {
        "status": "degraded",
        "components": {
            "database": {"status": "ok"},
            "publishers": {"status": "degraded"},
            "sources": {"status": "error", "error": "all down"},
        },
    }


def fake_prom(expr):
    if "errors_total" in expr:
        return 0.9  # выше порога 0.5
    if "failed" in expr:
        return 7.0  # выше порога 5
    return 0.0


def test_evaluate_rules():
    ev = AlertEvaluator(health_fn=fake_health, prom_fn=fake_prom)
    alerts = ev.evaluate()
    keys = {a.key for a in alerts}
    assert "component_down:sources" in keys
    assert "component_degraded:publishers" in keys
    assert "high_error_rate" in keys
    assert "job_failures" in keys


def test_severity_mapping():
    ev = AlertEvaluator(health_fn=fake_health, prom_fn=fake_prom)
    by_key = {a.key: a for a in ev.evaluate()}
    assert by_key["component_down:sources"].severity == "critical"
    assert by_key["high_error_rate"].severity == "critical"
    assert by_key["job_failures"].severity == "warning"


def test_format_contains_title():
    a = Alert(key="k", severity="critical", title="Boom", body="details")
    text = a.format()
    assert "Boom" in text and "details" in text and "🔴" in text


def test_cooldown_dedup():
    ns = NotificationService(cooldown_sec=1800)
    a = Alert(key="dup", severity="warning", title="T", body="B")
    # Первый вызов: telegram не настроен -> logged (send возвращает False, но cooldown ставится)
    ns.send(a)
    assert ns.logged_count == 1
    # Второй вызов в течение cooldown: не логируется
    ns.send(a)
    assert ns.logged_count == 1


def test_no_alerts_when_healthy():
    ev = AlertEvaluator(
        health_fn=lambda: {"status": "ok", "components": {"database": {"status": "ok"}}},
        prom_fn=lambda expr: 0.0,
    )
    assert ev.evaluate() == []