from typing import Callable, Awaitable, Any

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject

from backend.bot.config.db_conf import ADMIN_ID


class AdminMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict], Awaitable[Any]],
        event: TelegramObject,
        data: dict,
    ) -> Any:

        user_id = None

        if isinstance(event, Message):
            user_id = event.from_user.id

        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id

        if user_id != ADMIN_ID:
            if isinstance(event, CallbackQuery):
                await event.answer(
                    "⛔️ شما دسترسی به این بخش ندارید.",
                    show_alert=True,
                )
            elif isinstance(event, Message):
                await event.answer("⛔️ شما دسترسی به این بخش ندارید.")
            return

        return await handler(event, data)
