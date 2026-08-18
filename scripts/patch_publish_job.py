import pathlib, py_compile

# Путь в контейнере и локально совпадают относительно workspace
f = pathlib.Path('./backend/automation/jobs/automation_jobs.py')
s = f.read_text(encoding='utf-8')

# Ищем старый блок credentials (только для Telegram)
old_block = '''                    # Собираем credentials для платформы
                    credentials = {
                        "bot_token": getattr(channel, "bot_token", None),
                        "chat_id": getattr(channel, "chat_id", None),
                    }'''

# Пробуем найти через паттерн (если есть несовпадение пробелов)
if old_block not in s:
    # Ищем альтернативным паттерном
    lines = s.split('\n')
    start_idx = None
    for i, line in enumerate(lines):
        if 'bot_token' in line and 'chat_id' in lines[i+1] if i+1 < len(lines) else False:
            # Ищем начало блока (строка с "credentials = {")
            for j in range(max(0, i-3), i):
                if 'credentials = {' in lines[j]:
                    start_idx = j
                    break
            if start_idx:
                # Ищем закрывающую }
                for j in range(i, min(i+3, len(lines))):
                    if '}' in lines[j]:
                        end_idx = j + 1
                        print(f"Найден блок credentials: строки {start_idx+1}-{end_idx}")
                        print("Текущий блок:")
                        for k in range(start_idx, end_idx):
                            print(f"   {k+1}: {lines[k]}")
                        break
                break
    
    # Замена через строки
    if start_idx is not None:
        # Формируем новый блок
        indent = '                    '
        new_lines = [
            indent + '# Sprint 11: Собираем credentials в зависимости от платформы',
            indent + 'if platform == "vk":',
            indent + '    credentials = {',
            indent + '        "group_id": getattr(channel, "vk_group_id", None),',
            indent + '        "access_token": getattr(channel, "vk_access_token", None),',
            indent + '    }',
            indent + 'elif platform == "youtube":',
            indent + '    credentials = {',
            indent + '        "channel_id": getattr(channel, "youtube_channel_id", None),',
            indent + '        "api_key": getattr(channel, "youtube_api_key", None),',
            indent + '    }',
            indent + 'elif platform == "dzen":',
            indent + '    credentials = {',
            indent + '        "channel_id": getattr(channel, "dzen_channel_id", None),',
            indent + '        "api_key": getattr(channel, "dzen_api_key", None),',
            indent + '    }',
            indent + 'else:  # telegram (default)',
            indent + '    credentials = {',
            indent + '        "bot_token": getattr(channel, "bot_token", None),',
            indent + '        "chat_id": getattr(channel, "chat_id", None),',
            indent + '    }',
        ]
        # Заменяем блок
        lines[start_idx:end_idx] = new_lines
        s = '\n'.join(lines)
        f.write_text(s, encoding='utf-8')
        print("✅ PublishJob patched: multi-platform credentials")
    else:
        print("❌ Не удалось найти блок credentials")
        exit(1)
else:
    # Прямая замена
    new_block = '''                    # Sprint 11: Собираем credentials в зависимости от платформы
                    if platform == "vk":
                        credentials = {
                            "group_id": getattr(channel, "vk_group_id", None),
                            "access_token": getattr(channel, "vk_access_token", None),
                        }
                    elif platform == "youtube":
                        credentials = {
                            "channel_id": getattr(channel, "youtube_channel_id", None),
                            "api_key": getattr(channel, "youtube_api_key", None),
                        }
                    elif platform == "dzen":
                        credentials = {
                            "channel_id": getattr(channel, "dzen_channel_id", None),
                            "api_key": getattr(channel, "dzen_api_key", None),
                        }
                    else:  # telegram (default)
                        credentials = {
                            "bot_token": getattr(channel, "bot_token", None),
                            "chat_id": getattr(channel, "chat_id", None),
                        }'''
    s = s.replace(old_block, new_block, 1)
    f.write_text(s, encoding='utf-8')
    print("✅ PublishJob patched: multi-platform credentials")

try:
    py_compile.compile(str(f), doraise=True)
    print("✅✅✅ automation_jobs.py валиден! ✅✅✅")
except py_compile.PyCompileError as e:
    print(f"❌ Ошибка: {e}")