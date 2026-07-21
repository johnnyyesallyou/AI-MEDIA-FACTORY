from fastapi import APIRouter, Query, UploadFile, File
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import uuid4
from datetime import datetime

router = APIRouter(prefix="/assets", tags=["assets"])

# === МОДЕЛИ ===

class AssetItem(BaseModel):
    id: str
    name: str
    asset_type: str # image, video, font, logo, lora, workflow
    url: str
    size_kb: int
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AssetListResponse(BaseModel):
    total: int
    items: List[AssetItem]

# === ЗАГЛУШКИ ДАННЫХ ===
_assets_db = [
    AssetItem(id="1", name="cyberpunk_city.png", asset_type="image", url="/static/assets/cyberpunk_city.png", size_kb=1200),
    AssetItem(id="2", name="sd_xl_base_v1.safetensors", asset_type="lora", url="/static/assets/sd_xl_base_v1.safetensors", size_kb=6500000),
    AssetItem(id="3", name="news_workflow.json", asset_type="workflow", url="/static/assets/news_workflow.json", size_kb=45)
]

# === ENDPOINTS ===

@router.get("/", response_model=AssetListResponse)
async def list_assets(asset_type: Optional[str] = Query(None, description="Фильтр по типу: image, video, font, logo, lora, workflow")):
    '''Получить список всех ассетов (изображения, LoRA, ComfyUI Workflows).'''
    items = _assets_db
    if asset_type:
        items = [item for item in items if item.asset_type == asset_type]
    return AssetListResponse(total=len(items), items=items)

@router.post("/upload")
async def upload_asset(file: UploadFile = File(...), asset_type: str = Query(...)):
    '''Загрузить новый ассет (изображение, LoRA, шрифт и т.д.).'''
    # В реальности здесь будет загрузка в MinIO
    new_asset = AssetItem(
        id=str(uuid4()),
        name=file.filename,
        asset_type=asset_type,
        url=f"/static/assets/{file.filename}",
        size_kb=1024 # Заглушка
    )
    _assets_db.append(new_asset)
    return {"message": "Asset uploaded successfully", "asset": new_asset}
