import pathlib

p = pathlib.Path("/app/backend/app/api/v1/router.py")
c = p.read_text(encoding="utf-8")

if "posts_router" not in c:
    c = c.replace(
        "from .channel_control import router as channel_control_router",
        "from .channel_control import router as channel_control_router\nfrom .posts import router as posts_router",
    )
    
    c = c.replace(
        "api_v1_router.include_router(channel_control_router)",
        "api_v1_router.include_router(channel_control_router)\napi_v1_router.include_router(posts_router)",
    )
    
    p.write_text(c, encoding="utf-8")
    print("[OK] posts_router зарегистрирован")
else:
    print("[i] Уже зарегистрирован")