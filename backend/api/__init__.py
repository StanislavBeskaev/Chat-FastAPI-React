from fastapi import APIRouter

from . import auth, user, messages, contact, chats, chat_members


router = APIRouter(
    prefix="/api"
)

router.include_router(auth.router)
router.include_router(contact.router)
router.include_router(chats.router)
router.include_router(chat_members.router)
router.include_router(messages.router)
router.include_router(user.router)
