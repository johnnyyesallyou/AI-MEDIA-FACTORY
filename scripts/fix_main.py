import pathlib

f = pathlib.Path('./backend/main.py')
lines = f.read_text(encoding='utf-8').split('\n')

# Ищем строку с лишним отступом
for i, line in enumerate(lines):
    if '    app.include_router(health_router' in line:
        # Убираем лишние 4 пробела
        lines[i] = line[4:]  # убираем первые 4 пробела
        print(f'✅ Исправлена строка {i+1}: убрал отступ')
        print(f'   Было: "{line}"')
        print(f'   Стало: "{lines[i]}"')
        break

f.write_text('\n'.join(lines), encoding='utf-8')

import py_compile
try:
    py_compile.compile(str(f), doraise=True)
    print('✅✅✅ main.py валиден! ✅✅✅')
except py_compile.PyCompileError as e:
    print(f'❌ Ошибка: {e}')