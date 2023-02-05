import os
import uuid
from urllib import parse

import aiohttp
import requests
from telegram import (InlineQueryResultArticle, InlineQueryResultVideo,
                      InputTextMessageContent, Update, constants)
from telegram.error import BadRequest
from telegram.ext import ContextTypes

import config
from modules.utilities import file_in_limits
from loguru import logger


async def get_tiktok_video_infos(username: str, video_ID: str) -> dict:
    """
    Get Infos from the tiktok page and return a dict of relevant informations
    """

    infos = {}
    headers = {'User-Agent': 'com.ss.android.ugc.trill/494+Mozilla/5.0+(Linux;+Android+12;+2112123G+Build/SKQ1.211006.001;+wv)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Version/4.0+Chrome/107.0.5304.105+Mobile+Safari/537.36'}

    api_url = f"https://api16-normal-c-useast1a.tiktokv.com/aweme/v1/feed/?aweme_id={video_ID}"
    async with aiohttp.ClientSession() as session:
        logger.debug(f"Getting TikTok video infos from {api_url}")
        async with session.get(api_url, headers=headers, timeout=10) as response:
            logger.debug(f"Got TikTok video infos from {api_url}")
            response = await response.json()
            logger.debug(f"Got TikTok video infos from {api_url} {response}")
    
    data = response["aweme_list"][0]

    video_url = data["video"]["play_addr"]["url_list"][0]
    caption = f"<a href='https://www.tiktok.com/{username}'>{username}</a> (<a href='https://www.tiktok.com/{username}/video/{video_ID}'>link</a>)\n"
    caption += data["desc"]
    height = data["video"]["height"]
    width = data["video"]["width"]
    thumbnail_url = data["video"]["cover"]["url_list"][0]
    title = f"TikTok from {username}"

    infos["username"] = username
    infos["video_id"] = video_ID
    infos["video_url"] = video_url
    infos["title"] = title
    infos["caption"] = caption
    infos["thumbnail_url"] = thumbnail_url
    infos["height"] = height
    infos["width"] = width

    return infos


async def get_tiktok_username_id(url):
    """
    Get the username and the video id from a tiktok url
    """
    # from '/video https://www.tiktok.com/@alexandrachavez.23/video/7160401768625474822?_r=1&_t=8YQxzaqdbfy&is_from_webapp=v1'
    # get only the url
    url = url.split(" ")[1]
    purl = parse.urlparse(url)

    if purl.netloc == "vm.tiktok.com":
        tiktok_id = purl.path.split("/")[1]
        logger.debug(f"tiktok_id from {url} {tiktok_id}")
        link = f"https://vm.tiktok.com/{tiktok_id}"
        logger.debug(f"link from {url} {link}")
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"}
        # aqui ya deja de funcionar
        response = requests.get(link, headers=headers) 
        if response.status_code == 200:
            id = response.text.split("/video/")[1].split("?")[0].split("/")[0]
            username = response.text.split("/video/")[0].split("https://www.tiktok.com/@")[1]                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     
            logger.debug(f"response from {link} {response}")
        else:
            logger.debug(f"Invalid URL {url}")
            raise Exception("Invalid URL")
        
        
    elif purl.netloc == 'www.tiktok.com':
        username = purl.path.split("/")[1]
        id = purl.path.split("/")[3]
        link = url
    else:
        logger.debug(f"Invalid URL {url}")
        raise Exception("Invalid URL")
        
    return (username, id, link)


async def send_tiktok_video(update, context):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=constants.ChatAction.UPLOAD_VIDEO)

    logger.debug(f"Got TikTok video from {update.message.from_user.username} {update.message.text}")
    url_infos = await get_tiktok_username_id(update.message.text)
    logger.debug(f"Got TikTok video from {update.message.from_user.username} {update.message.text} {url_infos}")
    username = url_infos[0]
    video_id = url_infos[1]

    video_infos = await get_tiktok_video_infos(username, video_id)
    logger.debug(f"Got TikTok video from {update.message.from_user.username} {update.message.text} {video_infos}")
    video_url = video_infos.get("video_url")
    logger.debug(f"Got TikTok video from {update.message.from_user.username} {update.message.text} {video_url}")
    caption = video_infos.get("caption")
    logger.debug(f"Got TikTok video from {update.message.from_user.username} {update.message.text} {caption}")
    
    if int(requests.head(video_url).headers["Content-Length"]) >= 50000000:
        if update.message.from_user.language_code == "it":
            await update.message.reply_html(f"Questo video è troppo grande e non posso caricarlo, ma se clicchi <a href='{video_url}'>qui</a> puoi guardarlo dal browser.")
        else:
            await update.message.reply_html(f"This video is too big and I can't upload it, but if you click <a href='{video_url}'>here</a> you can watch it in the browser.")
    elif int(requests.head(video_url).headers["Content-Length"]) >= 20000000:
        if update.message.from_user.language_code == "it":
            messaggio = await update.message.reply_text("Il video è più grande del solito, dammi qualche secondo ok")
        else:
            messaggio = await update.message.reply_text("The video is too big, give me a second ok")
        filename = uuid.uuid4()
        video_width = video_infos.get("width")
        video_height = video_infos.get("height")
        open(f"{config.main_directory}/{filename}.mp4",
            "wb").write(requests.get(video_url).content)
        await update.message.reply_video(
            video=open(f'{config.main_directory}/{filename}.mp4', "rb"),
            caption=caption,
            parse_mode='HTML',
            width=video_width,
            height=video_height
        )
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=messaggio.message_id)
        os.remove(f"{config.main_directory}/{filename}.mp4")
    else:
        try:
            await update.message.reply_video(video=video_url, parse_mode='HTML', caption=caption)
        except BadRequest:
            if update.message.from_user.language_code == "it":
                await update.message.reply_html(f"Telegram non supporta questo video, ma se clicchi <a href='{video_url}'>qui</a> puoi guardarlo dal browser.")
            else:
                await update.message.reply_html(f"Telegram doesn't support this video, but if you click <a href='{video_url}'>here</a> you can watch it in the browser.")


async def inline_tiktok_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    if not query:
        return

    if query.startswith(("https://vm.tiktok.com", "https://www.tiktok.com")):
        try:
            url_infos = await get_tiktok_username_id(query)
            logger.debug(f"GOT TIKTOK username and id {url_infos}")
            username = url_infos[0]
            video_id = url_infos[1]
            
            video_infos = await get_tiktok_video_infos(username, video_id)
            logger.debug(f"GOT TIKTOK VIDEO INFOS {video_infos}")
            video_url = video_infos.get("video_url")
            caption = video_infos.get("caption")
            thumbnail = video_infos.get("thumbnail_url")
            
            results = []
            if await file_in_limits(video_url):
                logger.info(f"File size is ok, sending video to {update.inline_query.from_user.username}")
                results.append(
                    InlineQueryResultVideo(
                        id=str(uuid.uuid4()),
                        video_url=video_url,
                        mime_type="video/mp4",
                        thumb_url=thumbnail,
                        title=f"TikTok video by {username}",
                        caption=caption,
                        parse_mode="HTML"
                    )
                )
                await context.bot.answer_inline_query(update.inline_query.id, results)
            else:
                results.append(
                    InlineQueryResultArticle(
                        id=str(uuid.uuid4()),
                        title=f"TikTok video by {username}",
                        input_message_content=InputTextMessageContent(
                            f"The video is too big, but here's the direct link to view it in your browser: <a href='{video_url}'>link</a>\n\n{caption}",
                            parse_mode="HTML"
                        ),
                        description=caption
                    )
                )
                await context.bot.answer_inline_query(update.inline_query.id, results)
        except Exception as e:
            print(e)
            pass