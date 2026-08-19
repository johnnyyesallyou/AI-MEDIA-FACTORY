import pathlib

f = pathlib.Path('./backend/app/api/v1/channels.py')
s = f.read_text(encoding='utf-8')

# Проверяем есть ли уже logger
if 'logger = logging.getLogger(__name__)' in s:
    print("ℹ️ logger уже определён в channels.py")
else:
    # Добавляем import logging и logger после других импортов
    # Ищем место после from fastapi import ...
    if 'from fastapi import APIRouter' in s and 'import logging' not in s:
        s = s.replace(
            'from fastapi import APIRouter',
            'import logging\nfrom fastapi import APIRouter',
            1
        )
        print("✅ Добавлен import logging")
    
    # Добавляем logger = logging.getLogger(__name__) после router = APIRouter(...)
    if 'logger = logging.getLogger' not in s:
        # Ищем router = APIRouter и вставляем после
        lines = s.split('\n')
        new_lines = []
        for i, line in enumerate(lines):
            new_lines.append(line)
            if 'router = APIRouter(' in line:
                new_lines.append('')
                new_lines.append('logger = logging.getLogger(__name__)')
                print("✅ Добавлен logger = logging.getLogger(__name__)")
                break
        
        # Продолжаем добавлять остальные строки
        for i in range(i+1, len(lines)):
            new_lines.append(lines[i])
        
        s = '\n'.join(new_lines)
        f.write_text(s, encoding='utf-8')

import py_compile
try:
    py_compile.compile(str(f), doraise=True)
    print("✅✅✅ channels.py валиден! ✅✅✅")
except py_compile.PyCompileError as e:
    print(f"❌ Ошибка: {e}")