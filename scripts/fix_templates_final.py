import pathlib, re

p = pathlib.Path('/app/backend/app/api/v1/channels.py')
c = p.read_text(encoding='utf-8')

# 1. Удаляем битые endpoints из конца файла
marker = "# === CHANNEL TEMPLATES ENDPOINTS"
idx = c.find(marker)
if idx != -1:
    c = c[:idx].rstrip() + "\n"
    print("[1] Удалены битые endpoints из конца файла")
else:
    print("[1] Marker не найден, пропускаем")

# 2. Вставляем правильные endpoints ПОСЛЕ "GET /" (строка 77) и ПЕРЕД "/{channel_id}"
templates_block = '''

# === CHANNEL TEMPLATES (Sprint 46.2) ===
# ВАЖНО: эти endpoints ДОЛЖНЫ быть ПЕРЕД /{channel_id}, иначе FastAPI матчит "templates" как channel_id

@router.get("/templates")
async def list_channel_templates():
    """Список доступных шаблонов каналов (news/anime/manga)"""
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
    
    template = get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found")
    
    repo = ChannelRepository(db)
    
    # 1. Создаём канал
    channel_name = custom_name or template["name"]
    create_req = ChannelCreateRequest(
        name=channel_name,
        platform=template["platform"],
        language_search=template["language_search"],
        language_publish=template["language_publish"],
        style_profile=template["style_profile"],
        timezone=template["timezone"],
        description=template.get("description"),
    )
    
    # Используем существующий POST /channels/ endpoint логику
    channel = ChannelORM(
        id=str(uuid.uuid4()),
        name=create_req.name,
        platform=create_req.platform,
        language_search=create_req.language_search,
        language_publish=create_req.language_publish,
        style_profile=create_req.style_profile,
        timezone=create_req.timezone,
        description=create_req.description,
        is_active=True,
        template_id=template_id,
        sources=[],
    )
    db.add(channel)
    db.flush()
    
    # 2. Добавляем источники через repo.add_source (JSON field)
    for src in template["sources"]:
        source_dict = {
            "id": str(uuid.uuid4()),
            "name": src["name"],
            "source_type": src["source_type"],
            "url": src["url"],
            "priority": src.get("priority", 3),
            "is_active": True,
        }
        repo.add_source(channel.id, source_dict)
    
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
    
    return ChannelResponse(
        id=channel.id,
        name=channel.name,
        platform=channel.platform,
        language_search=channel.language_search,
        language_publish=channel.language_publish,
        style_profile=channel.style_profile,
        timezone=channel.timezone,
        description=channel.description,
        is_active=channel.is_active,
        created_at=channel.created_at,
        updated_at=channel.updated_at,
    )

'''

# Вставляем ПОСЛЕ строки с @router.get("/") и ПЕРЕД @router.get("/{channel_id}")
target = '@router.get("/{channel_id}", response_model=ChannelResponse)'
idx2 = c.find(target)
if idx2 != -1:
    c = c[:idx2] + templates_block + "\n\n" + c[idx2:]
    p.write_text(c, encoding='utf-8')
    print("[2] Endpoints templates вставлены ПЕРЕД /{channel_id}")
else:
    print("[FAIL] Не удалось найти точку вставки")