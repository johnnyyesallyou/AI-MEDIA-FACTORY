import pathlib

f = pathlib.Path('./frontend/src/pages/Channels.tsx')
s = f.read_text(encoding='utf-8')

# Старый dropdown (только text)
old_dropdown = '''                  <option value="telegram">Telegram</option>
                  <option value="vk">VK</option>
                  <option value="youtube">YouTube</option>'''

# Новый dropdown с Dzen + эмодзи
new_dropdown = '''                  <option value="telegram">📱 Telegram</option>
                  <option value="vk">🔵 VK (ВКонтакте)</option>
                  <option value="youtube">▶️ YouTube Shorts</option>
                  <option value="dzen">📰 Dzen (Дзен)</option>'''

if old_dropdown in s:
    s = s.replace(old_dropdown, new_dropdown, 1)
    print("✅ Добавлен Dzen в dropdown + эмодзи")
    f.write_text(s, encoding='utf-8')
else:
    print("⚠️ Dropdown не найден в точном виде — показываю текущий:")
    lines = s.split('\n')
    for i, line in enumerate(lines):
        if 'value="telegram"' in line or 'value="vk"' in line:
            for j in range(max(0, i-2), min(i+5, len(lines))):
                print(f"   {j+1}: {lines[j]}")
            break