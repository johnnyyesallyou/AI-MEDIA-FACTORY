import pathlib, re

p = pathlib.Path('./backend/automation/jobs/automation_jobs.py')
s = p.read_text(encoding='utf-8')
changes = []

# 1. Добавляем импорт PublisherFactory
import_marker = "from engines.telegram.engine import TelegramEngine"
if import_marker in s and "from backend.automation.publishers" not in s:
    s = s.replace(
        import_marker,
        import_marker + "\nfrom backend.automation.publishers import PublisherFactory",
        1
    )
    changes.append("добавлен импорт PublisherFactory")

# 2. Находим блок Telegram-публикации и заменяем на PublisherFactory
# Ищем старый блок: "telegram = TelegramEngine()" + "telegram.publish(...)"
old_block_pattern = r'''(telegram\s*=\s*TelegramEngine\(\).*?result\s*=\s*telegram\.publish\(\s*text=item\.draft_text,\s*bot_token=channel\.bot_token,\s*chat_id=channel\.chat_id\s*\))'''

match = re.search(old_block_pattern, s, re.DOTALL)
if match:
    # Заменяем на использование PublisherFactory
    new_block = '''# Sprint 8.5: используем PublisherFactory для поддержки разных платформ
            platform = getattr(channel, "platform", "telegram") or "telegram"
            publisher = PublisherFactory.get(platform)
            
            # Собираем credentials для платформы
            credentials = {
                "bot_token": getattr(channel, "bot_token", None),
                "chat_id": getattr(channel, "chat_id", None),
            }
            
            if not publisher.validate_credentials(credentials):
                logger.warning(
                    "Skip publish item=%s invalid credentials for platform=%s",
                    item.id, platform
                )
                continue
            
            result = publisher.publish(
                text=item.draft_text,
                credentials=credentials,
                channel=channel
            )
            
            if not result.success:
                logger.warning(
                    "Skip publish item=%s platform=%s error=%s",
                    item.id, platform, result.error
                )
                continue'''
    
    s = s[:match.start()] + new_block + s[match.end():]
    changes.append("TelegramEngine заменён на PublisherFactory")
else:
    print("⚠️ Паттерн TelegramEngine не найден")
    # Показываем текущее состояние
    lines = s.split('\n')
    for i, line in enumerate(lines):
        if 'TelegramEngine' in line or 'telegram.publish' in line:
            print(f"   L{i+1}: {line.strip()}")

# 3. Фиксим обработку результата (result.message_id → result.message_id)
# Старый код: item.telegram_message_id = str(result.message_id)
# Новый код тоже использует result.message_id — ничего не меняем

if changes:
    p.write_text(s, encoding='utf-8')
    print(f"\n✅ Применено {len(changes)} фиксов:")
    for c in changes:
        print(f"   - {c}")
else:
    print("\n⚠️ Изменения не применены")