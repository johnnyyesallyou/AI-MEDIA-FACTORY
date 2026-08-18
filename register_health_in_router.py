import pathlib, py_compile

f = pathlib.Path('./backend/app/api/v1/router.py')
s = f.read_text(encoding='utf-8')

# Проверяем есть ли уже include_router для health
if 'include_router(health_router)' in s:
    print("ℹ️ health_router уже зарегистрирован")
else:
    # Добавляем после workflows_router
    s = s.replace(
        'api_v1_router.include_router(workflows_router)',
        'api_v1_router.include_router(workflows_router)\napi_v1_router.include_router(health_router)',
        1
    )
    f.write_text(s, encoding='utf-8')
    print("✅ Добавлена строка: api_v1_router.include_router(health_router)")

try:
    py_compile.compile(str(f), doraise=True)
    print("✅✅✅ router.py валиден! ✅✅✅")
except py_compile.PyCompileError as e:
    print(f"❌ Ошибка: {e}")