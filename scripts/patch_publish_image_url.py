import pathlib, py_compile

f = pathlib.Path('./backend/automation/jobs/automation_jobs.py')
s = f.read_text(encoding='utf-8')

# Ищем где вызывается publisher.publish и добавляем image_url
old_publish = '''                    # Sprint 11: передаём asset_id для публикации с картинкой
                    asset_id = getattr(item, 'asset_id', None)
                    
                    result = publisher.publish(
                        text=full_text,
                        credentials=credentials,
                        channel=channel,
                        asset_id=asset_id
                    )'''

new_publish = '''                    # Sprint 11: передаём image_url для публикации с картинкой
                    image_url = getattr(item, 'image_url', None)
                    
                    result = publisher.publish(
                        text=full_text,
                        credentials=credentials,
                        channel=channel,
                        image_url=image_url
                    )'''

if old_publish in s:
    s = s.replace(old_publish, new_publish, 1)
    f.write_text(s, encoding='utf-8')
    print("✅ PublishJob обновлён — передаёт image_url")
else:
    print("⚠️ Паттерн не найден")

try:
    py_compile.compile(str(f), doraise=True)
    print("✅✅✅ automation_jobs.py валиден! ✅✅✅")
except py_compile.PyCompileError as e:
    print(f"❌ Ошибка: {e}")