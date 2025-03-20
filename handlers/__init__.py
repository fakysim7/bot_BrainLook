# handlers/__init__.py
from aiogram import Router
from handlers.start import router as start_router
from handlers.events import router as events_router
from .messages import messages_router
from .account import account_router

router = Router()
router.include_router(start_router)
router.include_router(events_router)
router.include_router(messages_router)
router.include_router(account_router)


