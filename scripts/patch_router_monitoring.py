import pathlib

f = pathlib.Path('backend/app/api/v1/router.py')
s = f.read_text(encoding='utf-8')

# Добавляем импорт monitoring router
if 'from .monitoring import router as monitoring_router' not in s:
    s = s.replace(
        'from fastapi import APIRouter',
        'from fastapi import APIRouter\nfrom .monitoring import router as monitoring_router'
    )
    print('  Added monitoring router import')

# Добавляем в include_router
if 'api_router.include_router(monitoring_router' not in s:
    # Находим последний include_router и добавляем после него
    last_include = s.rfind('api_router.include_router(')
    if last_include != -1:
        # Находим конец строки
        end_line = s.find('\n', last_include)
        insert_pos = end_line + 1
        new_line = 'api_router.include_router(monitoring_router, prefix="/api/v1", tags=["monitoring"])\n'
        s = s[:insert_pos] + new_line + s[insert_pos:]
        print('  Added monitoring_router to api_router')

f.write_text(s, encoding='utf-8')

import py_compile
try:
    py_compile.compile(str(f), doraise=True)
    print('  ✅ router.py валиден')
except py_compile.PyCompileError as e:
    print(f'  ❌ {e}')