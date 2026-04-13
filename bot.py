
import globals

import urllib.parse
import hashlib
import random
import string
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineQueryResultAudio
from aiogram.exceptions import TelegramBadRequest


dp = Dispatcher()
bot = Bot(token=globals.TELEGRAM_BOT_TOKEN)


def generate_token() -> tuple[str, str, str]:  # (username, token, salt)
    salt = "".join(random.choices(string.ascii_letters + string.digits, k=6))
    auth_string = globals.OSS_PASSWORD + salt
    token = hashlib.md5(auth_string.encode("utf-8")).hexdigest()

    return globals.OSS_USERNAME, token, salt


async def start_polling():
    await dp.start_polling(bot, allowed_updates=[])


@dp.inline_query()
async def handle_inline(query: types.InlineQuery):
    query_text = query.query.strip()
    if not query_text:
        return

    username, token, salt = generate_token()

    base_params = {
        "u": username,
        "t": token,
        "s": salt,
        "c": "OSS_TG_BOT",
        "v": "1.16.1",
        "f": "json",
    }

    params = {
        "query": query_text.lower(),
        "artistCount": 0,
        "albumCount": 0,
        "songCount": 50,
    }
    params = params | base_params

    if not globals.GLOBAL_SEMAPHORE or not globals.GLOBAL_SESSION:
        return

    async with globals.GLOBAL_SEMAPHORE:
        async with globals.GLOBAL_SESSION.get(
            url=f"{globals.OSS_URL}/rest/search3", params=params
        ) as response:
            response.raise_for_status()
            data = await response.json()

    subsonic_response = data.get("subsonic-response", {})
    subsonic_response_status = subsonic_response.get("status", "unknown")

    if subsonic_response_status != "ok":
        print(f"Subsonic API returned status: {subsonic_response_status}")
        return

    search3_result = subsonic_response.get("searchResult3", {})
    songs = search3_result.get("song", [])

    inline_results = []

    for song in songs:
        title = song.get("title", "Unknown Title")
        artists = song.get("artist", "Unknown Artist")
        duration = song.get("duration", 0)
        song_id = song.get("id", "")
        cover_id = song.get("coverArt", "")

        song_params = base_params | {"id": song_id, "format": "mp3", "maxBitRate": 320}
        song_query = urllib.parse.urlencode(song_params)
        song_url = f"{globals.OSS_URL}/rest/stream?{song_query}"

        cover_params = base_params | {"id": cover_id}
        cover_query = urllib.parse.urlencode(cover_params)
        cover_url = f"{globals.OSS_URL}/rest/getCoverArt?{cover_query}"

        result = InlineQueryResultAudio(
            id=song_id,
            title=title,
            performer=artists,
            audio_url=song_url,
            thumbnail_url=cover_url,
            duration=duration,
        )
        inline_results.append(result)

    try:
        await query.answer(inline_results, cache_time=300)
    except TelegramBadRequest as e:
        print(e)
        pass
