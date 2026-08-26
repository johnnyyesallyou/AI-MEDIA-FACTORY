import sys
sys.path.insert(0, '/app')

from core.database import SessionLocal
from core.models.channel_orm import ChannelORM

db = SessionLocal()

# Назначаем workflows
assignments = [
    ("Манга — новые главы", "wf-manga"),
    ("AI Anime News", "wf-anime"),
    ("АИ Новости", "wf-news"),
]

for channel_name, workflow_id in assignments:
    ch = db.query(ChannelORM).filter(ChannelORM.name == channel_name).first()
    if ch:
        ch.workflow_id = workflow_id
        print(f"[OK] {channel_name!r:35} -> {workflow_id}")
    else:
        print(f"[!] {channel_name!r:35} NOT FOUND")

db.commit()
db.close()
print("[OK] Workflows assigned to channels")