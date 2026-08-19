import pathlib

p = pathlib.Path("/app/backend/automation/jobs/manga_publish_job.py")
content = p.read_text(encoding="utf-8")

# Добавляем передачу inline_buttons в publish_photo
old_call = '''        result = publisher.publish_photo(text=text, image_url=image_url)'''

new_call = '''        # Sprint 19: Inline-кнопки (Читать на источнике + Telegraph)
        inline_buttons = []
        if telegraph_url:
            inline_buttons.append({"text": "📖 Читать на Telegraph", "url": telegraph_url})
        if short_url and short_url != telegraph_url:
            inline_buttons.append({"text": "🔗 Источник", "url": short_url})
        
        result = publisher.publish_photo(
            text=text,
            image_url=image_url,
            inline_buttons=inline_buttons
        )'''

if old_call in content:
    content = content.replace(old_call, new_call)
    print("✅ Inline buttons added")
else:
    print("❌ Block not found")

p.write_text(content, encoding="utf-8")

import ast
ast.parse(content)
print("✅ Syntax OK")