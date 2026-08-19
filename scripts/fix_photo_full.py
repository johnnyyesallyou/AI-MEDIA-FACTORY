import pathlib, py_compile

f = pathlib.Path('./engines/telegram/publisher.py')
s = f.read_text(encoding='utf-8')

# Находим метод publish_photo и полностью его заменяем
start = s.find('    def publish_photo(self, text: str, image_url: str)')
if start == -1:
    print('❌ Метод publish_photo не найден')
    exit(1)

# Находим конец метода (следующий метод класса или конец файла)
end = s.find('\n    def ', start + 10)
if end == -1:
    end = len(s)

print(f'Найден метод publish_photo: строки с {start} по {end}')

# Новый правильный метод
new_method = '''    def publish_photo(self, text: str, image_url: str) -> dict:
        """Публикует пост с картинкой через Telegram sendPhoto API."""
        url = self._url("sendPhoto")

        # Telegram ограничивает caption 1024 символами
        clean_text = _strip_markdown(text) if '_strip_markdown' in globals() else text
        if len(clean_text) > 1024:
            clean_text = clean_text[:1021] + "..."

        payload = {
            "chat_id": self.chat_id,
            "photo": image_url,
            "caption": clean_text,
        }

        try:
            logger.info(f"Sending photo: chat_id={self.chat_id}")
            logger.info(f"   image_url: {image_url[:100]}...")
            logger.info(f"   caption length: {len(clean_text)} chars")

            # ВАЖНО: data= вместо json= (Telegram ожидает form-data)
            response = requests.post(url, data=payload, timeout=30)

            # Логируем ответ ПЕРЕД raise_for_status
            logger.info(f"   Response status: {response.status_code}")
            if response.status_code != 200:
                logger.error(f"   Response body: {response.text[:500]}")
                # Не вызываем raise_for_status, а парсим JSON
                try:
                    data = response.json()
                    error_code = data.get("error_code", response.status_code)
                    description = data.get("description", response.text[:200])
                    logger.error(f"Telegram API error: code={error_code}, desc={description}")
                    
                    # Flood control
                    if error_code == 429:
                        retry_after = data.get("parameters", {}).get("retry_after", 10)
                        logger.warning(f"Flood control: waiting {retry_after} sec")
                        time.sleep(retry_after)
                        return self.publish_photo(text, image_url)
                    
                    # Fallback к тексту
                    logger.info("Falling back to text-only publish")
                    return self.publish(text)
                    
                except Exception as json_err:
                    logger.error(f"Cannot parse JSON: {json_err}")
                    logger.info("Falling back to text-only publish")
                    return self.publish(text)
            else:
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
                logger.info("Falling back to text-only publish")
                return self.publish(text)

        except Exception as e:
            logger.error(f"sendPhoto failed: {e}")
            logger.info("Falling back to text-only publish")
            return self.publish(text)
'''

# Заменяем
s = s[:start] + new_method + s[end:]
f.write_text(s, encoding='utf-8')
print('✅ publish_photo полностью перезаписан')

try:
    py_compile.compile(str(f), doraise=True)
    print('✅✅✅ publisher.py валиден! ✅✅✅')
except py_compile.PyCompileError as e:
    print(f'❌ Ошибка: {e}')