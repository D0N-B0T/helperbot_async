import asyncio
import json
import random
import string
from datetime import datetime
from functools import wraps
import httpx
from bs4 import BeautifulSoup
from loguru import logger
from telegram import constants



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



async def download_video(update,context):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=constants.ChatAction.UPLOAD_DOCUMENT)
    url = update.message.text.split(" ")[1]
    logger.info(f"downloading {url}")
    
    
    try:
        with httpx.AsyncClient(headers= _user_agent, timeout=30, cookies=_tt_webid_v2, follow_redirects=True) as client:   
            logger.info(f"downloading {url}")
            page = await client.get(url, headers=_user_agent)
            logger.info(f"status code {page.status_code}")
            page_id = page.url.path.rsplit('/', 1)[-1]
            logger.info(f"page id {page_id}")
            soup = BeautifulSoup(page.text, 'html.parser')
            script_selector = 'script[id="SIGI_STATE"]'
            if script := soup.select_one(script_selector):
                script = json.loads(script.text)
            else:
                logger.error(f"no script with selector {script_selector}")

            modules = tuple(script.get("ItemModule").values())
            if not modules:
                logger.error("no modules found")

            for data in modules:
                if data["id"] != page_id:
                    logger.error(f"page id {page_id} does not match data id {data['id']}")
                description = data["desc"]
                link = data["video"]["downloadAddr"].encode('utf-8').decode('unicode_escape')
                if video := await client.get(link, headers=_user_agent):
                    video.raise_for_status()
                    await context.bot.send_video(chat_id=update.effective_chat.id, video=video.content, caption=description, supports_streaming=True)
    except Exception as e:
        error = e+"error downloading video in line" + str(sys.exc_info()[-1].tb_lineno)
        logger.error(error)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Error downloading video")


