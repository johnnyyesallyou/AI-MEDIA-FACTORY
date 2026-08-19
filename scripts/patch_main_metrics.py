import pathlib

p = pathlib.Path("/app/backend/app/main.py")
c = p.read_text(encoding="utf-8")

if "/metrics" not in c:
    c = c.replace(
        "from backend.app.api.v1 import research, health, monitoring",
        "from backend.app.api.v1 import research, health, monitoring, metrics",
    )
    c = c.replace(
        "app.include_router(monitoring.router)",
        "app.include_router(monitoring.router)\napp.include_router(metrics.router)",
    )
    p.write_text(c, encoding="utf-8")
    print("✅ /metrics endpoint registered")
else:
    print("ℹ️ /metrics already registered")