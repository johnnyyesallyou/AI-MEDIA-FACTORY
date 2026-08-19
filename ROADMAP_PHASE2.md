
# 🚀 Roadmap: Autonomous Media Platform (Phase 2)

## Текущий статус
**Platform Core v1.0** ✅ (Sprint 1-40)
- Sources: ReManga + MangaDex + ReadManga + AniList + Habr
- Publishing: Telegram + VK
- Analytics: PostMetric + ABTest + Dashboard + Grafana
- Automation: ChannelScheduler + EngagementCollection
- Observability: Prometheus + Grafana

---

## Phase 2: Autonomous & Reliable

### Sprint 41 — Production Stabilization 🔴 CRITICAL
**Цель:** система безопасна для постоянной работы

1. **Secrets Management**
   - .env files audit
   - Все токены через environment variables
   - Проверка что секреты не в Git
   - .env.example для разработчиков

2. **Database Backup/Restore**
   - scripts/backup-db.ps1 — pg_dump с timestamp
   - scripts/restore-db.ps1 — pg_restore
   - **Обязательно:** тест восстановления (не просто наличие файла)

3. **Unified Health Endpoints**
GET /api/health
GET /api/health/database
GET /api/health/sources
GET /api/health/publishers
GET /api/health/automation
GET /api/health/prometheus
   Dashboard показывает:
SYSTEM
🟢 Database
🟢 Research (5 sources)
🟢 Telegram
🟢 VK
🟢 Scheduler
🟢 Prometheus

4. **Error Taxonomy**
   Классификация ошибок для авто-реакции:
   - TRANSIENT (429, timeout) → retry с backoff
   - PERMANENT (404, invalid URL) → fail + alert
   - CONFIGURATION (401, missing token) → alert + disable
   - NETWORK (DNS, connection refused) → retry
   - CONTENT (invalid format) → skip + log

5. **Graceful Degradation**
   - Если source unavailable → skip, не crash
   - Если publisher down → queue, retry later
   - Если DB timeout → exponential backoff

**Результат:** система может работать **неделями без ручного вмешательства**

---

### Sprint 42 — CI/CD + Automated Testing 🔴 CRITICAL
**Цель:** качество и безопасность изменений

1. **GitHub Actions Pipeline**
   `yaml
   git push → pytest → lint → migration check → docker build → deploy
2. Test Coverage
Knowledge Layer tests (deduplication, enrichment)
Research tests (all 5 sources)
Publishing tests (Telegram, VK)
Image Policy tests (real covers for manga/anime)
Channel isolation tests
A/B testing tests (Welch t-test)
3. Linting
Black (formatting)
Ruff (linting)
MyPy (type checking)
4. Migration Safety
Alembic для schema migrations
Auto-detect breaking changes
Dry-run перед apply
Результат: ручное тестирование больше не bottleneck
Sprint 43 — Unified Analytics Dashboard 🟠 HIGH
Цель: Dashboard становится центральной консолью
Текущая архитектура:
Application → Prometheus → Grafana (технический инструмент)
Новая архитектура:
Dashboard → Backend /api/metrics/* → Prometheus
Две секции в Analytics:
BUSINESS:
Posts, Views, Likes, Engagement Rate
Best channels, Best times, Best content
A/B tests (winner, improvement, confidence)
Top performers (by metric)
SYSTEM:
Jobs/sec, Posts/sec, Error rate
p95 duration, Queue size
Workers status
Source health (5/5 up)
Channel health (3 active, 1 paused)
Результат: всё управление в одном месте
Sprint 44 — Telegram Alerts 🟠 HIGH
Цель: мониторинг приходит к вам сам
Архитектура:
Monitoring (Prometheus rules)
      ↓
Alert Manager (eval rules)
      ↓
Notification Service (format + send)
      ↓
Telegram (message + buttons)
Alert примеры:
🔴 AI MEDIA FACTORY

Channel: Anime News
Job: ResearchJob
Error rate: 43% (12/28 attempts)

Last error:
AniList API timeout after 30s

Timestamp: 2026-08-20 14:32:00

Actions:
[🔄 Retry Now] [⏸️ Disable Channel] [📊 View Logs]
Результат: вы знаете о проблемах до того, как они стали критичными
Sprint 45 — Autonomous Engagement Loop 🟢 VERY IMPORTANT
Цель: система учится на результатах
Замкнутый контур:
            ┌──────────────┐
            │   Research   │
            └──────┬───────┘
                   ↓
              Publishing
                   ↓
             Engagement ←──── EngagementCollectionJob (periodic)
                   ↓
               Analytics ←── PostMetric aggregation
                   ↓
             Optimization ←─ HeadlineOptimizer + PostingTimeOptimizer
                   ↓
          ┌────────┴────────┐
          ↓                 ↓
    Content rules      Posting schedule
          ↓                 ↓
          └───────┬─────────┘
                  ↓
              Research (with learned rules)
Реализация:
ContentOptimizer — анализирует топ-посты, генерирует rules
ScheduleOptimizer — обновляет posting times на основе engagement
A/B testing — автоматическое применение winners
Feedback loop — метрики влияют на следующий research
Результат: система учится и улучшается без ручного вмешательства
Sprint 46 — New Publishing Platforms 🟢 POST-STABILIZATION
Цель: расширение дистрибуции
Платформы:
Dzen (статьи + видео)
YouTube (video shorts)
Threads (micro-posts)
Medium (long-form)
Архитектура:
Unified Publication Interface
        ↓
Publisher Factory
        ↓
┌─────────┬─────┬─────┬────────┬────────┐
│Telegram │ VK  │Dzen │YouTube │Threads │
└─────────┴─────┴─────┴────────┴────────┘
Преимущество: новый publisher почти не затрагивает остальную систему (благодаря Publishing Layer из Sprint 28)
Результат: мультиплатформенная дистрибуция
Sprint 47+ — Dashboard / Channel Management 🚀
Цель: управление через UI без кода
Идеальный user flow:
Создать канал → указать тематику
Выбрать источники (ReManga, AniList, Habr)
Подключить Telegram/VK (бот-токены)
Настроить правила (frequency, filters)
Нажать Start
Система работает сама
Результат: AI Media Factory как продукт
📊 Метрики успеха Phase 2
Метрика
Текущее
Цель (Sprint 45)
Uptime (без manual intervention)
часы
недели
Error rate (critical)
неизвестно
< 1%
Test coverage
0%
> 80%
Time to recover (backup restore)
неизвестно
< 5 мин
Alerts false positive rate
N/A
< 5%
Autonomous optimization
нет
100%

🎯 Следующий шаг: Sprint 41 — Production Stabilization
План:
Secrets audit (проверить .env, tokens в коде)
DB backup/restore scripts + TEST
Unified health endpoints
Error taxonomy + graceful degradation
Документация "Emergency Procedures"
Критерии успеха:
✅ Все секреты в environment variables
✅ Backup создан и восстановлен
✅ /api/health показывает статус всех компонентов
✅ Ошибки классифицированы и обрабатываются правильно
✅ Система может работать 24/7 без вмешательства
Начинаем Sprint 41?
