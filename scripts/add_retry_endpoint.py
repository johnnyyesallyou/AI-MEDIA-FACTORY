import pathlib

p = pathlib.Path('./backend/app/api/v1/automation.py')
s = p.read_text(encoding='utf-8')

# Добавляем нужные импорты
imports_to_add = [
    ('from backend.automation.runner import AutomationRunner', 'from backend.automation.runner import AutomationRunner'),
    ('from core.database import get_db', 'from core.database import get_db, SessionLocal'),
    ('from core.repositories.channel_repository import ChannelRepository', 'from core.repositories.channel_repository import ChannelRepository'),
    ('from fastapi import Depends, HTTPException', 'from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException'),
]

for imp in imports_to_add:
    if imp[0] not in s:
        # Находим первый импорт и вставляем после него
        first_import = s.split('\n')[0] if 'import' in s.split('\n')[0] else 'import uuid'
        s = s.replace(first_import, first_import + '\n' + imp[1], 1)

# Добавляем эндпоинт retry в конец файла
retry_endpoint = '''

# === RETRY STAGE ===

class RetryRequest(BaseModel):
    execution_id: str
    stage: str

class RetryResponse(BaseModel):
    status: str
    new_execution_id: str
    stage: str
    message: str

VALID_STAGES = ["research", "decision", "writing", "evaluation", "revision", "re_evaluation", "publish"]

@router.post("/retry", response_model=RetryResponse)
async def retry_stage(request: RetryRequest, background_tasks: BackgroundTasks):
    """Повторяет один конкретный этап пайплайна для канала из исходного запуска."""
    if request.stage not in VALID_STAGES:
        raise HTTPException(status_code=400, detail=f"Invalid stage. Valid: {VALID_STAGES}")

    # Находим channel_id из исходного execution_id
    db = SessionLocal()
    try:
        log = db.query(ExecutionLogORM).filter(
            ExecutionLogORM.execution_id == request.execution_id
        ).first()

        if not log:
            raise HTTPException(status_code=404, detail="Execution not found")

        channel_id = log.channel_id
        channel = None
        if channel_id:
            repo = ChannelRepository(db)
            channel = repo.get(channel_id)
    finally:
        db.close()

    new_execution_id = f"retry-{request.execution_id}-{request.stage}"

    async def _do_retry():
        runner = AutomationRunner()
        await runner.retry_stage(channel, request.stage, new_execution_id)

    background_tasks.add_task(_do_retry)

    return RetryResponse(
        status="started",
        new_execution_id=new_execution_id,
        stage=request.stage,
        message=f"Retrying stage '{request.stage}' for execution {request.execution_id}"
    )
'''

# Нужно добавить импорт ExecutionLogORM
if 'from core.models.execution_log_orm import ExecutionLogORM' not in s:
    s = s.replace('from backend.automation.scheduler import automation_scheduler',
                  'from backend.automation.scheduler import automation_scheduler\nfrom core.models.execution_log_orm import ExecutionLogORM')
    print('OK: ExecutionLogORM import added')

if '/retry' not in s:
    s = s + retry_endpoint
    p.write_text(s, encoding='utf-8')
    print('OK: /retry endpoint added')
else:
    print('endpoint already exists')