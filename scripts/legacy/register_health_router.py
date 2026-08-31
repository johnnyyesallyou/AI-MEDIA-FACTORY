import pathlib, py_compile, re

main_file = pathlib.Path('./backend/main.py')
if not main_file.exists():
    main_file = pathlib.Path('./main.py')

s = main_file.read_text(encoding='utf-8')

# Проверяем есть ли уже импорт health_router
if 'health_router' not in s:
    # Ищем место где регистрируются другие routers
    # Обычно это что-то вроде: app.include_router(api_v1_router, prefix="/api/v1")
    
    # Добавляем импорт
    if 'from backend.app.api.v1.router import api_v1_router' in s:
        s = s.replace(
            'from backend.app.api.v1.router import api_v1_router',
            'from backend.app.api.v1.router import api_v1_router\nfrom backend.app.api.v1.health import router as health_router',
            1
        )
    
    # Добавляем регистрацию ПОСЛЕ api_v1_router
    # Ищем строку где регистрируется api_v1_router
    pattern = r'app\.include_router\(api_v1_router[^)]*\)'
    match = re.search(pattern, s)
    if match:
        insert_point = match.end()
        new_line = '\n    app.include_router(health_router, prefix="/api/v1")'
        s = s[:insert_point] + new_line + s[insert_point:]
        print("✅ Добавлен health_router в main.py")
    
    main_file.write_text(s, encoding='utf-8')
else:
    print("ℹ️ health_router уже есть в main.py")

try:
    py_compile.compile(str(main_file), doraise=True)
    print("✅✅✅ main.py валиден! ✅✅✅")
except py_compile.PyCompileError as e:
    print(f"❌ Ошибка: {e}")