from fastapi import APIRouter
from .auth import auth
from .languages import languages
from .voice_samples import voice_samples
from .users import users
from .meeting import meeting

router = APIRouter(prefix='/api')

router.include_router(auth.router)
router.include_router(languages.router)
router.include_router(voice_samples.router)
router.include_router(users.router)
router.include_router(meeting.router)
