import pathlib

f = pathlib.Path('./backend/app/api/v1/health.py')
s = f.read_text(encoding='utf-8')

# Заменяем f-string с "моделей"
old = 'f"Ollama is available. {len(models)} моделей"'
new = 'f"Ollama is available. {len(models)} models"'

if old in s:
    s = s.replace(old, new, 1)
    f.write_text(s, encoding='utf-8')
    print("✅ Заменено: 'моделей' → 'models'")
else:
    # Пробуем другой вариант
    lines = s.split('\n')
    for i, line in enumerate(lines):
        if 'моделей' in line or 'модель' in line.lower():
            print(f"   Строка {i+1}: {line.strip()}")

import py_compile
py_compile.compile(str(f), doraise=True)
print("✅✅✅ Валидно!")