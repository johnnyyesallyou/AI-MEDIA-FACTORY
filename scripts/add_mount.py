import pathlib, py_compile

f = pathlib.Path('./backend/main.py')
s = f.read_text(encoding='utf-8')

# Проверяем есть ли уже mount для assets
if '"/assets"' in s or "'/assets'" in s:
    print("ℹ️ Mount для /assets уже есть")
else:
    # Добавляем импорт StaticFiles
    if 'from fastapi.staticfiles import StaticFiles' not in s:
        s = s.replace(
            'from fastapi import FastAPI',
            'from fastapi import FastAPI\nfrom fastapi.staticfiles import StaticFiles',
            1
        )
        print("✅ Добавлен импорт StaticFiles")
    
    # Добавляем mount после создания app
    # Ищем "app = FastAPI(" и вставляем mount после
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
            print(f"✅ Добавлен app.mount('/assets') после строки {j+1}")
            break

try:
    py_compile.compile(str(f), doraise=True)
    print("✅✅✅ main.py валиден! ✅✅✅")
except py_compile.PyCompileError as e:
    print(f"❌ Ошибка: {e}")