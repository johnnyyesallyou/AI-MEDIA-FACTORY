import pathlib

p = pathlib.Path("/app/core/models/__init__.py")
c = p.read_text(encoding="utf-8")

if "ChannelProfileORM" not in c:
    c = c.replace(
        "from core.models.channel_template_orm import ChannelTemplateORM  # Sprint 52",
        "from core.models.channel_template_orm import ChannelTemplateORM  # Sprint 52\nfrom core.models.channel_profile_orm import ChannelProfileORM  # Sprint 52",
    )
    
    c = c.replace(
        '    "ChannelTemplateORM",  # Sprint 52',
        '    "ChannelTemplateORM",  # Sprint 52\n    "ChannelProfileORM",  # Sprint 52',
    )
    
    p.write_text(c, encoding="utf-8")
    print("[OK] Добавлен импорт ChannelProfileORM в core/models/__init__.py")
else:
    print("[i] ChannelProfileORM уже импортируется")

# Проверка
print("\nСодержимое __init__.py:")
print(p.read_text(encoding="utf-8"))