import pathlib

p = pathlib.Path("/app/backend/app/api/v1/router.py")
c = p.read_text(encoding="utf-8")

if "wizard_router" not in c:
    # Добавляем импорт
    c = c.replace(
        "from .sources import router as sources_router",
        "from .sources import router as sources_router\nfrom .wizard import router as wizard_router",
    )
    
    # Регистрируем router
    c = c.replace(
        "api_v1_router.include_router(sources_router)",
        "api_v1_router.include_router(sources_router)\napi_v1_router.include_router(wizard_router)",
    )
    
    p.write_text(c, encoding="utf-8")
    print("[OK] wizard_router зарегистрирован")
else:
    print("[i] wizard_router уже зарегистрирован")