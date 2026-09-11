# Sprint 76.5 — Source Health & Quarantine

**Дата начала:** 2026-09-11  
**Статус:** IN PROGRESS  
**Цель:** Автоматический мониторинг здоровья источников с quarantine и recovery

---

## 📋 План реализации

### 1. Health Check Engine

**Файл:** `engines/source_health_checker.py`

Функционал:
- Периодическая проверка источников (каждый час, день)
- Валидация RSS feed доступности
- Проверка item count
- Отслеживание failure trends
- Автоматическое определение unhealthy sources

### 2. Source Quarantine Logic

**Файл:** `engines/source_quarantine.py`

Функционал:
- Quarantine threshold (N failures за M дней)
- Auto-quarantine when threshold reached
- Quarantine reason logging
- Recovery conditions

### 3. Source Recovery Engine

**Файл:** `engines/source_recovery.py`

Функционал:
- Periodic recovery attempts
- Recovery threshold (success count needed)
- Gradual re-enablement
- Recovery metrics tracking

### 4. Health Status API

**Файл:** `backend/app/api/v1/source_health.py` (новый)

Endpoints:
- `GET /health/sources` — статус всех источников
- `GET /health/sources/{id}` — детали одного источника
- `GET /health/report` — summary report
- `POST /health/check-now` — force health check
- `POST /health/quarantine/{id}` — manual quarantine
- `POST /health/recover/{id}` — manual recovery

### 5. Tests

**Файл:** `tests/test_source_health.py`

Тесты:
- Health check logic
- Quarantine conditions
- Recovery process
- API endpoints
- Alert generation

---

## 📊 Data Model

### HealthStatus

```python
class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    SICK = "sick"
    QUARANTINED = "quarantined"
    RECOVERING = "recovering"
```

### Health Metrics

```
success_rate > 90%          → HEALTHY
success_rate 70-90%         → DEGRADED
success_rate 30-70%         → SICK
automatic quarantine        → QUARANTINED
gradual recovery            → RECOVERING
```

---

## Acceptance Criteria

- [ ] Health check engine реализован
- [ ] Quarantine logic работает
- [ ] Recovery engine работает
- [ ] API endpoints доступны
- [ ] Тесты написаны (все passed)
- [ ] Полный регресс passed
- [ ] Graceful degradation работает
- [ ] Alerts система готова

---

**Статус:** Starting implementation  
**Estimated time:** 2-3 часа
