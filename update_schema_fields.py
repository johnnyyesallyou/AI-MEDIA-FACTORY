import pathlib

f = pathlib.Path('./backend/app/api/v1/schemas.py')
lines = f.read_text(encoding='utf-8').split('\n')

# Ищем ChannelResponse и добавляем поля после chat_id
new_lines = []
in_channel_response = False
added = False

for i, line in enumerate(lines):
    new_lines.append(line)
    
    if 'class ChannelResponse' in line:
        in_channel_response = True
    
    if in_channel_response and not added and 'chat_id: Optional[str] = None' in line:
        # Добавляем VK/YouTube/Dzen поля
        new_lines.append('    # Sprint 11: VK credentials')
        new_lines.append('    vk_group_id: Optional[str] = None')
        new_lines.append('    vk_access_token: Optional[str] = None')
        new_lines.append('    # Sprint 11: YouTube credentials')
        new_lines.append('    youtube_channel_id: Optional[str] = None')
        new_lines.append('    youtube_api_key: Optional[str] = None')
        new_lines.append('    # Sprint 11: Dzen credentials')
        new_lines.append('    dzen_channel_id: Optional[str] = None')
        new_lines.append('    dzen_api_key: Optional[str] = None')
        added = True
        print("✅ Добавлены поля vk_*, youtube_*, dzen_* в ChannelResponse")
    
    if in_channel_response and line.strip().startswith('class ') and 'ChannelResponse' not in line:
        in_channel_response = False

f.write_text('\n'.join(new_lines), encoding='utf-8')

import py_compile
try:
    py_compile.compile(str(f), doraise=True)
    print("✅✅✅ schemas.py валиден! ✅✅✅")
except py_compile.PyCompileError as e:
    print(f"❌ Ошибка: {e}")