from fastapi import APIRouter
from .channels import router as channels_router

api_v1_router = APIRouter(prefix="/api/v1")

# Подключаем все роуты
api_v1_router.include_router(channels_router)

# В будущем добавим:
# from .content import router as content_router
# from .ai import router as ai_router
# from .automation import router as automation_router
# from .analytics import router as analytics_router
# api_v1_router.include_router(content_router)
# api_v1_router.include_router(ai_router)
# api_v1_router.include_router(automation_router)
# api_v1_router.include_router(analytics_router)
