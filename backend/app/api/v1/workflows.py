from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db, Base, engine
from core.repositories.workflow_repository import WorkflowRepository
from .schemas import WorkflowCreateRequest, WorkflowResponse, WorkflowListResponse

Base.metadata.create_all(bind=engine)

router = APIRouter(prefix="/workflows", tags=["workflows"])


def _to_response(item) -> WorkflowResponse:
    from datetime import datetime
    return WorkflowResponse(
        id=item.id,
        name=item.name,
        description=item.description,
        definition=item.definition,
        is_active=item.is_active,
        created_at=item.created_at or datetime.utcnow(),
        updated_at=item.updated_at or datetime.utcnow(),
    )


@router.get("/", response_model=WorkflowListResponse)
async def list_workflows(db: Session = Depends(get_db)):
    repo = WorkflowRepository(db)
    items = repo.list_all()
    if not items:
        default_definition = {
            "id": "telegram-default",
            "name": "Telegram Research to Publish",
            "description": "Research -> Decision -> Writing -> Fact Check -> Image -> Review -> Telegram",
            "nodes": [
                {"id": "research", "type": "research", "config": {}, "status": "pending", "output": None},
                {"id": "decision", "type": "decision", "config": {}, "status": "pending", "output": None},
                {"id": "writing", "type": "brief", "config": {}, "status": "pending", "output": None},
                {"id": "fact_check", "type": "fact_checker", "config": {}, "status": "pending", "output": None},
                {"id": "image", "type": "image", "config": {}, "status": "pending", "output": None},
                {"id": "review", "type": "evaluator", "config": {}, "status": "pending", "output": None},
                {"id": "publisher", "type": "publisher", "config": {}, "status": "pending", "output": None},
            ],
            "edges": [
                {"source_node_id": "research", "target_node_id": "decision"},
                {"source_node_id": "decision", "target_node_id": "writing"},
                {"source_node_id": "writing", "target_node_id": "fact_check"},
                {"source_node_id": "fact_check", "target_node_id": "image"},
                {"source_node_id": "image", "target_node_id": "review"},
                {"source_node_id": "review", "target_node_id": "publisher"},
            ],
            "is_active": True,
        }
        repo.create(
            name="Telegram Research to Publish",
            description="Research -> Decision -> Writing -> Fact Check -> Image -> Review -> Telegram",
            definition=default_definition,
            is_active=True,
        )
        items = repo.list_all()

    return WorkflowListResponse(total=len(items), items=[_to_response(item) for item in items])


@router.post("/", response_model=WorkflowResponse, status_code=201)
async def create_workflow(request: WorkflowCreateRequest, db: Session = Depends(get_db)):
    repo = WorkflowRepository(db)
    existing = repo.get_by_name(request.name)
    if existing:
        raise HTTPException(status_code=400, detail="Workflow with this name already exists")

    item = repo.create(
        name=request.name,
        description=request.description,
        definition=request.definition,
        is_active=request.is_active,
    )
    return _to_response(item)


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: str, db: Session = Depends(get_db)):
    repo = WorkflowRepository(db)
    item = repo.get(workflow_id)
    if not item:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return _to_response(item)


@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(workflow_id: str, request: WorkflowCreateRequest, db: Session = Depends(get_db)):
    repo = WorkflowRepository(db)
    item = repo.update(
        workflow_id,
        name=request.name,
        description=request.description,
        definition=request.definition,
        is_active=request.is_active,
    )
    if not item:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return _to_response(item)


@router.delete("/{workflow_id}", status_code=204)
async def delete_workflow(workflow_id: str, db: Session = Depends(get_db)):
    repo = WorkflowRepository(db)
    if not repo.delete(workflow_id):
        raise HTTPException(status_code=404, detail="Workflow not found")
