import pathlib

f = pathlib.Path('./backend/automation/publishers/telegram.py')
s = f.read_text(encoding='utf-8')

# Ищем метод publish и добавляем поддержку image_url
old_publish = '''        try:
            result = self.engine.publish(
                text=text,
                bot_token=credentials["bot_token"],
                chat_id=credentials["chat_id"]
            )

            return PublishResult(
                success=True,
                message_id=str(result.message_id),
                published_at=result.published_at,
                platform_data={"telegram_message_id": result.message_id}
            )'''

new_publish = '''        # Sprint 11: поддержка картинок
        image_url = kwargs.get('image_url')
        
        try:
            if image_url:
                # Публикуем с картинкой через sendPhoto
                result = self.engine.publish_photo(
                    text=text,
                    image_url=image_url,
                    bot_token=credentials["bot_token"],
                    chat_id=credentials["chat_id"]
                )
            else:
                # Обычная публикация текстом
                result = self.engine.publish(
                    text=text,
                    bot_token=credentials["bot_token"],
                    chat_id=credentials["chat_id"]
                )

            return PublishResult(
                success=True,
                message_id=str(result.message_id),
                published_at=result.published_at,
                platform_data={
                    "telegram_message_id": result.message_id,
                    "has_image": bool(image_url)
                }
            )'''

if old_publish in s:
    s = s.replace(old_publish, new_publish, 1)
    f.write_text(s, encoding='utf-8')
    print("✅ TelegramPublisher обновлён — поддерживает image_url")
else:
    print("⚠️ Паттерн не найден")

import py_compile
py_compile.compile(str(f), doraise=True)
print("✅✅✅ telegram.py валиден! ✅✅✅")