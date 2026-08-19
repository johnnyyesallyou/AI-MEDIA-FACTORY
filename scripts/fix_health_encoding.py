import pathlib, py_compile

f = pathlib.Path('./backend/app/api/v1/health.py')
s = f.read_text(encoding='utf-8')
changes = []

# Заменяем русские сообщения на английские (избегаем проблем кодировки)
replacements = {
    "PostgreSQL доступен": "PostgreSQL is available",
    "Redis доступен": "Redis is available",
    "Ollama доступен.": "Ollama is available.",
    "Timeout: Ollama не отвечает за 5 секунд": "Timeout: Ollama not responding within 5s",
    "Ошибка:": "Error:",
    " моделей": " models"
}

for old, new in replacements.items():
    if old in s:
        s = s.replace(old, new, 1)
        changes.append(f"   {old} → {new}")

if changes:
    f.write_text(s, encoding='utf-8')
    print(f"✅ Применено {len(changes)} замен:")
    for c in changes:
        print(c)
else:
    print("ℹ️ Все сообщения уже на английском")

try:
    py_compile.compile(str(f), doraise=True)
    print("✅✅✅ Синтаксис валиден! ✅✅✅")
except py_compile.PyCompileError as e:
    print(f"❌ Ошибка: {e}")