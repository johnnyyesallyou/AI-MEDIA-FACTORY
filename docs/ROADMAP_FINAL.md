# AI Media Factory — FINAL ROADMAP (canonical)

**Статус:** единый канон планирования. ЭТОТ файл — источник истины для последовательности спринтов
и гейтов готовности. ROADMAP.md остаётся кратким обзором фаз со ссылкой сюда. STATUS.md / AI_CONTEXT.md
отражают текущую точку на этом пути.

**Дата фиксации:** 2026-09-11. **Текущая точка:** после Sprint 76.2 (Smart Source Selection), готовится
Sprint 76.3 — Verification & Integration Gate.

---

## 0. Принцип, который нельзя нарушать

Уровни готовности — НЕ «бонус», а **обязательный Definition of Done** для каждого блока:

```
Implementation      — код существует
      ↓
Integration         — подключён к Universal Pipeline (реально вызывается из цепочки, а не только из API)
      ↓
Reliability         — покрыт тестами + обработкой отказов (fallback, изоляция, идемпотентность)
      ↓
Production validation — проверен на реальных каналах и длительной работе
```

**Правило фиксации факта:** нельзя писать в STATUS «сделано», если блок не прошёл уровень Integration
в общей цепочке. «Модуль имеет API» ≠ «модуль влияет на поведение pipeline».

**Проверенные текущие пробелы (по коду, 2026-09-11):**
- `SmartSourceSelector` (76.2) вызывается ТОЛЬКО из `sources.py` (API) и тестов;
  `ResearchJob` берёт источники из `profile_cfg["sources"]` и НЕ использует selector
  → 76.1/76.2 сейчас на уровне «Implementation + API», НЕ Integration.
- Нет E2E-теста `Profile → Source Selection → Research`.
- Два Sprint 60 теста = **skipped** (`requires_llm`), не исправлены/не xfail
  → регресс читается как «194 passed, 2 skipped, 2 legacy unresolved».

Вывод: **Sprint 76.3 — Verification & Integration Gate** обязателен ДО любого нового функционала.

---

## 1. Целевая архитектура

```
Channel
  └─ Channel Profile (единый runtime config source)
       └─ Universal Pipeline
            ├─ Source Discovery (76.x)
            ├─ Smart Source Selection (76.x)
            ├─ Research
            ├─ Decision
            ├─ Brief
            ├─ Writing
            ├─ Evaluation
            ├─ Revision
            ├─ Image / Media
            ├─ Publishing
            ├─ Analytics
            └─ Learning Loop
```

- **Channel Profile — единственный** источник runtime-конфигурации (сделано в 75.x).
- **Platform-специфика — только в Platform Adapter** (78.2), не в ядре pipeline.

---

## 2. Этап 0 — закрытие текущего состояния (ОТКРЫТО)

### 2.A Sprint 76.3 — Verification & Integration Gate (НЕ новый функционал)

Цель — закрыть разрыв «код есть, но не влияет на поведение»:

1. **Wiring Smart Source Selection в ResearchJob** цепочка:
   `ResearchJob → Channel Profile → SmartSourceSelector.select(content_type, topic, language, freshness) → Selected Sources → ResearchEngine.run(sources_override=...)`.
   - topic/language/freshness берутся из `load_profile_config`.
   - Fallback: ошибка/пустой результат selector → прежний `profile_cfg["sources"]` → статический реестр.
   - Убедиться, что старый механизм не обходится параллельно.

2. **E2E-тесты (обязательно):**
   - `Profile → Selection → Research` (выбор источника меняет собранные темы).
   - `Profile → Writing → Evaluation` (подтвердить актуальность 75.2).
   - Isolation двух каналов (подтвердить 75.3).
   - Fallback-тесты: selector пуст/падает; rotation не вытесняет единственный качественный
     источник; diversity не выбирает нерелевантное.

3. **Решить Sprint 60:** зафиксировать статус (skipped; legacy unresolved) в доках;
   регресс-строка сигнализирует «194 passed, 2 skipped, 2 legacy unresolved».

**DoD этапа:** E2E `Profile→Selection→Research` зелёный; fallback-тесты зелёные;
рабочий tree чистый; всё запушено; STATUS/AI_CONTEXT синхронизированы.
**Без DoD этап НЕ считается закрытым.**