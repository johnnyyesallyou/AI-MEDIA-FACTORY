import pathlib

f = pathlib.Path('./frontend/src/pages/Channels.tsx')
s = f.read_text(encoding='utf-8')

# Ищем место где сейчас есть кнопка Telegram (channel.platform === 'telegram')
# И добавляем кнопки для других платформ

old_buttons = '''                  {channel.platform === 'telegram' && (
                    <button
                      onClick={() => openTelegramModal(channel.id)}
                      className="p-2 text-blue-400 hover:text-blue-300 hover:bg-gray-700 rounded"
                      title="Подключить Telegram"
                    >
                      <Send size={18} />
                    </button>
                  )}'''

new_buttons = '''                  {channel.platform === 'telegram' && (
                    <button
                      onClick={() => openTelegramModal(channel.id)}
                      className="p-2 text-blue-400 hover:text-blue-300 hover:bg-gray-700 rounded"
                      title="Подключить Telegram"
                    >
                      <Send size={18} />
                    </button>
                  )}
                  {channel.platform === 'vk' && (
                    <button
                      onClick={() => openVkModal(channel.id)}
                      className="p-2 text-blue-500 hover:text-blue-400 hover:bg-gray-700 rounded"
                      title="Подключить VK"
                    >
                      🔵
                    </button>
                  )}
                  {channel.platform === 'youtube' && (
                    <button
                      onClick={() => openYoutubeModal(channel.id)}
                      className="p-2 text-red-500 hover:text-red-400 hover:bg-gray-700 rounded"
                      title="Подключить YouTube"
                    >
                      ▶️
                    </button>
                  )}
                  {channel.platform === 'dzen' && (
                    <button
                      onClick={() => openDzenModal(channel.id)}
                      className="p-2 text-yellow-500 hover:text-yellow-400 hover:bg-gray-700 rounded"
                      title="Подключить Dzen"
                    >
                      📰
                    </button>
                  )}'''

if old_buttons in s:
    s = s.replace(old_buttons, new_buttons, 1)
    print("✅ Добавлены кнопки подключения для VK/YouTube/Dzen")
    f.write_text(s, encoding='utf-8')
else:
    print("⚠️ Точный паттерн не найден — показываю текущий код:")
    lines = s.split('\n')
    for i, line in enumerate(lines):
        if "channel.platform === 'telegram'" in line and 'openTelegramModal' in s[s.find(line):s.find(line)+500]:
            for j in range(max(0, i-1), min(i+10, len(lines))):
                print(f"   {j+1}: {lines[j]}")
            break