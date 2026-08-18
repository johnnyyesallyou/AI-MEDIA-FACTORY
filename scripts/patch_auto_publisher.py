import pathlib, py_compile

f = pathlib.Path('./backend/automation/publishers/telegram.py')
s = f.read_text(encoding='utf-8')

# Добавляем логирование image_url
if 'logger.info(f"Publishing with image: {image_url' not in s:
    # Находим блок с if image_url
    old_block = '''        image_url = kwargs.get('image_url')
        
        try:
            if image_url:
                # Публикуем с картинкой через sendPhoto
                result = self.engine.publish_photo('''
    
    new_block = '''        image_url = kwargs.get('image_url')
        
        logger.info(f"TelegramPublisher.publish: text_len={len(text)}, image_url={'YES' if image_url else 'NO'}")
        if image_url:
            logger.info(f"   image_url: {image_url[:100]}...")
        
        try:
            if image_url:
                # Публикуем с картинкой через sendPhoto
                logger.info(f"   Calling engine.publish_photo...")
                result = self.engine.publish_photo('''
    
    if old_block in s:
        s = s.replace(old_block, new_block, 1)
        f.write_text(s, encoding='utf-8')
        print("✅ Добавлено логирование image_url")
    else:
        print("⚠️ Паттерн не найден")

try:
    py_compile.compile(str(f), doraise=True)
    print("✅✅✅ telegram.py валиден! ✅✅✅")
except py_compile.PyCompileError as e:
    print(f"❌ Ошибка: {e}")