import pathlib

f = pathlib.Path('./engines/telegram/publisher.py')
s = f.read_text(encoding='utf-8')

# Новый правильный метод publish_with_image
new_method = '''
    def publish_with_image(self, text: str, image_url: str, bot_token: str = None, chat_id: str = None) -> dict:
        """Публикует пост с картинкой через Telegram Bot API."""
        import requests
        
        if not bot_token or not chat_id:
            raise ValueError("bot_token and chat_id are required")
        
        url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
        
        # Формируем данные для Telegram API
        data = {
            "chat_id": chat_id,
            "photo": image_url,
            "caption": text[:1024],  # Telegram ограничивает caption 1024 символами
            "parse_mode": "HTML"
        }
        
        try:
            logger.info(f"Sending photo to {chat_id}: {image_url[:80]}...")
            response = requests.post(url, data=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"✅ Photo sent: message_id={result['result']['message_id']}")
            
            return {
                "status": "success",
                "message_id": result["result"]["message_id"],
                "chat_id": chat_id
            }
        
        except Exception as e:
            logger.error(f"sendPhoto failed: {e}")
            # Fallback: публикуем только текст
            logger.info("Falling back to text-only publish")
            return self.publish(text, bot_token, chat_id)
'''

# Ищем старый метод и заменяем
if 'def publish_with_image' in s:
    # Находим начало и конец метода
    start = s.find('    def publish_with_image')
    if start != -1:
        # Ищем следующий метод или конец класса
        end = s.find('\n    def ', start + 1)
        if end == -1:
            end = len(s)
        
        s = s[:start] + new_method + s[end:]
        f.write_text(s, encoding='utf-8')
        print("✅ publish_with_image исправлен")
    else:
        print("⚠️ Не удалось найти метод")
else:
    print("⚠️ Метод publish_with_image не найден")

import py_compile
try:
    py_compile.compile(str(f), doraise=True)
    print("✅✅✅ publisher.py валиден! ✅✅✅")
except py_compile.PyCompileError as e:
    print(f"❌ Ошибка: {e}")