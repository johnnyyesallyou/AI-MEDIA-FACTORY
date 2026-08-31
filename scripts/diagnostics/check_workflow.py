import sys, os
sys.path.insert(0, '.')
from backend.database import SessionLocal
from core.models.workflow_orm import WorkflowORM

db = SessionLocal()
wf = db.query(WorkflowORM).filter(WorkflowORM.id == "wf-simple").first()
if wf:
    import json
    print(f"Workflow: {wf.name} (id={wf.id})")
    print(f"Definition type: {type(wf.definition)}")
    print("\nDefinition:")
    print(json.dumps(wf.definition, indent=2, ensure_ascii=False))
else:
    print("❌ Workflow 'wf-simple' не найден")
db.close()