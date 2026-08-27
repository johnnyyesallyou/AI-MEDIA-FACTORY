import pathlib

p = pathlib.Path("/app/core/models/__init__.py")
c = p.read_text(encoding="utf-8")

if "PostHistoryORM" not in c:
    c = c.replace(
        "from core.models.channel_profile_orm import ChannelProfileORM  # Sprint 52",
        "from core.models.channel_profile_orm import ChannelProfileORM  # Sprint 52\nfrom core.models.post_history_orm import PostHistoryORM, PostMetricsORM, ChannelLearningsORM  # Sprint 57",
    )
    
    c = c.replace(
        '    "ChannelProfileORM",  # Sprint 52',
        '    "ChannelProfileORM",  # Sprint 52\n    "PostHistoryORM",\n    "PostMetricsORM",\n    "ChannelLearningsORM",  # Sprint 57',
    )
    
    p.write_text(c, encoding="utf-8")
    print("[OK] Post History ORM импортирован")
else:
    print("[i] Уже импортирован")