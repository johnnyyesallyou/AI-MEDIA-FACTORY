import pathlib

# Ищем главный файл приложения (main.py или app.py)
for filename in ['main.py', 'app.py']:
    f = pathlib.Path(f'./backend/app/{filename}')
    if f.exists():
        break
else:
    # Ищем в backend/
    for f in pathlib.Path('./backend').glob('*.py'):
        if 'FastAPI' in f.read_text(encoding='utf-8'):
            break

print(f'Найден главный файл: {f}')
s = f.read_text(encoding='utf-8')

# Проверяем есть ли уже StaticFiles
if 'StaticFiles' in s and 'assets' in s:
    print('ℹ️ StaticFiles уже добавлен')
else:
    # Добавляем импорт
    if 'from fastapi.staticfiles import StaticFiles' not in s:
        s = s.replace(
            'from fastapi import FastAPI',
            'from fastapi import FastAPI\nfrom fastapi.staticfiles import StaticFiles',
            1
        )
        print('✅ Добавлен импорт StaticFiles')
    
    # Добавляем mount после создания app
    if 'app.mount' not in s or 'assets' not in s:
        # Ищем "app = FastAPI(" и добавляем mount после
        if 'app = FastAPI(' in s:
            lines = s.split('\n')
            for i, line in enumerate(lines):
                if 'app = FastAPI(' in line:
                    # Находим конец блока app = FastAPI(...)
                    j = i
                    while j < len(lines) and ')' not in lines[j]:
                        j += 1
                    # Вставляем mount после
                    mount_code = '''

# Sprint 11: Serving generated assets
import os
os.makedirs("/app/assets", exist_ok=True)
app.mount("/assets", StaticFiles(directory="/app/assets"), name="assets")
'''
                    lines.insert(j+1, mount_code)
                    s = '\n'.join(lines)
                    f.write_text(s, encoding='utf-8')
                    print('✅ Добавлен app.mount("/assets")')
                    break

import py_compile
try:
    py_compile.compile(str(f), doraise=True)
    print("✅✅✅ main.py валиден! ✅✅✅")
except py_compile.PyCompileError as e:
    print(f"❌ Ошибка: {e}")