from fastapi import APIRouter
from .channels import router as channels_router
from .dashboard import router as dashboard_router
from .content import router as content_router

api_v1_router = APIRouter(prefix="/api/v1")

# Подключаем все роуты по порядку
api_v1_router.include_router(dashboard_router)
api_v1_router.include_router(channels_router)
api_v1_router.include_router(content_router)

# В следующих шагах добавим:
# from .ai import router as ai_router
# from .automation import router as automation_router
# api_v1_router.include_router(ai_router)
# api_v1_router.include_router(automation_router)
