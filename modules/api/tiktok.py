import asyncio
import json
#import logging
import random
import string
from datetime import datetime
from functools import wraps
from typing import AsyncIterator
import httpx
#from aiogram.types import Message
from attr import define, field
from bs4 import BeautifulSoup
from loguru import logger
from telegram import constants
from loguru import logger
import os

class Retrying(Exception):
    pass


def retries(times: int):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for _ in range(times):
                try:
                    return await func(*args, **kwargs)
                except Exception as ex:
                    logger.exception(ex)
                    await asyncio.sleep(0.5)
        return wrapper
    return decorator



async def handle_message(update, context):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=constants.ChatAction.UPLOAD_DOCUMENT)
    url = update.message.text.split(" ")[1]
    return await url

async def download_video(url: str) -> tuple[str, bytes]:

        async with httpx.AsyncClient(headers= {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}, timeout=30, cookies=_tt_webid_v2, follow_redirects=True) as client:   
            response = await client.get(url)
            page = await client.get(url, headers=_user_agent)
            page_id = page.url.path.rsplit('/', 1)[-1]

            soup = BeautifulSoup(page.text, 'html.parser')
            script_selector = 'script[id="SIGI_STATE"]'
            if script := soup.select_one(script_selector):
                script = json.loads(script.text)
            else:
                raise Retrying("no script")

            modules = tuple(script.get("ItemModule").values())
            if not modules:
                raise Retrying("no modules")

            for data in modules:
                if data["id"] != page_id:
                    raise Retrying("video_id is different from page_id")
                description = data["desc"]
                link = data["video"]["downloadAddr"].encode('utf-8').decode('unicode_escape')
                if video := await client.get(link, headers=_user_agent):
                    video.raise_for_status()
                    return description, video.content


def _user_agent():
        return {
            'User-Agent': (
                f"{''.join(random.choices(string.ascii_lowercase, k=random.randint(4,10)))}-"
                f"{''.join(random.choices(string.ascii_lowercase, k=random.randint(3,7)))}/"
                f"{random.randint(10, 300)} "
                f"({datetime.now().replace(microsecond=0).timestamp()})"
            )
        }

def _tt_webid_v2():
        return {'tt_webid_v2': f"{random.randint(10 ** 18, (10 ** 19) - 1)}"}
