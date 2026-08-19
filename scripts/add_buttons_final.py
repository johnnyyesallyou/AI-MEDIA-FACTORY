import pathlib

f = pathlib.Path('./frontend/src/pages/Channels.tsx')
lines = f.read_text(encoding='utf-8').split('\n')

# Ищем строку с MessageCircle size={18} (Telegram кнопка) и её закрывающую )}
message_circle_idx = None
for i, line in enumerate(lines):
    if 'MessageCircle size={18}' in line:
        # Ищем )} в следующих 3 строках
        for j in range(i+1, min(i+4, len(lines))):
            if lines[j].strip() == ')}':
                message_circle_idx = j
                break
        break

if message_circle_idx:
    print(f"✅ Найдена Telegram кнопка на строке {message_circle_idx+1} (закрывающая )})")
    
    new_buttons = '''                  {channel.platform === 'vk' && (
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
    
    # Вставляем ПОСЛЕ message_circle_idx
    lines.insert(message_circle_idx + 1, new_buttons)
    f.write_text('\n'.join(lines), encoding='utf-8')
    print("✅ Кнопки VK/YouTube/Dzen добавлены в карточку канала")
else:
    print("❌ Не удалось найти Telegram кнопку с MessageCircle")