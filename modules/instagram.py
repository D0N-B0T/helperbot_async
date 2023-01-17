from loguru import logger
import os
from telegram import constants

async def send_instagram_video(update, context):    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=constants.ChatAction.UPLOAD_DOCUMENT)
    url = update.message.text.split(" ")[1]                
    split_instagram_url = update.message.text.split("?")[0].split("/")
    shortcode = split_instagram_url[5]
    logger.info(f"Downloading instagram post {split_instagram_url} with shortcode {shortcode}")
    try:
        logger.info(f"Downloading instagram post {url}")
        os.system('bash yt-dlp/yt-dlp.sh '+ url +' -o '+shortcode+'.mp4')
        await update.message.reply_video(video=open(shortcode+'.mp4', 'rb'))

        
    except Exception as e:
        logger.error(f"Error downloading instagram post {split_instagram_url} with shortcode {shortcode}: {e}")
        return
