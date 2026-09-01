"""
Sprint 66.5.5: Worker Integration Guide

Как интегрировать ErrorLogger в существующие automation jobs.
"""

# ============================================================================
# КРАТКАЯ ИНСТРУКЦИЯ ПО ИНТЕГРАЦИИ
# ============================================================================

# Шаг 1: Импортировать JobErrorHandler
# ============================================================================
"""
from backend.automation.job_error_handler import JobErrorHandler, handle_job_errors
"""

# Шаг 2: Обернуть job код в контекстный менеджер
# ============================================================================
"""
БЫЛО:
def run(self, channel: ChannelORM) -> Dict:
    try:
        result = fetch_data()
        return {"status": "ok", "data": result}
    except Exception as e:
        logger.exception(f"Job failed: {e}")
        return {"status": "failed", "error": str(e)}

СТАЛО:
def run(self, channel: ChannelORM, execution_id: str = None) -> Dict:
    with JobErrorHandler(
        channel_id=channel.id,
        pipeline="research",  # или generation, media, publishing, learning
        job="fetch_data",     # Название конкретной работы
        execution_id=execution_id,
    ) as ctx:
        try:
            result = fetch_data()
            return {"status": "ok", "data": result}
        except Exception as e:
            # Ошибка автоматически залогируется при выходе из контекста
            logger.exception(f"Job failed: {e}")
            return {"status": "failed", "error": str(e), "execution_id": ctx.execution_id}
"""

# Шаг 3: Как указать execution_id при вызове
# ============================================================================
"""
job = MangaResearchJob()
result = job.run(
    channel=channel,
    execution_id="exec-12345"  # Передавать для трассировки
)
"""

# ============================================================================
# ПОЛНЫЙ ПРИМЕР ИНТЕГРАЦИИ
# ============================================================================

"""
# File: backend/automation/jobs/manga_research_job.py

import logging
from backend.automation.job_error_handler import JobErrorHandler

logger = logging.getLogger(__name__)

class MangaResearchJob:
    def run(self, channel, limit_per_source=20, execution_id=None):
        '''With error tracking'''
        with JobErrorHandler(
            channel_id=channel.id,
            pipeline="research",
            job="fetch_manga_sources",
            execution_id=execution_id,
        ) as ctx:
            db = SessionLocal()
            
            try:
                # ... existing logic ...
                
                # На каждую подошибку:
                try:
                    result = self.knowledge.process_items(db, all_items)
                except Exception as e:
                    ctx.log_error(e, context={"data": "process_items"})
                    raise
                
                # ... more logic ...
                
                db.commit()
                return {"status": "ok", "items": len(items), "execution_id": ctx.execution_id}
                
            except Exception as e:
                db.rollback()
                # Ошибка уже залогирована в __exit__
                return {"status": "failed", "error": str(e), "execution_id": ctx.execution_id}
            finally:
                db.close()
"""

# ============================================================================
# ВАРИАНТЫ ИНТЕГРАЦИИ
# ============================================================================

# Вариант 1: Минимальная интеграция (контекстный менеджер)
# ============================================================================
"""
def run(self, channel, execution_id=None):
    with JobErrorHandler(channel.id, "research", "job_name", execution_id) as ctx:
        result = do_work()
        return {"status": "ok", "result": result, "execution_id": ctx.execution_id}
"""

# Вариант 2: С детальным логированием отдельных операций
# ============================================================================
"""
def run(self, channel, execution_id=None):
    with JobErrorHandler(channel.id, "research", "job_name", execution_id) as ctx:
        try:
            data = fetch_data()
        except TimeoutError:
            ctx.log_timeout(30.0)
            raise
        except RateLimitError as e:
            ctx.log_rate_limit("pixabay", retry_after=60)
            raise
        except Exception as e:
            ctx.log_error(e)
            raise
        
        return {"status": "ok", "data": data}
"""

# Вариант 3: С использованием декоратора (для простых функций)
# ============================================================================
"""
from backend.automation.job_error_handler import handle_job_errors

class MyJob:
    @handle_job_errors(pipeline="research", job="fetch_items", timeout_seconds=30)
    async def fetch(self, channel_id: str) -> Dict:
        items = await fetch_all()
        return {"items": items}

# Вызов:
job = MyJob()
result = await job.fetch("ch-123", execution_id="exec-456")
"""

# ============================================================================
# СПИСОК JOBS ДЛЯ ИНТЕГРАЦИИ (Priority)
# ============================================================================

"""
RESEARCH PIPELINE (High Priority):
  [ ] manga_research_job.py
  [ ] anime_research_job.py
  [ ] news_research_job.py

GENERATION PIPELINE (High Priority):
  [ ] manga_pipeline_job.py (содержит генерацию)
  [ ] anime_pipeline_job.py
  [ ] news_pipeline_job.py

MEDIA PIPELINE (Medium Priority):
  [ ] image_job.py
  [ ] smart_image_acquisition_job.py

PUBLISHING PIPELINE (High Priority):
  [ ] manga_publish_job.py
  [ ] anime_publish_job.py
  [ ] news_publish_job.py

ENGAGEMENT & MONITORING (Low Priority):
  [ ] engagement_collection_job.py
  [ ] monitoring_job.py
"""

# ============================================================================
# ERROR TYPES И ИХ ОБРАБОТКА
# ============================================================================

"""
При перехвате исключений, используй специфичные методы:

1. TimeoutError / asyncio.TimeoutError:
   ctx.log_timeout(timeout_seconds)

2. RateLimitError / 429 ошибки:
   ctx.log_rate_limit(service="pixabay", retry_after=60)

3. ConnectionError / NetworkError:
   ctx.log_error(e) # Автоматически классифицируется как network

4. Другие исключения:
   ctx.log_error(e) # Автоматически классифицируется по типу

Автоматическая классификация:
  timeout / TimeoutError → ErrorType.TIMEOUT
  rate_limit / 429 → ErrorType.RATE_LIMIT
  connection / network → ErrorType.NETWORK
  validation / invalid → ErrorType.VALIDATION
  llm / generation → ErrorType.LLM_ERROR
  media / image / video → ErrorType.MEDIA_ERROR
  publish / telegram / vk → ErrorType.PUBLISH_ERROR
  exception → ErrorType.EXCEPTION
  остальное → ErrorType.UNKNOWN
"""

# ============================================================================
# QUERY FAILURES ЧЕРЕЗ API
# ============================================================================

"""
После интеграции, получить ошибки:

# Все failures для канала
GET /api/v1/channels/{channel_id}/failures

# Failures определённого типа
GET /api/v1/failures?channel_id={ch_id}&error_type=timeout

# Статистика
GET /api/v1/channels/{channel_id}/stats

# Dashboard
GET /api/v1/failures/dashboard/summary

# Отметить как resolved
POST /api/v1/failures/{failure_id}/resolve
{\"resolution\": \"success\" or \"manual_fix\"}
"""

# ============================================================================
# ТЕСТИРОВАНИЕ ИНТЕГРАЦИИ
# ============================================================================

"""
Как убедиться что error logging работает:

1. Вызвать job с известной ошибкой:
   job.run(channel, execution_id="test-123")

2. Проверить API:
   curl http://localhost:8000/api/v1/failures?execution_id=test-123

3. Должен вернуться список failures с:
   - execution_id: "test-123"
   - channel_id: "<channel_id>"
   - error_type: "<type>"
   - error_message: "<message>"
   - resolved: false
"""

# ============================================================================
# RETRY LOGIC (для будущей реализации)
# ============================================================================

"""
После того как ErrorLogger интегрирован, можно добавить retry logic:

def retry_failed_jobs():
    '''Повторно запустить retryable ошибки'''
    failures = db.query(PipelineFailure).filter(
        PipelineFailure.resolved == False,
        PipelineFailure.retry_at <= datetime.utcnow(),
    ).all()
    
    for failure in failures:
        # Найти job и переиспользовать
        job = get_job_by_name(failure.job)
        channel = db.query(ChannelORM).get(failure.channel_id)
        
        # Повторить с увеличенным attempt
        result = job.run(channel, execution_id=failure.execution_id)
        
        if result['status'] == 'ok':
            failure.mark_resolved('retry_success')
        else:
            failure.attempt += 1
            if failure.is_retryable():
                failure.retry_at = datetime.utcnow() + timedelta(minutes=5)
        
        db.commit()
"""

# ============================================================================
# MONITORING & ALERTS
# ============================================================================

"""
После интеграции, можно мониторить:

1. Error Rate по типам:
   - timeout errors за день
   - rate_limit errors за день
   - llm_error rate
   - publish_error rate

2. Channel Health:
   - которые каналы падают?
   - какие jobs падают?
   - паттерны ошибок?

3. System Health:
   - общее количество failures
   - % резолвленных ошибок
   - средний retry count

Пример мониторинга:
   stats = requests.get("http://api/v1/failures/dashboard/summary").json()
   if stats['total_unresolved'] > 50:
       alert("Too many unresolved failures!")
"""

print(__doc__)
