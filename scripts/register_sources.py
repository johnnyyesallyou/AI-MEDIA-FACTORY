import pathlib

p = pathlib.Path("/app/backend/app/api/v1/router.py")
c = p.read_text(encoding="utf-8")

if "sources_router" not in c:
    # Добавляем импорт
    c = c.replace(
        "from .templates import profiles_router, templates_router",
        "from .templates import profiles_router, templates_router\nfrom .sources import router as sources_router",
    )
    
    # Регистрируем router
    c = c.replace(
        "api_v1_router.include_router(profiles_router)",
        "api_v1_router.include_router(profiles_router)\napi_v1_router.include_router(sources_router)",
    )
    
    p.write_text(c, encoding="utf-8")
    print("[OK] sources_router зарегистрирован")
else:
    print("[i] sources_router уже зарегистрирован")