import pathlib

p = pathlib.Path("/app/backend/automation/publishers/__init__.py")
c = p.read_text(encoding="utf-8")

# Добавляем VK publisher
if "VKPublisher" not in c:
    # Импортируем VK engine
    c = c.replace(
        "from .telegram_publisher import TelegramPublisher",
        "from .telegram_publisher import TelegramPublisher\nfrom .vk_publisher import VKPublisher",
    )
    
    # Добавляем в factory
    c = c.replace(
        '        if platform == "telegram":\n            return TelegramPublisher()',
        '        if platform == "telegram":\n            return TelegramPublisher()\n        elif platform == "vk":\n            return VKPublisher()',
    )
    
    p.write_text(c, encoding="utf-8")
    print("[OK] VK publisher added to factory")
else:
    print("[i] VK publisher already exists")