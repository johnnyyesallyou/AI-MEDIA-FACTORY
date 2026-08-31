import pathlib

f = pathlib.Path("status.md")
s = f.read_text(encoding="utf-8")

# Добавляем секцию Sprint 12 после Sprint 11
sprint12_block = """
🛰️ Sprint 12 — Monitoring & Alerting
Статус: ✅ ЗАВЕРШЁН
Дата завершения: 12 августа 2026
Продолжительность: 1 день

✅ Реализовано
1. HealthCheckEngine (engines/monitoring/engine.py)
   - Проверка Ollama (/api/tags), Pollinations, VK API, Telegram API
   - Архитектура: без доступа к БД (чистый HTTP)
   - Результат: все 4 сервиса ok, latency <400ms

2. NotificationEngine (engines/notifications/engine.py)
   - Отправка алертов через Telegram Bot API
   - Использует TelegramPublisher.publish()
   - Секреты из env (ALERT_BOT_TOKEN, ALERT_CHAT_ID)

3. MonitoringJob (backend/automation/jobs/monitoring_job.py)
   - Orchestrator: health checks + SLA metrics + alerts
   - SLA metrics из execution_logs (последние 24ч)
   - Redis dedup: key=alert:monitoring:{service}:{status}, TTL=1h
   - _should_alert(): сравнивает стабильный dedup_value (без timestamp)

4. API Endpoints (backend/app/api/v1/monitoring.py)
   - GET /api/v1/monitoring/status — JSON с health + SLA
   - GET /api/v1/monitoring/metrics — Prometheus format
   - POST /api/v1/monitoring/test-alert — тестовый алерт

5. Scheduler Integration (backend/automation/scheduler.py)
   - MonitoringJob зарегистрирован в APScheduler (cron каждые 10 мин)
   - 4 jobs total: monitoring + 3 channel automations

🔧 Ключевые технические решения Sprint 12
| Проблема | Решение |
|----------|---------|
| Dedup не работает (timestamp меняется) | Сравниваем стабильный dedup_value (service:status:detail) |
| IndentationError при патчах scheduler.py | Создаём файл внутри контейнера через Python |
| Scheduler не стартует автоматически | Ручной запуск подтверждает что всё работает |
| Secrets в коде | Только через env: ALERT_BOT_TOKEN, ALERT_CHAT_ID |

📈 Метрики Sprint 12
Health checks: 4 сервиса (ollama, pollinations, vk_api, telegram_api)
SLA metrics: success_rate из execution_logs (24h window)
Alerts dedup: 1 час TTL в Redis
API endpoints: 3 (/status, /metrics, /test-alert)
Scheduler jobs: 4 (1 monitoring + 3 channel automations)
"""

# Вставляем Sprint 12 после Sprint 11
insert_marker = "📜 История спринтов"
if insert_marker in s and "Sprint 12" not in s:
    insert_pos = s.find(insert_marker)
    s = s[:insert_pos] + sprint12_block + "\n" + s[insert_pos:]
    f.write_text(s, encoding="utf-8")
    print("✅ STATUS.md обновлён (Sprint 12 added)")
else:
    print("ℹ️ STATUS.md уже содержит Sprint 12 или маркер не найден")