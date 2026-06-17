from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart

from backend.bot.config.db_conf import ADMIN_ID
from backend.bot.keyboards.admin_keys import main_menu

r = Router()


@r.message(CommandStart())
async def start_handler(message: Message):
    try:
        if message.from_user.id == ADMIN_ID:
            await message.answer(
                "سلام ادمین عزیز! به پنل مدیریت خوش آمدید.", reply_markup=main_menu()
            )
    except:
        await message.answer("سلام! به ربات ما خوش آمدید.")
