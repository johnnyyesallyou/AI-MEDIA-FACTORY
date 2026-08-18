import re

file_path = '/app/backend/automation/jobs/automation_jobs.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Добавляем импорты
if 'from core.models.execution_log_orm import ExecutionLogORM' not in content:
    content = content.replace(
        'from engines.research.engine import ResearchEngine',
        'from engines.research.engine import ResearchEngine\nimport time\nimport uuid\nfrom core.models.execution_log_orm import ExecutionLogORM'
    )

# 2. Добавляем класс PipelineLogger перед ResearchJob
logger_class = '''
class PipelineLogger:
    def __init__(self, execution_id: str, channel_id: str = None):
        self.execution_id = execution_id or str(uuid.uuid4())
        self.channel_id = channel_id
        self.db = SessionLocal()
        self.start_time = None
        self.log_id = None

    def start(self, stage: str, headline: str = None):
        self.start_time = time.time()
        log = ExecutionLogORM(
            execution_id=self.execution_id,
            channel_id=self.channel_id,
            stage=stage,
            status='started',
            headline=headline
        )
        self.db.add(log)
        self.db.commit()
        self.log_id = log.id

    def finish(self, status: str, details: str = None, error_message: str = None):
        if not self.log_id: return
        duration_ms = int((time.time() - self.start_time) * 1000) if self.start_time else 0
        log = self.db.query(ExecutionLogORM).filter(ExecutionLogORM.id == self.log_id).first()
        if log:
            log.status = status
            log.completed_at = datetime.utcnow()
            log.duration_ms = duration_ms
            log.details = details
            log.error_message = error_message
            self.db.commit()
        self.db.close()

'''
if 'class PipelineLogger:' not in content:
    content = content.replace('class ResearchJob:', logger_class + 'class ResearchJob:')

# 3. Обновляем сигнатуру и начало ResearchJob.run
old_run = '''class ResearchJob:

    def run(self, channel=None) -> dict[str, Any]:

        logger.info(
            "ResearchJob started channel=%s",
            getattr(channel, "name", None)
        )

        db = SessionLocal()'''

new_run = '''class ResearchJob:

    def run(self, channel=None, execution_id: str = None) -> dict[str, Any]:
        p_logger = PipelineLogger(execution_id, channel.id if channel else None)
        p_logger.start("research")

        logger.info(
            "ResearchJob started channel=%s",
            getattr(channel, "name", None)
        )

        db = SessionLocal()'''

content = content.replace(old_run, new_run)

# 4. Находим конец ResearchJob и добавляем finish
content = content.replace(
    'skipped = 0\n\n',
    'skipped = 0\n        p_logger.finish("success", details=f"Created {created}, skipped {skipped}")\n\n'
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ ResearchJob успешно обновлен с логированием!')
