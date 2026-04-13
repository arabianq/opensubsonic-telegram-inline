import os

from aiohttp import ClientSession
from asyncio import Semaphore


GLOBAL_SESSION:     ClientSession   | None = None
GLOBAL_SEMAPHORE:   Semaphore       | None = None

TELEGRAM_BOT_TOKEN: str = os.environ["TELEGRAM_BOT_TOKEN"]

OSS_URL:        str = os.environ["OSS_URL"].rstrip("/")
OSS_USERNAME:   str = os.environ["OSS_USERNAME"]
OSS_PASSWORD:   str = os.environ["OSS_PASSWORD"]

SESSION_TIMEOUT: int = int(os.getenv("SESSION_TIMEOUT", "15"))
MAX_REQUESTS:    int = int(os.getenv("MAX_REQUESTS", "50"))
