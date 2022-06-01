from fastapi import APIRouter

from . import auth, user, messages, contact


router = APIRouter(
    prefix="/api"
)

router.include_router(auth.router)
router.include_router(contact.router)
router.include_router(messages.router)
router.include_router(user.router)
