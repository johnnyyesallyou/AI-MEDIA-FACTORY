import pathlib

p = pathlib.Path("/app/backend/app/api/v1/channels.py")
c = p.read_text(encoding="utf-8")

# Убираем template_id=template_id из ChannelORM creation
old = '''        is_active=True,
        template_id=template_id,
        sources=[],'''

new = '''        is_active=True,
        sources=[],'''

if old in c:
    c = c.replace(old, new, 1)
    p.write_text(c, encoding="utf-8")
    print("[OK] template_id убран из ChannelORM creation (FK violation fix)")
else:
    print("[i] Паттерн не найден")