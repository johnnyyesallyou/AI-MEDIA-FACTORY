from fastapi import APIRouter
from .dashboard import router as dashboard_router
from .channels import router as channels_router
from .content import router as content_router
from .ai import router as ai_router
from .automation import router as automation_router
from .analytics import router as analytics_router
from .knowledge import router as knowledge_router
from .assets import router as assets_router
from .integrations import router as integrations_router
from .logs import router as logs_router

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(dashboard_router)
api_v1_router.include_router(channels_router)
api_v1_router.include_router(content_router)
api_v1_router.include_router(ai_router)
api_v1_router.include_router(automation_router)
api_v1_router.include_router(analytics_router)
api_v1_router.include_router(knowledge_router)
api_v1_router.include_router(assets_router)
api_v1_router.include_router(integrations_router)
api_v1_router.include_router(logs_router)
