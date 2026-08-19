import pathlib

f = pathlib.Path('./backend/automation/publishers/telegram.py')
s = f.read_text(encoding='utf-8')

# Проверяем есть ли уже image_url
if 'image_url' in s:
    print("ℹ️ image_url уже поддерживается")
else:
    # Находим метод publish и добавляем image_url поддержку
    # Ищем строку с result = self.engine.publish(
    
    if 'self.engine.publish(' in s and 'image_url' not in s:
        # Заменяем блок publish на версию с image_url
        old_block = '''        try:
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
        
        new_block = '''        # Sprint 11: поддержка картинок
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
        
        if old_block in s:
            s = s.replace(old_block, new_block, 1)
            f.write_text(s, encoding='utf-8')
            print("✅ telegram.py обновлён — поддерживает image_url")
        else:
            print("⚠️ Точный паттерн не найден — показываю текущий код:")
            lines = s.split('\n')
            for i, line in enumerate(lines):
                if 'self.engine.publish' in line:
                    for j in range(max(0, i-5), min(i+15, len(lines))):
                        print(f"   {j+1}: {lines[j]}")
                    break

import py_compile
try:
    py_compile.compile(str(f), doraise=True)
    print("✅✅✅ telegram.py валиден! ✅✅✅")
except py_compile.PyCompileError as e:
    print(f"❌ Ошибка: {e}")