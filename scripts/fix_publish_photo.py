import pathlib, py_compile

f = pathlib.Path('./engines/telegram/publisher.py')
s = f.read_text(encoding='utf-8')

# Старый метод publish_photo
old_method = '''    def publish_photo(self, text: str, image_url: str) -> dict:
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
            return self.publish(text)'''

# Новый исправленный метод
new_method = '''    def publish_photo(self, text: str, image_url: str) -> dict:
        """Публикует пост с картинкой через Telegram sendPhoto API."""
        url = self._url("sendPhoto")

        # Telegram ограничивает caption 1024 символами
        clean_text = _strip_markdown(text)
        if len(clean_text) > 1024:
            clean_text = clean_text[:1021] + "..."

        payload = {
            "chat_id": self.chat_id,
            "photo": image_url,
            "caption": clean_text,
        }

        try:
            logger.info(f"Sending photo: chat_id={self.chat_id}, image_url={image_url[:80]}...")
            logger.info(f"   Caption length: {len(clean_text)} chars")
            
            # ВАЖНО: data= вместо json= для form-data
            response = requests.post(url, data=payload, timeout=30)
            
            # Логируем полный ответ для диагностики
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"   Response body: {response.text[:500]}")
                response.raise_for_status()
            
            data = response.json()

            if data.get("ok"):
                message_id = data["result"]["message_id"]
                logger.info(f"✅ Photo sent: message_id={message_id}")
                return {
                    "status": "success",
                    "message_id": message_id,
                    "chat_id": self.chat_id,
                    "text_length": len(clean_text)
                }
            else:
                error_code = data.get("error_code")
                description = data.get("description")
                logger.error(f"Telegram API error code={error_code} description={description}")
                
                # Flood control
                if error_code == 429:
                    retry_after = data.get("parameters", {}).get("retry_after", 10)
                    logger.warning(f"Flood control: waiting {retry_after} sec")
                    time.sleep(retry_after)
                    return self.publish_photo(text, image_url)
                
                raise Exception(f"Telegram API error: {data}")

        except Exception as e:
            logger.error(f"sendPhoto failed: {e}")
            # Fallback: публикуем только текст
            logger.info("Falling back to text-only publish")
            return self.publish(text)'''

if old_method in s:
    s = s.replace(old_method, new_method, 1)
    f.write_text(s, encoding='utf-8')
    print("✅ publish_photo исправлен (data= вместо json=)")
else:
    print("⚠️ Старый метод не найден — показываю текущий:")
    # Показываем текущий метод
    start = s.find('def publish_photo')
    if start != -1:
        end = s.find('\n    def ', start + 1)
        if end == -1:
            end = len(s)
        print(s[start:end])

try:
    py_compile.compile(str(f), doraise=True)
    print("✅✅✅ publisher.py валиден! ✅✅✅")
except py_compile.PyCompileError as e:
    print(f"❌ Ошибка: {e}")