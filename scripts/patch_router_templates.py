import pathlib

p = pathlib.Path('./backend/app/api/v1/router.py')
s = p.read_text(encoding='utf-8')
changes = []

if 'templates_router' not in s:
    # Добавляем импорты
    if 'from .automation import router' in s:
        s = s.replace(
            'from .automation import router',
            'from .templates import profiles_router, templates_router\nfrom .automation import router',
            1
        )
        changes.append('added templates imports')
    
    # Регистрируем роутеры
    if 'api_v1_router.include_router(automation_router)' in s:
        s = s.replace(
            'api_v1_router.include_router(automation_router)',
            'api_v1_router.include_router(profiles_router)\napi_v1_router.include_router(templates_router)\napi_v1_router.include_router(automation_router)',
            1
        )
        changes.append('registered templates/profiles routers')
    
    if changes:
        p.write_text(s, encoding='utf-8')
        print(f'OK: применены фиксы:')
        for c in changes:
            print(f'   - {c}')
    else:
        print('⚠️ Не удалось применить')
else:
    print('ℹ️ Роутеры уже зарегистрированы')