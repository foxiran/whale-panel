from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart

from backend.bot.config.db_conf import ADMIN_ID
from backend.bot.keyboards.admin_keys import main_menu
from backend.db import crud
from backend.db.engin import sessionLocal

r = Router()


@r.message(CommandStart())
async def start_handler(message: Message):
    try:
        if message.from_user.id == ADMIN_ID:
            await message.answer(
                "سلام ادمین عزیز! به پنل مدیریت خوش آمدید.", reply_markup=main_menu()
            )
        else:
            db = sessionLocal()
            user = crud.get_user(db, message.from_user.id)
            if not user:
                crud.add_user(
                    db,
                    message.from_user.first_name,
                    message.from_user.id,
                    message.from_user.username,
                )
            setting = crud.get_all_settings(db)
            await message.answer(
                (
                    setting.start_message
                    if setting.start_message
                    else "سلام! به ربات ما خوش آمدید."
                ),
                reply_markup=main_menu(),
            )

    except Exception as e:
        print(f"Error in start handler: {e}")
        await message.answer(setting.start_message, reply_markup=main_menu())
