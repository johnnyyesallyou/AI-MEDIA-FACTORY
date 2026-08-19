import pathlib

p = pathlib.Path("/app/engines/source_adapters/readmanga_adapter.py")
c = p.read_text(encoding="utf-8")

# Исправляем regex для title (добавляем re.DOTALL для \s)
old = '''            title = re.sub(r'\s*—\s*RM\.me.*$', '', title_text)
                title = re.sub(r'^Манхва\s+', '', title)
                title = re.sub(r'\s*онлайн.*$', '', title, flags=re.IGNORECASE)
                # Убираем скобки с оригинальным названием если есть
                title = re.sub(r'\s*\([^)]*\)\s*', '', title)'''

new = '''            title = re.sub(r'\s*—\s*RM\.me.*$', '', title_text, flags=re.DOTALL)
                title = re.sub(r'^Манхва\s+', '', title)
                title = re.sub(r'\s*онлайн.*$', '', title, flags=re.IGNORECASE | re.DOTALL)
                # Убираем скобки с оригинальным названием если есть
                title = re.sub(r'\s*\([^)]*\)\s*', '', title)
                title = title.strip()'''

if old in c:
    c = c.replace(old, new, 1)
    p.write_text(c, encoding="utf-8")
    print("✅ Title regex fixed (re.DOTALL)")
else:
    print("ℹ️ Already fixed or marker not found")