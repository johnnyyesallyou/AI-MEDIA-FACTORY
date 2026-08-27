from fastapi import APIRouter
from .monitoring import router as monitoring_router
from .dashboard import router as dashboard_router
from .channels import router as channels_router
from .research import router as research_router, content_router as writing_router
from .content import router as content_router
from .ai import router as ai_router
from .templates import profiles_router, templates_router
from .sources import router as sources_router
from .wizard import router as wizard_router
from .channel_control import router as channel_control_router
from .automation import router as automation_router
from .automation_v2 import router as automation_v2_router
from .analytics import router as analytics_router
from .knowledge import router as knowledge_router
from .assets import router as assets_router
from .integrations import router as integrations_router
from .logs import router as logs_router
from .users import router as users_router
from .settings import router as settings_router
from .workflows import router as workflows_router
from .health import router as health_router

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(monitoring_router)
api_v1_router.include_router(dashboard_router)
api_v1_router.include_router(channels_router)
api_v1_router.include_router(research_router)
api_v1_router.include_router(writing_router)
api_v1_router.include_router(content_router)
api_v1_router.include_router(ai_router)
api_v1_router.include_router(profiles_router)
api_v1_router.include_router(sources_router)
api_v1_router.include_router(wizard_router)
api_v1_router.include_router(channel_control_router)
api_v1_router.include_router(templates_router)
api_v1_router.include_router(automation_router)
api_v1_router.include_router(automation_v2_router)
api_v1_router.include_router(analytics_router)
api_v1_router.include_router(knowledge_router)
api_v1_router.include_router(assets_router)
api_v1_router.include_router(integrations_router)
api_v1_router.include_router(logs_router)
api_v1_router.include_router(users_router)
api_v1_router.include_router(settings_router)
api_v1_router.include_router(workflows_router)
api_v1_router.include_router(health_router)


