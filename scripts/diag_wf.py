import sys
sys.path.insert(0, '/app')
from core.database import SessionLocal
from core.models.channel_orm import ChannelORM

db = SessionLocal()
try:
    for ch in db.query(ChannelORM).all():
        print(f"{ch.name!r}: workflow_id={ch.workflow_id!r} profile_id={getattr(ch, 'profile_id', None)!r}")
finally:
    db.close()

# дамп workflow definitions
try:
    from core.models.workflow_orm import WorkflowORM
    db = SessionLocal()
    try:
        cols = [c.name for c in WorkflowORM.__table__.columns]
        print("\nWorkflowORM columns:", cols)
        for w in db.query(WorkflowORM).all():
            print(f"\nworkflow: id={w.id} name={getattr(w, 'name', '?')}")
            for col in cols:
                if col in ('definition', 'nodes', 'steps', 'config', 'graph'):
                    val = getattr(w, col)
                    print(f"  {col}: {str(val)[:400]}")
    finally:
        db.close()
except Exception as e:
    print("workflow dump error:", e)