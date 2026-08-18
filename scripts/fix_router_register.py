import pathlib, py_compile

f = pathlib.Path('backend/app/api/v1/router.py')
s = f.read_text(encoding='utf-8')

# Проверяем есть ли уже регистрация
if 'api_v1_router.include_router(monitoring_router' in s:
    print('  ℹ️ monitoring_router уже зарегистрирован')
else:
    # Вставляем регистрацию сразу после dashboard_router (первая include_router строка)
    s = s.replace(
        'api_v1_router.include_router(dashboard_router)',
        'api_v1_router.include_router(monitoring_router)\napi_v1_router.include_router(dashboard_router)',
        1
    )
    print('  ✅ Добавлен api_v1_router.include_router(monitoring_router)')
    f.write_text(s, encoding='utf-8')

try:
    py_compile.compile(str(f), doraise=True)
    print('  ✅✅✅ router.py валиден')
except py_compile.PyCompileError as e:
    print(f'  ❌ Ошибка: {e}')