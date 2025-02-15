from fastapi import APIRouter
from app.routers.auth import auth
from app.config import settings

router = APIRouter(prefix=f'/api/{settings.environment}')

router.include_router(auth.router)
