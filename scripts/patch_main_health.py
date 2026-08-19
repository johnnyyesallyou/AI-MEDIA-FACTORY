import pathlib

p = pathlib.Path("/app/main.py")
c = p.read_text(encoding="utf-8")

if "health_unified" not in c:
    # Импорт
    c = c.replace(
        "from backend.app.api.v1 import metrics",
        "from backend.app.api.v1 import metrics, health as health_router",
        1
    )
    
    # Регистрация
    c = c.replace(
        "app.include_router(metrics.router)",
        "app.include_router(metrics.router)\napp.include_router(health_router.router)",
        1
    )
    
    p.write_text(c, encoding="utf-8")
    print("[OK] Health router registered")
else:
    print("[i] Already registered")