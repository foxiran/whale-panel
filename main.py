import asyncio
import uvicorn

from backend.config import config
from backend.bot.config.db_conf import IS_ACTIVE as BOT_IS_ACTIVE


async def run_bot():
    if BOT_IS_ACTIVE:
        from backend.bot.run import main as bot_main

        await bot_main()


async def run_api():
    server = uvicorn.Server(
        uvicorn.Config(
            app="backend.app:app",
            host=config.HOST,
            port=config.PORT,
            ssl_keyfile=config.SSL_KEYFILE,
            ssl_certfile=config.SSL_CERTFILE,
            reload=False,
        )
    )

    await server.serve()


async def main():
    tasks = [asyncio.create_task(run_api())]

    if BOT_IS_ACTIVE:
        tasks.append(asyncio.create_task(run_bot()))

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
