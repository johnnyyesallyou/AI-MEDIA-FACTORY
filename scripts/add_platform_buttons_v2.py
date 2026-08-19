import pathlib, re

f = pathlib.Path('./frontend/src/pages/Channels.tsx')
s = f.read_text(encoding='utf-8')

# Ищем место где рендерятся кнопки действий для канала
# Обычно это div с классом flex gap-2, где есть кнопка Telegram
# Ищем по наличию openTelegramModal и title="Подключить Telegram"

telegram_button_pattern = r'''(<button\s+onClick=\{\(\) => openTelegramModal\(channel\.id\)\}[^>]*>\s*<Send size=\{18\} />\s*</button>\s*</button>\s*\)\})'''

# Если есть точный match
if "channel.platform === 'vk'" not in s:
    # Добавим кнопки после всей конструкции {channel.platform === 'telegram' && (...)}
    
    # Ищем закрывающую скобку telegram блока
    old_block = '''                  {channel.platform === 'telegram' && (
                    <button
                      onClick={() => openTelegramModal(channel.id)}
                      className="p-2 text-blue-400 hover:text-blue-300 hover:bg-gray-700 rounded"
                      title="Подключить Telegram"
                    >
                      <Send size={18} />
                    </button>
                  )}'''
    
    new_block = '''                  {channel.platform === 'telegram' && (
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
    
    if old_block in s:
        s = s.replace(old_block, new_block, 1)
        f.write_text(s, encoding='utf-8')
        print("✅ Добавлены кнопки VK/YouTube/Dzen")
    else:
        print("⚠️ Паттерн не совпал — добавим через regex")
        
        # Альтернатива: ищем по title="Подключить Telegram" и добавляем после
        import re
        pattern = r'(<button[^>]*title="Подключить Telegram"[^>]*>.*?</button>\s*\)\})'
        match = re.search(pattern, s, re.DOTALL)
        if match:
            insert_after = match.group(0)
            new_buttons = '''
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
            s = s.replace(insert_after, insert_after + new_buttons, 1)
            f.write_text(s, encoding='utf-8')
            print("✅ Добавлены кнопки через regex")
        else:
            print("❌ Не удалось найти место для вставки")