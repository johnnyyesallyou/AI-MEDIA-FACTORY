import pathlib

p = pathlib.Path("/app/main.py")
c = p.read_text(encoding="utf-8")

if "system_metrics" not in c:
    c = c.replace(
        "from backend.app.api.v1 import metrics, health as health_router",
        "from backend.app.api.v1 import metrics, health as health_router, system_metrics",
        1,
    )
    c = c.replace(
        "app.include_router(health_router.router)",
        "app.include_router(health_router.router)\napp.include_router(system_metrics.router)",
        1,
    )
    p.write_text(c, encoding="utf-8")
    print("[OK] system_metrics router registered")
else:
    print("[i] already registered")