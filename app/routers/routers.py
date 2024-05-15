from fastapi import APIRouter
from .auth import auth

router = APIRouter(prefix='/api')

router.include_router(auth.router)
