import pathlib

p = pathlib.Path("/app/backend/app/api/v1/router.py")
c = p.read_text(encoding="utf-8")

if "channel_control_router" not in c:
    c = c.replace(
        "from .wizard import router as wizard_router",
        "from .wizard import router as wizard_router\nfrom .channel_control import router as channel_control_router",
    )
    
    c = c.replace(
        "api_v1_router.include_router(wizard_router)",
        "api_v1_router.include_router(wizard_router)\napi_v1_router.include_router(channel_control_router)",
    )
    
    p.write_text(c, encoding="utf-8")
    print("[OK] channel_control_router зарегистрирован")
else:
    print("[i] уже зарегистрирован")