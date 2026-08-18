import pathlib

f = pathlib.Path('./frontend/src/pages/Channels.tsx')
lines = f.read_text(encoding='utf-8').split('\n')

# Ищем интерфейс Channel и добавляем поля после platform
new_lines = []
in_channel_interface = False
added = False

for i, line in enumerate(lines):
    new_lines.append(line)
    
    if 'interface Channel {' in line or 'interface Channel\b' in line:
        in_channel_interface = True
    
    if in_channel_interface and not added:
        # Добавляем поля после строки с platform
        if 'platform: string;' in line:
            new_lines.append('  vk_group_id?: string;')
            new_lines.append('  vk_access_token?: string;')
            new_lines.append('  youtube_channel_id?: string;')
            new_lines.append('  youtube_api_key?: string;')
            new_lines.append('  dzen_channel_id?: string;')
            new_lines.append('  dzen_api_key?: string;')
            added = True
            print("✅ Добавлены поля vk_*, youtube_*, dzen_* в интерфейс Channel")
    
    if in_channel_interface and line.strip() == '}' and added:
        in_channel_interface = False

f.write_text('\n'.join(new_lines), encoding='utf-8')