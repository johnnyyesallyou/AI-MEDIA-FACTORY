import datetime
from pathlib import Path

# Читаем текущий STATUS.md
status_file = Path("status.md")
s = status_file.read_text(encoding="utf-8")

# Добавляем секцию Sprint 12 после секции "🎯 Следующие спринты"
if "Sprint 12 — Monitoring & Alerting" not in s:
    sprint12_section = """

🛰️ Sprint 12 — Monitoring & Alerting
Статус: 🔄 В ПРОЦЕССЕ
Дата начала: 12 августа 2026

✅ Шаг 1: HealthCheckEngine
- engines/monitoring/engine.py — HTTP-проверки внешних сервисов
- Проверки: Ollama, Pollinations, Telegram API, VK API
- Архитектура: без доступа к БД (чистый HTTP)
- Результат: все 4 сервиса ok, latency <400ms

✅ Шаг 2: MonitoringJob + Telegram Alerts + Redis Dedup
- backend/automation/jobs/monitoring_job.py — orchestrator
- engines/notifications/engine.py — отправка алертов через Telegram
- Redis dedup: key lert:monitoring:{service}:{status}, TTL 1 час
- SLA metrics: success_rate из execution_logs (последние 24ч)
- Credentials: ALERT_BOT_TOKEN, ALERT_CHAT_ID из env (безопасно)
- Тест: первый run отправляет алерт, второй run подавляет (dedup работает)

⏳ Шаг 3: API Endpoints (следующий)
- GET /api/v1/monitoring/status — текущее состояние
- GET /api/v1/monitoring/metrics — Prometheus format

⏳ Шаг 4: Scheduler Cron (каждые 10 мин)

⏳ Шаг 5: Prometheus + Grafana (опционально)
"""
    # Вставляем перед "🚀 Запуск проекта"
    insert_pos = s.find("🚀 Запуск проекта")
    if insert_pos != -1:
        s = s[:insert_pos] + sprint12_section + "\n" + s[insert_pos:]
        status_file.write_text(s, encoding="utf-8")
        print("✅ STATUS.md обновлён (добавлен Sprint 12)")
else:
    print("ℹ️ STATUS.md уже содержит Sprint 12")

# Обновляем TASK.md
task_update = """# AI Media Factory
Current Task

Task:
Sprint 12 - Monitoring & Alerting.

Status:
In Progress

Current Objective
Make the platform observable and self-alerting before adding new platforms.

Steps
Step 1: HealthCheckEngine (Ollama, Pollinations, Telegram, VK) - external HTTP checks, no DB.
Status: Completed

Step 2: NotificationEngine (Telegram alerts) + alert dedup via Redis.
Status: Completed

Step 3: MonitoringJob (health + SLA metrics from execution_logs) + scheduler cron every 10 min.
Status: In Progress (job done, scheduler pending)

Step 4: API endpoint /api/v1/monitoring/status + /metrics (Prometheus format).
Status: Pending

Step 5: Prometheus + Grafana in docker-compose (optional phase).
Status: Pending

Step 6: Update STATUS.md, docs, tests.
Status: Pending

Rules
Do not break working publishing pipeline.
Engines must not access database.
Secrets only via environment variables.
Update STATUS.md after each step.

End Task
"""

Path("TASK.md").write_text(task_update, encoding="utf-8")
print("✅ TASK.md обновлён (Sprint 12 шаг 2 completed)")

# Добавляем в MEMORY.md
memory_update = """

==========================================================
SPRINT 12 PROGRESS - 2026-08-12
==========================================================

MONITORING IMPLEMENTATION:
1. HealthCheckEngine (engines/monitoring/engine.py):
   - check_ollama(): GET /api/tags, returns models count
   - check_pollinations(): tiny URL test (64x64), validates size>0
   - check_telegram(): getMe with bot_token, returns username
   - check_vk(): status.get, validates HTTP 200
   - run_all(): returns {overall: ok/down, down_services: [], checks: []}

2. NotificationEngine (engines/notifications/engine.py):
   - send(text): uses TelegramPublisher.publish()
   - Returns message_id or None on failure

3. MonitoringJob (backend/automation/jobs/monitoring_job.py):
   - Reads ALERT_BOT_TOKEN, ALERT_CHAT_ID from env (security rule)
   - Runs HealthCheckEngine.run_all()
   - Queries execution_logs for SLA metrics (last 24h)
   - Sends alerts for down_services and success_rate<0.70
   - Redis dedup: key=alert:monitoring:{service}:{status}:{detail}, TTL=3600s
   - _should_alert(): compares stable dedup_value (without timestamp)
   - Returns: {health, sla, alerts_sent, alerts_suppressed, runtime_ms}

TESTING RESULTS:
- All 4 services healthy (ollama 8 models, pollinations 2KB, vk 200, telegram ok)
- Forced Ollama down (localhost:9999) -> alert sent to Telegram
- Second run -> alert suppressed (Redis dedup working)
- SLA: 27/27 success (100%) last 24h

NEXT: API endpoints + scheduler cron
"""

with open("docs/ai/MEMORY.md", "a", encoding="utf-8") as f:
    f.write(memory_update)
print("✅ MEMORY.md обновлён (Sprint 12 progress)")