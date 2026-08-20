import pathlib, re

p = pathlib.Path('/app/backend/app/api/v1/channels.py')
c = p.read_text(encoding='utf-8')

# Проверяем есть ли endpoints templates
if 'list_channel_templates' in c:
    print('[i] Endpoints уже есть')
else:
    # Добавляем импорт KnowledgeSource если нет
    if 'from core.models.channel import KnowledgeSource' not in c:
        c = c.replace(
            'from core.models.channel_orm import ChannelORM',
            'from core.models.channel_orm import ChannelORM\nfrom core.models.channel import KnowledgeSource, SourceType'
        )
        print('[+] Добавлен импорт KnowledgeSource')
    
    # Добавляем endpoints
    endpoints = '''

# === CHANNEL TEMPLATES ENDPOINTS (Sprint 46.2) ===

@router.get("/templates")
async def list_channel_templates():
    """Список доступных шаблонов каналов"""
    from core.models.channel_templates import list_templates
    return list_templates()


@router.post("/from-template", status_code=201)
async def create_channel_from_template(
    template_id: str,
    custom_name: str = None,
    db: Session = Depends(get_db)
):
    """Создать канал из шаблона (одним кликом)"""
    from core.models.channel_templates import get_template
    from core.models.channel import KnowledgeSource, SourceType
    from core.models.channel_schedule_orm import ChannelScheduleORM
    
    template = get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found")
    
    # 1. Создаём канал
    channel_name = custom_name or template["name"]
    channel = ChannelORM(
        name=channel_name,
        platform=template["platform"],
        language_search=template["language_search"],
        language_publish=template["language_publish"],
        style_profile=template["style_profile"],
        timezone=template["timezone"],
        description=template.get("description"),
        is_active=True,
    )
    db.add(channel)
    db.flush()
    
    # 2. Добавляем источники
    for src in template["sources"]:
        source = KnowledgeSource(
            channel_id=channel.id,
            name=src["name"],
            source_type=src["source_type"],
            url=src["url"],
            priority=src.get("priority", 3),
            is_active=True,
        )
        db.add(source)
    
    # 3. Создаём schedule
    sched = template["schedule"]
    schedule = ChannelScheduleORM(
        channel_id=channel.id,
        cron_expression=sched["cron_expression"],
        timezone=sched.get("timezone", "UTC"),
        max_posts_per_day=sched.get("max_posts_per_day", 3),
        auto_publish=sched.get("auto_publish", True),
        is_active=sched.get("is_active", True),
    )
    db.add(schedule)
    
    db.commit()
    db.refresh(channel)
    
    return {
        "id": channel.id,
        "name": channel.name,
        "platform": channel.platform,
        "language_search": channel.language_search,
        "language_publish": channel.language_publish,
        "style_profile": channel.style_profile,
        "timezone": channel.timezone,
        "description": channel.description,
        "is_active": channel.is_active,
    }
'''
    
    c += endpoints
    p.write_text(c, encoding='utf-8')
    print('[+] Endpoints добавлены')