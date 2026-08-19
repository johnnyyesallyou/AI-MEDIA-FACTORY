import pathlib

f = pathlib.Path('./backend/app/api/v1/channels.py')
lines = f.read_text(encoding='utf-8').split('\n')

# Ищем строку с is_connected=c.is_connected и вставляем перед ней новые поля
new_lines = []
added = False

for i, line in enumerate(lines):
    if not added and 'is_connected=c.is_connected,' in line:
        # Вставляем новые поля перед is_connected
        indent = '        '
        new_lines.append(indent + '# Sprint 11: Multi-platform credentials')
        new_lines.append(indent + 'vk_group_id=getattr(c, "vk_group_id", None),')
        new_lines.append(indent + 'vk_access_token=getattr(c, "vk_access_token", None),')
        new_lines.append(indent + 'youtube_channel_id=getattr(c, "youtube_channel_id", None),')
        new_lines.append(indent + 'youtube_api_key=getattr(c, "youtube_api_key", None),')
        new_lines.append(indent + 'dzen_channel_id=getattr(c, "dzen_channel_id", None),')
        new_lines.append(indent + 'dzen_api_key=getattr(c, "dzen_api_key", None),')
        added = True
        print("✅ Добавлены поля vk_*, youtube_*, dzen_* в _to_response")
    
    new_lines.append(line)

f.write_text('\n'.join(new_lines), encoding='utf-8')

import py_compile
try:
    py_compile.compile(str(f), doraise=True)
    print("✅✅✅ channels.py валиден! ✅✅✅")
except py_compile.PyCompileError as e:
    print(f"❌ Ошибка: {e}")