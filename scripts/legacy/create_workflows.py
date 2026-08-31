import sys, uuid
sys.path.insert(0, '/app')

from core.database import SessionLocal
from core.models.workflow_orm import WorkflowORM

db = SessionLocal()

# 1. wf-manga: manga_research → manga_enrichment → manga_publish
manga_def = {
    "id": "wf-manga",
    "name": "Manga Pipeline",
    "description": "Research → Enrichment → Publish (с обложкой, Telegraph, кнопками)",
    "nodes": [
        {"id": "manga_research", "type": "manga_research", "config": {}, "status": "pending", "output": None},
        {"id": "manga_enrichment", "type": "manga_enrichment", "config": {}, "status": "pending", "output": None},
        {"id": "manga_publish", "type": "manga_publish", "config": {}, "status": "pending", "output": None},
    ],
    "edges": [
        {"source_node_id": "manga_research", "target_node_id": "manga_enrichment"},
        {"source_node_id": "manga_enrichment", "target_node_id": "manga_publish"},
    ],
}

# 2. wf-anime: anime_research → anime_publish
anime_def = {
    "id": "wf-anime",
    "name": "Anime Pipeline",
    "description": "Research → Publish (с key visual, Telegraph, кнопками)",
    "nodes": [
        {"id": "anime_research", "type": "anime_research", "config": {}, "status": "pending", "output": None},
        {"id": "anime_publish", "type": "anime_publish", "config": {}, "status": "pending", "output": None},
    ],
    "edges": [
        {"source_node_id": "anime_research", "target_node_id": "anime_publish"},
    ],
}

# 3. wf-news: research → writing → evaluation → publish (generic для новостей)
news_def = {
    "id": "wf-news",
    "name": "News Pipeline",
    "description": "Research → Writing → Evaluation → Publish (generic)",
    "nodes": [
        {"id": "research", "type": "research", "config": {}, "status": "pending", "output": None},
        {"id": "writing", "type": "writing", "config": {}, "status": "pending", "output": None},
        {"id": "evaluation", "type": "evaluation", "config": {}, "status": "pending", "output": None},
        {"id": "publish", "type": "publish", "config": {}, "status": "pending", "output": None},
    ],
    "edges": [
        {"source_node_id": "research", "target_node_id": "writing"},
        {"source_node_id": "writing", "target_node_id": "evaluation"},
        {"source_node_id": "evaluation", "target_node_id": "publish"},
    ],
}

# Создаём workflows
for wf_id, wf_def in [("wf-manga", manga_def), ("wf-anime", anime_def), ("wf-news", news_def)]:
    existing = db.query(WorkflowORM).filter(WorkflowORM.id == wf_id).first()
    if existing:
        existing.definition = wf_def
        print(f"[OK] Updated workflow {wf_id}")
    else:
        wf = WorkflowORM(
            id=wf_id,
            name=wf_def["name"],
            description=wf_def["description"],
            definition=wf_def,
            is_active=True,
        )
        db.add(wf)
        print(f"[OK] Created workflow {wf_id}")

db.commit()
db.close()
print("[OK] Specialized workflows created/updated")