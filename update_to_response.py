import pathlib

f = pathlib.Path('./backend/app/api/v1/channels.py')
s = f.read_text(encoding='utf-8')

# Ищем _to_response и добавляем новые поля
old_to_response = '''        bot_token=c.bot_token,
        chat_id=c.chat_id,
        is_connected=c.is_connected,'''

new_to_response = '''        bot_token=c.bot_token,
        chat_id=c.chat_id,
        # Sprint 11: Multi-platform
        vk_group_id=getattr(c, 'vk_group_id', None),
        vk_access_token=getattr(c, 'vk_access_token', None),
        youtube_channel_id=getattr(c, 'youtube_channel_id', None),
        youtube_api_key=getattr(c, 'youtube_api_key', None),
        dzen_channel_id=getattr(c, 'dzen_channel_id', None),
        dzen_api_key=getattr(c, 'dzen_api_key', None),
        is_connected=c.is_connected,'''

if old_to_response in s:
    s = s.replace(old_to_response, new_to_response, 1)
    print("✅ _to_response обновлён — возвращает vk_*, youtube_*, dzen_* поля")
    f.write_text(s, encoding='utf-8')
else:
    print("⚠️ Паттерн не найден — показываю _to_response:")
    lines = s.split('\n')
    for i, line in enumerate(lines):
        if 'def _to_response' in line:
            for j in range(i, min(i+20, len(lines))):
                print(f"   {j+1}: {lines[j]}")
            break

import py_compile
try:
    py_compile.compile(str(f), doraise=True)
    print("✅✅✅ channels.py валиден! ✅✅✅")
except py_compile.PyCompileError as e:
    print(f"❌ Ошибка: {e}")