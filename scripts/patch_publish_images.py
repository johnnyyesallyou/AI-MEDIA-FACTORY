import pathlib

f = pathlib.Path('./backend/automation/jobs/automation_jobs.py')
s = f.read_text(encoding='utf-8')

# Ищем строку с publisher.publish и добавляем image_url
old_publish = '''                    # Публикуем через PublisherFactory (используем существующий draft_text!)
                    full_text = f"{item.headline}\\n\\n{item.draft_text}"
                    result = publisher.publish(
                        text=full_text,
                        credentials=credentials,
                        channel=channel
                    )'''

new_publish = '''                    # Публикуем через PublisherFactory (используем существующий draft_text!)
                    full_text = f"{item.headline}\\n\\n{item.draft_text}"
                    
                    # Sprint 11: добавляем картинку если есть
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

import py_compile
py_compile.compile(str(f), doraise=True)
print("✅✅✅ automation_jobs.py валиден! ✅✅✅")