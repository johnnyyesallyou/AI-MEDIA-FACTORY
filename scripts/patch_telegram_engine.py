import pathlib

f = pathlib.Path('./engines/telegram/engine.py')
s = f.read_text(encoding='utf-8')

if 'def publish_photo' in s:
    print("ℹ️ publish_photo уже существует")
else:
    publish_photo_method = '''
    
    def publish_photo(
        self,
        text: str,
        image_url: str,
        bot_token: str,
        chat_id: str
    ) -> TelegramPublishResult:
        """Публикует пост с картинкой через sendPhoto."""
        try:
            publisher = TelegramPublisher(
                bot_token=bot_token,
                chat_id=chat_id
            )
            
            result = publisher.publish_photo(text=text, image_url=image_url)
            
            return TelegramPublishResult(
                status=result["status"],
                message_id=result["message_id"],
                chat_id=result["chat_id"],
                published_at=datetime.utcnow(),
                text_length=result["text_length"]
            )
        
        except Exception as e:
            logger.exception("Telegram publish_photo failed")
            raise TelegramPublishError(str(e))
'''
    
    # Вставляем перед последним except блоком
    lines = s.split('\n')
    insert_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith('except Exception as e:') and i > 20:
            insert_idx = i
            break
    
    if insert_idx:
        # Находим конец метода publish (следующий def или конец класса)
        lines.insert(insert_idx, publish_photo_method)
        s = '\n'.join(lines)
        f.write_text(s, encoding='utf-8')
        print(f"✅ publish_photo добавлен в TelegramEngine (строка {insert_idx+1})")

import py_compile
py_compile.compile(str(f), doraise=True)
print("✅✅✅ engine.py валиден! ✅✅✅")