from fastapi import APIRouter

from . import auth, user, messages, contacts, chats, chat_members, data


router = APIRouter(
    prefix="/api"
)

router.include_router(auth.router)
router.include_router(contacts.router)
router.include_router(chats.router)
router.include_router(chat_members.router)
router.include_router(data.router)
router.include_router(messages.router)
router.include_router(user.router)
