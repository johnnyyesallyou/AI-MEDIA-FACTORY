import pathlib

f = pathlib.Path('./engines/telegram/publisher.py')
s = f.read_text(encoding='utf-8')

if 'def publish_photo' in s:
    print("ℹ️ publish_photo уже существует")
else:
    photo_method = '''
    
    def publish_photo(self, text: str, image_url: str) -> dict:
        """Публикует пост с картинкой через Telegram sendPhoto API."""
        import requests
        
        url = f"https://api.telegram.org/bot{self.bot_token}/sendPhoto"
        
        payload = {
            "chat_id": self.chat_id,
            "photo": image_url,
            "caption": text,
            "parse_mode": "HTML"
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data.get("ok"):
                message_id = data["result"]["message_id"]
                return {
                    "status": "success",
                    "message_id": message_id,
                    "chat_id": self.chat_id,
                    "text_length": len(text)
                }
            else:
                raise Exception(f"Telegram API error: {data}")
        
        except Exception as e:
            logger.error(f"sendPhoto failed: {e}")
            # Fallback: публикуем только текст
            logger.info("Falling back to text-only publish")
            return self.publish(text)
'''
    
    # Вставляем в конец класса
    s += photo_method
    f.write_text(s, encoding='utf-8')
    print("✅ publish_photo добавлен в TelegramPublisher")

import py_compile
py_compile.compile(str(f), doraise=True)
print("✅✅✅ publisher.py валиден! ✅✅✅")