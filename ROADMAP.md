# AI Media Factory — Roadmap

## Текущая фаза: Phase 3 — Productization

**Цель:** превратить AI Media Factory из набора работающих пайплайнов в **продукт**, где пользователь может создать канал за 5 минут и оставить его работать автономно.

**KPI:** *«Могу ли я создать новый канал за несколько минут и оставить его работать автономно?»*

---

## 🎯 Phase 3 — Productization (текущая)

### ✅ Sprint 53 — Channel Config + Source Registry (ЗАВЕРШЁН)

**Сделано:**
- ✅ \SourceRegistry\ с 9 self-describing sources
- ✅ API \/sources/\ (list, filter, validate)
- ✅ Миграция 4 каналов на новую схему
- ✅ \lag_modified\ для JSONB tracking
- ✅ Исправлен Anime channel (RSS → AniList/MAL)

**Статус:** 🎉 Закрыт

---

### ✅ Sprint 54 — Formatter Layer (ЗАВЕРШЁН)

**Проблема:** формат поста захардкожен внутри publish_job-ов

**Что будет создано:**
- \engines/formatters/base.py\ — \BaseFormatter\ interface
- \engines/formatters/manga_formatter.py\
- \engines/formatters/news_formatter.py\
- \engines/formatters/anime_formatter.py\
- \engines/formatters/formatter_registry.py\
- Рефакторинг publish_job-ов на использование formatter-ов

**Результат:**
- Формат определяется \channel_profile\, а не job-ом
- Можно добавить новый тип контента без нового job
- Основа для Sprint 55 (Wizard)

**Статус:** 🚧 В работе

---

### ✅ Sprint 55 — Channel Wizard + AI Suggestion (ЗАВЕРШЁН)

**Что будет создано:**
- POST \/wizard/suggest\ — AI предлагает config по названию
- POST \/wizard/validate\ — backend валидирует
- AI НЕ источник истины, только предложение
- Frontend: 5-7 step wizard

**UI Flow:**
\\\
Название: [ Манга — новые главы ]
    ↓
AI: "Определил: manga / new_chapters / RU"
    ↓
Источники: ☑ ReManga ☑ MangaDex ☑ ReadManga
    ↓
Язык: ● Русский
    ↓
Формат: preview поста
    ↓
Telegram: [ Подключить ]
    ↓
[ Создать канал ]
\\\

**Статус:** 📋 Planned

---

### ✅ Sprint 56 — One-Click START + Dashboard (ЗАВЕРШЁН)

**Что будет создано:**
- POST \/channels/{id}/start\ — активирует cron job
- POST \/channels/{id}/pause\
- GET \/channels/{id}/status\ — last run, next run, stats
- Frontend: карточки каналов с метриками

**UI:**
\\\
┌──────────────────────────────────┐
│  Манга — новые главы             │
│  ● Telegram connected            │
│  ● 3 sources connected           │
│  ● Schedule: 30 min              │
│                                  │
│  Last research:  17:00           │
│  Last publish:   17:02           │
│  Next run:       17:30           │
│                                  │
│          [ ▶ START ]             │
└──────────────────────────────────┘
\\\

**Статус:** 📋 Planned

---

### ✅ Sprint 57 — History + Analytics (ЗАВЕРШЁН)

**Что будет создано:**
- История постов с метриками
- "Что работает" на дашборде
- Analytics Collector (cron каждый час)
- Таблицы: \post_history\, \post_metrics\, \channel_learnings\

**Статус:** 📋 Planned

---

### ✅ Sprint 58 — Learning Loop (ЗАВЕРШЁН) — Learning Loop UI

**Что будет создано:**
- Post performance → Analytics → Learning → Recommendation
- "Посты с коротким описанием получают +27% просмотров"
- Система предлагает изменение → пользователь подтверждает

**Статус:** 📋 Planned

---

### 📋 Sprint 59 — AI Channel Creator

**Что будет создано:**
- "Создай канал по описанию" → LLM генерирует config proposal
- Пользователь подтверждает → канал создан

**Статус:** 📋 Planned

---

## 🚀 Phase 4 — Expansion (после Phase 3)

### Sprint 60+ — Video Manager
- Pexels API (бесплатное видео)
- Runway ML (генерация, платная)
- Fallback: видео → изображение

### Sprint 61+ — Dzen Publisher
- Dzen API интеграция
- Публикация видео + статей

### Sprint 62+ — YouTube
- YouTube API
- Публикация Shorts

### Sprint 63+ — Новые источники
- Дополнительные manga/anime/news источники
- Custom RSS (UI для добавления)

### Sprint 64+ — Новые AI capabilities
- Image generation (DALL-E, Stable Diffusion)
- Video generation (Sora, Pika Labs)
- Voice generation

---

## 📊 Progress Tracking

| Sprint | Status | Start | End | Commits |
|--------|--------|-------|-----|---------|
| 46.1A-47 | ✅ Done | - | - | Foundation |
| 48 | ✅ Done | - | - | JobFactory |
| 49 | ✅ Done | - | - | Conditional Status |
| 50 | ✅ Done | - | - | PostMetric |
| 51 | ✅ Done | - | - | Rich Posts |
| 52 | ✅ Done | - | - | Channel Cleanup |
| 52B | ✅ Done | - | - | News Pipeline |
| 52C | ✅ Done | - | - | RU Translation |
| **53** | ✅ **Done** | 2026-08-27 | 2026-08-27 | a57f56b |
| **54** | ✅ **Done** | 2026-08-27 | 2026-08-27 | 36b350c |
| **55** | ✅ **Done** | 2026-08-27 | 2026-08-27 | (wizard) |
| **56** | 🚧 **In Progress** | 2026-08-27 | - | - |
| 55 | 📋 Planned | - | - | - |
| 56 | 📋 Planned | - | - | - |
| 57 | 📋 Planned | - | - | - |
| 58 | 📋 Planned | - | - | - |
| 59 | 📋 Planned | - | - | - |

---

## 🔥 Current Focus

**Sprint 54 — Formatter Layer**

Это самый важный архитектурный рефакторинг Phase 3. Без него:
- ❌ Нельзя добавить новый тип контента без нового job
- ❌ Wizard не сможет создавать каналы с разными форматами
- ❌ Дублирование кода в publish_job-ах

После Sprint 54:
- ✅ Формат определяется \channel_profile\
- ✅ Новые типы контента = новые formatter-ы
- ✅ Основа для Sprint 55 (Wizard) готова

---

## 🚫 Freeze List (не трогаем до Phase 4)

- ❌ Video Manager (Runway ML, Sora)
- ❌ Dzen Publisher
- ❌ YouTube
- ❌ Новые manga/anime/news источники
- ❌ Image generation (DALL-E, Stable Diffusion)
- ❌ Voice generation
- ❌ Сложный A/B testing
- ❌ Дополнительные enrichment-механизмы

**Почему?** Потому что они **не являются узким местом сейчас**. Узкое место = **productization** (Wizard, One-Click START, Dashboard).

---

## 📚 Documentation

- \status.md\ — detailed project status
- \ARCHITECTURE.md\ — current architecture + principles
- \ROADMAP.md\ — this file
- \README.md\ — installation + usage (to be updated)
