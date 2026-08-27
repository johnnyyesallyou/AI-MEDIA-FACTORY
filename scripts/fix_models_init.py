import pathlib

p = pathlib.Path("/app/core/models/__init__.py")
c = p.read_text(encoding="utf-8")

# Добавляем импорт ChannelTemplateORM
if "ChannelTemplateORM" not in c:
    # Добавляем в импорты
    c = c.replace(
        "from core.models.asset_orm import AssetORM  # Sprint 11",
        "from core.models.asset_orm import AssetORM  # Sprint 11\nfrom core.models.channel_template_orm import ChannelTemplateORM  # Sprint 52",
    )
    
    # Добавляем в __all__
    c = c.replace(
        '    "AssetORM",  # Sprint 11',
        '    "AssetORM",  # Sprint 11\n    "ChannelTemplateORM",  # Sprint 52',
    )
    
    p.write_text(c, encoding="utf-8")
    print("[OK] Добавлен импорт ChannelTemplateORM в core/models/__init__.py")
else:
    print("[i] ChannelTemplateORM уже импортируется")