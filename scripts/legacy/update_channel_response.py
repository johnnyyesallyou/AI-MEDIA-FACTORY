import pathlib

f = pathlib.Path('./backend/app/api/v1/schemas.py')
s = f.read_text(encoding='utf-8')

# Старый ChannelResponse (с дубликатом bot_token)
old_response = '''class ChannelResponse(BaseModel):
    \'\'\'РџРѕР»РЅС‹Р№ РѕС‚РІРµС‚ СЃ РёРЅС„РѕСЂРјР°С†РёРµР№ Рѕ РєР°РЅР°Р»Рµ.\'\'\'
    id: str
    name: str
    platform: str
    language_search: str
    language_publish: str
    style_profile: str
    timezone: str
    workflow_id: Optional[str] = None
    description: Optional[str]
    is_connected: bool
    is_active: bool
    bot_token: Optional[str] = None
    bot_token: Optional[str] = None
    chat_id: Optional[str] = None
    sources: List[KnowledgeSource]
    created_at: datetime
    updated_at: datetime'''

# Новый ChannelResponse с полями для VK/YouTube/Dzen + фикс дубликата
new_response = '''class ChannelResponse(BaseModel):
    \'\'\'Полный ответ с информацией о канале.\'\'\'
    id: str
    name: str
    platform: str
    language_search: str
    language_publish: str
    style_profile: str
    timezone: str
    workflow_id: Optional[str] = None
    description: Optional[str]
    is_connected: bool
    is_active: bool
    # Telegram credentials
    bot_token: Optional[str] = None
    chat_id: Optional[str] = None
    # VK credentials (Sprint 11)
    vk_group_id: Optional[str] = None
    vk_access_token: Optional[str] = None
    # YouTube credentials (Sprint 11)
    youtube_channel_id: Optional[str] = None
    youtube_api_key: Optional[str] = None
    # Dzen credentials (Sprint 11)
    dzen_channel_id: Optional[str] = None
    dzen_api_key: Optional[str] = None
    # Relations
    sources: List[KnowledgeSource]
    created_at: datetime
    updated_at: datetime'''

if old_response in s:
    s = s.replace(old_response, new_response, 1)
    print("✅ ChannelResponse обновлён:")
    print("   - Убран дубликат bot_token")
    print("   - Добавлены поля vk_*, youtube_*, dzen_*")
    print("   - Исправлена кодировка docstring")
    f.write_text(s, encoding='utf-8')
else:
    print("⚠️ Точный паттерн не найден — показываю текущий:")
    lines = s.split('\n')
    for i, line in enumerate(lines):
        if 'class ChannelResponse' in line:
            for j in range(i, min(i+20, len(lines))):
                print(f"   {j+1}: {lines[j]}")
            break

import py_compile
try:
    py_compile.compile(str(f), doraise=True)
    print("✅✅✅ schemas.py валиден! ✅✅✅")
except py_compile.PyCompileError as e:
    print(f"❌ Ошибка: {e}")