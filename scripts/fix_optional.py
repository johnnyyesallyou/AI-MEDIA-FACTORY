import pathlib

p = pathlib.Path("./backend/app/api/v1/channels.py")
c = p.read_text(encoding="utf-8")

# Заменяем Optional[str] = None на str = None в сигнатуре from-template
old = '''async def create_channel_from_template(
    template_id: str,
    custom_name: Optional[str] = None,
    db: Session = Depends(get_db)'''

new = '''async def create_channel_from_template(
    template_id: str,
    custom_name: str = None,
    db: Session = Depends(get_db)'''

if old in c:
    c = c.replace(old, new, 1)
    p.write_text(c, encoding="utf-8")
    print("[OK] Optional заменён на str = None")
else:
    print("[i] Паттерн не найден или уже исправлен")