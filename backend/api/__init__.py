from fastapi import APIRouter

from . import (
    auth,
)


router = APIRouter(
    prefix="/api_library"
)

router.include_router(auth.router)
