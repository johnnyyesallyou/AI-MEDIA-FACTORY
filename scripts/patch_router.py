import pathlib

p = pathlib.Path('./backend/app/api/v1/router.py')
s = p.read_text(encoding='utf-8')
changes = []

# Проверяем, не зарегистрирован ли уже
if 'automation_v2' in s:
    print('ℹ️ automation_v2 уже зарегистрирован')
else:
    # Добавляем импорт
    if 'from .automation import router as automation_router' in s:
        s = s.replace(
            'from .automation import router as automation_router',
            'from .automation import router as automation_router\nfrom .automation_v2 import router as automation_v2_router'
        )
        changes.append('added import')
    
    # Регистрируем router
    if 'api_v1_router.include_router(automation_router)' in s:
        s = s.replace(
            'api_v1_router.include_router(automation_router)',
            'api_v1_router.include_router(automation_router)\napi_v1_router.include_router(automation_v2_router)'
        )
        changes.append('registered router')
    
    if changes:
        p.write_text(s, encoding='utf-8')
        print(f'✅ Применены: {", ".join(changes)}')
    else:
        print('⚠️ Не удалось применить патчи')