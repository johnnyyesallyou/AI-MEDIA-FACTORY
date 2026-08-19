import pathlib

p = pathlib.Path("/app/backend/app/api/v1/channels.py")
c = p.read_text(encoding="utf-8")

old = '''async def delete_channel(channel_id: str, db: Session = Depends(get_db)):
    repo = ChannelRepository(db)
    if not repo.delete(channel_id):
        raise HTTPException(status_code=404, detail="Channel not found")'''

new = '''async def delete_channel(channel_id: str, db: Session = Depends(get_db)):
    repo = ChannelRepository(db)
    if not repo.delete_cascade(channel_id):
        raise HTTPException(status_code=404, detail="Channel not found")'''

if old in c:
    c = c.replace(old, new, 1)
    p.write_text(c, encoding="utf-8")
    print("[OK] delete_channel -> delete_cascade")
elif new in c:
    print("[i] already fixed")
else:
    print("[?] delete_channel block not found, trying alternative")
    # Альтернатива: ищем по ключевым словам
    import re
    pattern = r'async def delete_channel\(channel_id: str[^)]*\):\s*repo = ChannelRepository\(db\)\s*if not repo\.delete\(channel_id\):'
    repl = 'async def delete_channel(channel_id: str, db: Session = Depends(get_db)):\n    repo = ChannelRepository(db)\n    if not repo.delete_cascade(channel_id):'
    c2, count = re.subn(pattern, repl, c)
    if count > 0:
        p.write_text(c2, encoding="utf-8")
        print(f"[OK] fixed via regex ({count} replacement(s))")
    else:
        print("[FAIL] could not fix delete_channel")