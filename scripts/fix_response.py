import pathlib

p = pathlib.Path("/app/backend/app/api/v1/channels.py")
c = p.read_text(encoding="utf-8")

old = '''    return ChannelResponse(
        id=channel.id,
        name=channel.name,
        platform=channel.platform,
        language_search=channel.language_search,
        language_publish=channel.language_publish,
        style_profile=channel.style_profile,
        timezone=channel.timezone,
        description=channel.description,
        is_active=channel.is_active,
        created_at=channel.created_at,
        updated_at=channel.updated_at,
    )'''

new = '''    return ChannelResponse(
        id=channel.id,
        name=channel.name,
        platform=channel.platform,
        language_search=channel.language_search,
        language_publish=channel.language_publish,
        style_profile=channel.style_profile,
        timezone=channel.timezone,
        description=channel.description,
        is_active=channel.is_active,
        is_connected=channel.is_connected if channel.is_connected is not None else False,
        sources=channel.sources if channel.sources is not None else [],
        created_at=channel.created_at,
        updated_at=channel.updated_at,
    )'''

if old in c:
    c = c.replace(old, new, 1)
    p.write_text(c, encoding="utf-8")
    print("[OK] Добавлены is_connected и sources в ChannelResponse")
else:
    print("[?] Паттерн не найден — ищем альтернативу")
    import re
    pattern = r'(return ChannelResponse\([^)]*is_active=channel\.is_active,)'
    repl = r'''\1
        is_connected=channel.is_connected if channel.is_connected is not None else False,
        sources=channel.sources if channel.sources is not None else [],'''
    c2, count = re.subn(pattern, repl, c, count=1, flags=re.DOTALL)
    if count > 0:
        p.write_text(c2, encoding="utf-8")
        print(f"[OK] Исправлено через regex ({count} replacement)")
    else:
        print("[FAIL] Не удалось применить фикс")