from aiogram import Bot, Dispatcher

from backend.bot.config.db_conf import TOKEN
from backend.bot.handlers import routers

bot = Bot(token=TOKEN)
dp = Dispatcher()


async def main():
    for router in routers:
        dp.include_router(router)

    try:
        await dp.start_polling(bot)

    except Exception as e:
        print(f"Error in bot polling: {e}")

    finally:
        await bot.session.close()
