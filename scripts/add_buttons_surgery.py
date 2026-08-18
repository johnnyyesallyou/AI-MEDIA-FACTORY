import pathlib

f = pathlib.Path('./frontend/src/pages/Channels.tsx')
lines = f.read_text(encoding='utf-8').split('\n')

# Ищем строку с </button> закрывающим Telegram кнопку
# Это строка с "Send size={18}" и после неё идёт </button>, </button>, )}
telegram_close_idx = None
for i, line in enumerate(lines):
    if 'Send size={18}' in line:
        # Ищем следующие строки с закрывающими тегами
        for j in range(i+1, min(i+5, len(lines))):
            if '</button>' in lines[j] and ')}' in lines[j+1] if j+1 < len(lines) else False:
                telegram_close_idx = j + 1  # Строка с )}
                break
            elif '</button>' in lines[j] and j+2 < len(lines) and ')}' in lines[j+2]:
                telegram_close_idx = j + 2
                break
        break

if telegram_close_idx:
    print(f"   Найдена Telegram кнопка на строке {telegram_close_idx+1}")
    
    # Вставляем новые кнопки ПОСЛЕ telegram_close_idx
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
    
    lines.insert(telegram_close_idx + 1, new_buttons)
    f.write_text('\n'.join(lines), encoding='utf-8')
    print("✅ Кнопки VK/YouTube/Dzen добавлены")
else:
    print("❌ Не удалось найти Telegram кнопку")
    print("   Показываю строки 295-315 (где обычно кнопки):")
    for i in range(294, min(315, len(lines))):
        print(f"   {i+1}: {lines[i]}")