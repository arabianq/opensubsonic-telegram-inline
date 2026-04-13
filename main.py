import dotenv
import logging
import asyncio

from aiohttp import ClientSession, ClientTimeout
from asyncio import Semaphore


async def main():
    dotenv.load_dotenv()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    import globals
    import bot

    globals.GLOBAL_SESSION = ClientSession(
        timeout=ClientTimeout(total=globals.SESSION_TIMEOUT)
    )
    globals.GLOBAL_SEMAPHORE = Semaphore(globals.MAX_REQUESTS)

    await bot.start_polling()


if __name__ == "__main__":
    asyncio.run(main())
