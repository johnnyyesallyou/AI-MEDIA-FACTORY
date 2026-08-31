import pathlib, re

p = pathlib.Path('./backend/automation/jobs/automation_jobs.py')
s = p.read_text(encoding='utf-8')

# 1. Добавляем импорт PublisherFactory
if "from backend.automation.publishers import PublisherFactory" not in s:
    s = s.replace(
        "from engines.telegram.engine import TelegramEngine",
        "from engines.telegram.engine import TelegramEngine\nfrom backend.automation.publishers import PublisherFactory"
    )
    print("✅ Добавлен импорт PublisherFactory")

# 2. Находим блок telegram.publish и заменяем на PublisherFactory
# Ищем: "result = telegram.publish("
old_pattern = r'''result = telegram\.publish\(\s*text=item\.draft_text,\s*bot_token=channel\.bot_token,\s*chat_id=channel\.chat_id\s*\)'''

new_code = '''# Sprint 8.5: используем PublisherFactory
            platform = getattr(channel, "platform", "telegram") or "telegram"
            publisher = PublisherFactory.get(platform)
            credentials = {
                "bot_token": getattr(channel, "bot_token", None),
                "chat_id": getattr(channel, "chat_id", None),
            }
            
            if not publisher.validate_credentials(credentials):
                logger.warning("Skip publish item=%s invalid credentials for platform=%s", item.id, platform)
                continue
            
            result = publisher.publish(text=item.draft_text, credentials=credentials, channel=channel)
            
            if not result.success:
                logger.warning("Skip publish item=%s platform=%s error=%s", item.id, platform, result.error)
                continue'''

s_new, count = re.subn(old_pattern, new_code, s, flags=re.DOTALL)

if count > 0:
    s = s_new
    print(f"✅ Заменён telegram.publish на PublisherFactory ({count} раз)")
else:
    print("⚠️ Паттерн telegram.publish не найден")

p.write_text(s, encoding='utf-8')

# Проверяем синтаксис
import py_compile
try:
    py_compile.compile(str(p), doraise=True)
    print("✅✅✅ СИНТАКСИС ВАЛИДЕН! ✅✅✅")
except py_compile.PyCompileError as e:
    print(f"❌ Ошибка: {e}")