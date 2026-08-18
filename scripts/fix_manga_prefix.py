import pathlib

p = pathlib.Path("/app/engines/source_adapters/readmanga_adapter.py")
c = p.read_text(encoding="utf-8")

# Добавляем удаление префиксов "Манга", "Манхва", "Маньхуа", "Комикс"
old = '''            title = re.sub(r'\s*—\s*RM\.me.*$', '', title_text, flags=re.DOTALL)
                title = re.sub(r'^Манхва\s+', '', title)'''

new = '''            title = re.sub(r'\s*—\s*RM\.me.*$', '', title_text, flags=re.DOTALL)
                # Убираем префиксы типов контента
                title = re.sub(r'^(Манга|Манхва|Маньхуа|Комикс)\s+', '', title, flags=re.IGNORECASE)'''

if old in c:
    c = c.replace(old, new, 1)
    p.write_text(c, encoding="utf-8")
    print("✅ Manga prefix removal added")
else:
    print("ℹ️ Marker not found")