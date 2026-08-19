import pathlib, py_compile

# 1. Добавляем VkConnectionRequest в schemas.py
schemas_file = pathlib.Path('./backend/app/api/v1/schemas.py')
s = schemas_file.read_text(encoding='utf-8')

if 'class VkConnectionRequest' not in s:
    vk_schema = '''

class VkConnectionRequest(BaseModel):
    \'\'\'Схема для подключения VK группы.\'\'\'
    group_id: str = Field(description="ID группы VK (например: -123456789 или my_group)")
    access_token: str = Field(description="Access token с правами wall, groups")


class YoutubeConnectionRequest(BaseModel):
    \'\'\'Схема для подключения YouTube канала.\'\'\'
    channel_id: str = Field(description="ID YouTube канала")
    api_key: str = Field(description="YouTube Data API v3 key")


class DzenConnectionRequest(BaseModel):
    \'\'\'Схема для подключения Дзен канала.\'\'\'
    channel_id: str = Field(description="ID Дзен канала")
    api_key: str = Field(description="Дзен API key")
'''
    # Вставляем после TelegramConnectionRequest
    s = s.replace(
        'class KnowledgeSourceCreateRequest(BaseModel):',
        vk_schema + '\n\nclass KnowledgeSourceCreateRequest(BaseModel):',
        1
    )
    schemas_file.write_text(s, encoding='utf-8')
    print("✅ Добавлены VkConnectionRequest, YoutubeConnectionRequest, DzenConnectionRequest")

# 2. Добавляем endpoints connect-vk, connect-youtube, connect-dzen в channels.py
channels_file = pathlib.Path('./backend/app/api/v1/channels.py')
c = channels_file.read_text(encoding='utf-8')

# Импортируем новые schemas
if 'VkConnectionRequest' not in c:
    c = c.replace(
        'TelegramConnectionRequest',
        'TelegramConnectionRequest, VkConnectionRequest, YoutubeConnectionRequest, DzenConnectionRequest',
        1
    )
    print("✅ Добавлены импорты VkConnectionRequest, YoutubeConnectionRequest, DzenConnectionRequest")

# Добавляем endpoint connect-vk после connect-telegram
if '@router.post("/{channel_id}/connect-vk"' not in c:
    vk_endpoint = '''

@router.post("/{channel_id}/connect-vk", response_model=ChannelResponse)
async def connect_vk(channel_id: str, request: VkConnectionRequest, db: Session = Depends(get_db)):
    """
    Sprint 11: Подключает VK группу к каналу.
    
    Сохраняет group_id и access_token в БД.
    Валидация токена будет добавлена в VkPublisher.
    """
    repo = ChannelRepository(db)
    channel = repo.get(channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    channel.vk_group_id = request.group_id
    channel.vk_access_token = request.access_token
    channel.is_connected = True
    db.commit()
    db.refresh(channel)
    
    logger.info("VK connected for channel %s: group_id=%s", channel_id, request.group_id)
    return _to_response(channel)


@router.post("/{channel_id}/connect-youtube", response_model=ChannelResponse)
async def connect_youtube(channel_id: str, request: YoutubeConnectionRequest, db: Session = Depends(get_db)):
    """Sprint 11: Подключает YouTube канал."""
    repo = ChannelRepository(db)
    channel = repo.get(channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    channel.youtube_channel_id = request.channel_id
    channel.youtube_api_key = request.api_key
    channel.is_connected = True
    db.commit()
    db.refresh(channel)
    
    logger.info("YouTube connected for channel %s", channel_id)
    return _to_response(channel)


@router.post("/{channel_id}/connect-dzen", response_model=ChannelResponse)
async def connect_dzen(channel_id: str, request: DzenConnectionRequest, db: Session = Depends(get_db)):
    """Sprint 11: Подключает Дзен канал."""
    repo = ChannelRepository(db)
    channel = repo.get(channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    channel.dzen_channel_id = request.channel_id
    channel.dzen_api_key = request.api_key
    channel.is_connected = True
    db.commit()
    db.refresh(channel)
    
    logger.info("Dzen connected for channel %s", channel_id)
    return _to_response(channel)

'''
    # Вставляем перед @router.post("/{channel_id}/sources"
    c = c.replace(
        '@router.post("/{channel_id}/sources",',
        vk_endpoint + '@router.post("/{channel_id}/sources",',
        1
    )
    channels_file.write_text(c, encoding='utf-8')
    print("✅ Добавлены endpoints: connect-vk, connect-youtube, connect-dzen")

# Проверяем синтаксис
for f in [schemas_file, channels_file]:
    try:
        py_compile.compile(str(f), doraise=True)
        print(f"✅ {f.name} валиден")
    except py_compile.PyCompileError as e:
        print(f"❌ {f.name}: {e}")