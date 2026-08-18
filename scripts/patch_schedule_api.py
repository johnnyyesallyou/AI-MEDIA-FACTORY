import pathlib

# 1. schemas.py — добавляем схемы расписаний
sp = pathlib.Path('./backend/app/api/v1/schemas.py')
s = sp.read_text(encoding='utf-8')
if 'class ChannelScheduleRequest' not in s:
    s += '''

# === SCHEDULE SCHEMAS ===

class ChannelScheduleRequest(BaseModel):
    cron_expression: str = Field(default="0 */3 * * *")
    timezone: str = Field(default="Europe/Moscow")
    max_posts_per_day: int = Field(default=3, ge=1, le=50)
    auto_publish: bool = True
    is_active: bool = True

class ChannelScheduleResponse(BaseModel):
    id: str
    channel_id: str
    cron_expression: str
    timezone: str
    max_posts_per_day: int
    auto_publish: bool
    is_active: bool
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
'''
    sp.write_text(s, encoding='utf-8')
    print('OK schemas.py: schedule schemas added')

# 2. channels.py — импорты + эндпоинты
cp = pathlib.Path('./backend/app/api/v1/channels.py')
c = cp.read_text(encoding='utf-8')
if 'ChannelScheduleRequest' not in c:
    c = c.replace(
        '    KnowledgeSourceResponse\n)',
        '    KnowledgeSourceResponse,\n    ChannelScheduleRequest,\n    ChannelScheduleResponse\n)'
    )
    c = c.replace(
        'from core.repositories.channel_repository import ChannelRepository',
        'from core.repositories.channel_repository import ChannelRepository\nfrom backend.automation.scheduler import automation_scheduler'
    )
    c += '''

# === SCHEDULE ENDPOINTS ===

def _schedule_to_response(s: ChannelScheduleORM) -> ChannelScheduleResponse:
    return ChannelScheduleResponse(
        id=s.id,
        channel_id=s.channel_id,
        cron_expression=s.cron_expression,
        timezone=s.timezone,
        max_posts_per_day=s.max_posts_per_day,
        auto_publish=s.auto_publish,
        is_active=s.is_active,
        last_run=s.last_run,
        next_run=s.next_run,
    )


@router.get("/{channel_id}/schedule", response_model=ChannelScheduleResponse)
async def get_channel_schedule(channel_id: str, db: Session = Depends(get_db)):
    schedule = (
        db.query(ChannelScheduleORM)
        .filter(ChannelScheduleORM.channel_id == channel_id)
        .first()
    )
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return _schedule_to_response(schedule)


@router.put("/{channel_id}/schedule", response_model=ChannelScheduleResponse)
async def upsert_channel_schedule(channel_id: str, request: ChannelScheduleRequest, db: Session = Depends(get_db)):
    channel = db.query(ChannelORM).filter(ChannelORM.id == channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    # Валидация cron ДО сохранения в БД
    try:
        from apscheduler.triggers.cron import CronTrigger
        from pytz import timezone as pytz_timezone
        CronTrigger.from_crontab(request.cron_expression, timezone=pytz_timezone(request.timezone))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid cron: {e}")

    schedule = (
        db.query(ChannelScheduleORM)
        .filter(ChannelScheduleORM.channel_id == channel_id)
        .first()
    )
    if not schedule:
        schedule = ChannelScheduleORM(channel_id=channel_id)
        db.add(schedule)

    schedule.cron_expression = request.cron_expression
    schedule.timezone = request.timezone
    schedule.max_posts_per_day = request.max_posts_per_day
    schedule.auto_publish = request.auto_publish
    schedule.is_active = request.is_active
    db.commit()
    db.refresh(schedule)

    # Планировщик подхватывает изменения БЕЗ перезапуска backend
    await automation_scheduler.refresh_schedule(channel_id)

    return _schedule_to_response(schedule)
'''
    cp.write_text(c, encoding='utf-8')
    print('OK channels.py: schedule endpoints added')