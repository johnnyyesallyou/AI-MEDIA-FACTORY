# Sprint 76.V — Verification Gate

**Дата начала:** 2026-09-11  
**Статус:** IN PROGRESS  
**Цель:** Подтвердить, что Sprint 75.1–76.2 не просто существуют в коде, а реально подключены к рабочему pipeline

---

## Критерий успеха

> Нельзя начинать Sprint 76.3 (Subscribe.ru integration) без доказательства, что 76.1–76.2 действительно работают в unified pipeline

---

## Чек-лист проверок

### 1. Profile Enforcement в Jobs

**ResearchJob должен использовать профиль канала**

- [ ] `ResearchJob` получает Channel Profile
- [ ] `ResearchJob` использует `load_profile_config()`
- [ ] Язык из профиля передаётся в RSS fetcher
- [ ] Freshness policy из профиля применяется
- [ ] Источники из профиля используются
- [ ] Разные профили дают разные результаты Research

**Тест:** Запустить два канала с разными профилями, проверить что Research выбирает разные источники

**Где проверять:** `backend/automation/jobs/research_job.py`

---

### 2. WritingJob Profile Enforcement

- [ ] `WritingJob` получает Channel Profile
- [ ] `WritingJob` использует `load_profile_config()`
- [ ] `target_style` из профиля используется
- [ ] Длина из профиля влияет на результат
- [ ] Аудитория из профиля влияет на tone
- [ ] Разные профили дают разные тексты на одних и тех же темах

**Тест:** Запустить одну тему через два профиля, сравнить выходной текст

**Где проверять:** `backend/automation/jobs/writing_job.py` → `load_profile_config()` использование

---

### 3. EvaluationJob Profile Enforcement

- [ ] `EvaluationJob` получает Channel Profile
- [ ] `evaluation_criteria` из профиля используются
- [ ] Quality thresholds разные по профилям
- [ ] Ошибки FactGuard применяются согласно профилю

**Тест:** Проверить что эвалюатор применяет разные критерии для разных профилей

**Где проверять:** `backend/automation/jobs/evaluation_job.py`

---

### 4. Cross-channel Isolation

**Контент одного канала не должен смешиваться с другим**

- [ ] `list_all()` вызовы фильтруют по `channel_id`
- [ ] WritingJob обрабатывает только контент ЕГО канала
- [ ] EvaluationJob обрабатывает только контент ЕГО канала
- [ ] ImageJob обрабатывает только контент ЕГО канала
- [ ] PublishJob обрабатывает только контент ЕГО канала
- [ ] RevisionJob обрабатывает только контент ЕГО канала
- [ ] Credentials одного канала не используются другим
- [ ] Rate limits независимы
- [ ] Pause одного канала не влияет на другие

**Тест:** Создать контент в канале A и канале B, убедиться что jobs обрабатывают только свой контент

**Где проверять:** 
- `backend/automation/jobs/*.py` - проверить `channel_id` фильтры
- `tests/test_profile_ab_behavior.py` - integration тесты

---

### 5. Source Selection Integration

**SmartSourceSelector должен реально использоваться в ResearchJob**

- [ ] `ResearchJob` вызывает `SmartSourceSelector.select()`
- [ ] `topic` передаётся из Channel Profile
- [ ] `language` учитывается в selector
- [ ] `freshness` учитывается в selector
- [ ] `quality_score` влияет на выбор
- [ ] `rotation` работает (не один и тот же источник каждый раз)
- [ ] `diversity` работает
- [ ] Fallback на известные источники работает при ошибке selector

**Тест:** Запустить ResearchJob несколько раз, проверить что выбираются разные источники (rotation)

**Где проверять:** `backend/engines/source_selection.py` + `backend/automation/jobs/research_job.py`

---

### 6. QualityRegistry Behavior

- [ ] Quality метрики сохраняются в памяти
- [ ] Неудачные источники штрафуются в score
- [ ] Успешные источники повышаются в приоритете
- [ ] Rotation предотвращает усталость от одного источника
- [ ] Нет жёсткого заклинивания на одном источнике

**Тест:** Запустить несколько прогонов, проверить что quality метрики накапливаются

**Где проверять:** `backend/core/quality_registry.py` + `backend/engines/source_selection.py`

---

### 7. Sprint 60 Tests Status

**Два тета в наследстве от Sprint 60 должны быть документированы**

- [ ] `test_generate_news_post` — статус известен и задокументирован
- [ ] `test_generate_manga_post_no_video` — статус известен и задокументирован
- [ ] Оба теста либо skipped с причиной, либо isxfail, либо исправлены

**Где проверять:** `tests/test_*.py` - найти эти тесты и проверить маркеры

---

## Тестовый план

### Test 1: Profile Enforcement Integration Test

```python
def test_profile_enforcement_research_writing():
    """Проверить что профиль влияет на Research и Writing"""
    
    # Создать два канала с разными профилями
    analytical = create_channel(profile="Analytical Deep Dive")  # 2500 chars
    casual = create_channel(profile="Casual Manga Buzz")        # 800 chars
    
    # Запустить Research для обоих
    analytical_research = run_research(analytical)
    casual_research = run_research(casual)
    
    # Запустить Writing для обоих на одной теме
    analytical_draft = run_writing(analytical, topic)
    casual_draft = run_writing(casual, topic)
    
    # Проверить различия
    assert len(analytical_draft.text) > len(casual_draft.text)
    assert analytical_draft.text != casual_draft.text
```

### Test 2: Cross-Channel Isolation Test

```python
def test_cross_channel_isolation():
    """Проверить что контент не смешивается между каналами"""
    
    # Создать два канала
    channel_a = create_channel(name="Channel A")
    channel_b = create_channel(name="Channel B")
    
    # Создать контент для каждого в draft
    content_a = create_content(channel_a)
    content_b = create_content(channel_b)
    
    # Запустить WritingJob для A
    write_job_a(channel_a)
    
    # Проверить что job обработал только content_a
    assert get_job_results(channel_a) == [content_a.id]
    assert get_job_results(channel_b) == []
```

### Test 3: Source Selection Integration Test

```python
def test_source_selection_in_research():
    """Проверить что SmartSourceSelector используется в ResearchJob"""
    
    channel = create_channel()
    
    # Запустить несколько Research прогонов
    results_1 = run_research(channel)
    results_2 = run_research(channel)
    results_3 = run_research(channel)
    
    # Проверить что источники разнообразны (rotation работает)
    sources_1 = [r['source'] for r in results_1]
    sources_2 = [r['source'] for r in results_2]
    sources_3 = [r['source'] for r in results_3]
    
    # Не все одинаковые (ротация работает)
    assert sources_1 != sources_2 or sources_2 != sources_3
```

---

## Как запустить проверки

### Вариант 1: Manual Testing через API

```bash
# Запустить Research для канала
curl -X POST http://localhost:8000/api/v1/automation-v2/channels/{channel_id}/research

# Запустить Writing
curl -X POST http://localhost:8000/api/v1/automation-v2/channels/{channel_id}/writing

# Запустить Evaluation
curl -X POST http://localhost:8000/api/v1/automation-v2/channels/{channel_id}/evaluation

# Проверить что контент правильного канала обработан
curl http://localhost:8000/api/v1/content?channel_id={channel_id}&status=draft
```

### Вариант 2: Automated Tests

```bash
# Запустить все verification-тесты
pytest tests/test_profile_enforcement.py -v

# Запустить cross-channel isolation тесты
pytest tests/test_cross_channel_isolation.py -v

# Запустить source selection интеграционные тесты
pytest tests/test_source_selection_integration.py -v

# Полный регресс
pytest tests/ -v
```

### Вариант 3: Full Pipeline Test

```bash
# Запустить полный pipeline для двух каналов
curl -X POST http://localhost:8000/api/v1/automation-v2/run-all-channels

# Проверить results в БД
sqlite3 data/amf.db "SELECT channel_id, status, COUNT(*) FROM content GROUP BY channel_id, status"
```

---

## Результаты проверок

### ✅ Подтверждено

- [ ] Profile Enforcement работает в Research/Writing/Evaluation
- [ ] Cross-channel isolation полная
- [ ] SmartSourceSelector используется в ResearchJob
- [ ] QualityRegistry накапливает метрики
- [ ] Rotation работает (разные источники выбираются)
- [ ] Sprint 60 tests задокументированы

### ❌ Найденные проблемы

(будут заполнены при тестировании)

---

## Документы для обновления после Verification Gate

- [ ] STATUS.md - добавить результаты проверок
- [ ] MASTER_ROADMAP.md - подтвердить текущий статус
- [ ] Начать Sprint 76.3 - Subscribe.ru discovery integration

---

**Статус:** ⏳ Ready for verification  
**Следующий шаг:** Запустить Test Suite и manual checks

