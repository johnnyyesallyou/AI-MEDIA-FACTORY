import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session

from core.models.workflow_orm import WorkflowORM


class WorkflowRepository:
    """Repository для data-driven workflow definitions."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, **fields) -> WorkflowORM:
        item = WorkflowORM(id=str(uuid.uuid4()), **fields)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def get(self, workflow_id: str) -> Optional[WorkflowORM]:
        return self.db.query(WorkflowORM).filter(WorkflowORM.id == workflow_id).first()

    def get_by_name(self, name: str) -> Optional[WorkflowORM]:
        return self.db.query(WorkflowORM).filter(WorkflowORM.name == name).first()

    def list_all(self) -> List[WorkflowORM]:
        return self.db.query(WorkflowORM).order_by(WorkflowORM.created_at.desc()).all()

    def update(self, workflow_id: str, **fields) -> Optional[WorkflowORM]:
        item = self.get(workflow_id)
        if not item:
            return None
        for key, value in fields.items():
            if value is not None:
                setattr(item, key, value)
        item.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete(self, workflow_id: str) -> bool:
        item = self.get(workflow_id)
        if not item:
            return False
        self.db.delete(item)
        self.db.commit()
        return True
