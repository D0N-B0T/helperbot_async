from loguru import logger
import os,sys
from telegram import constants
async def send_instagram_video(update, context):    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=constants.ChatAction.UPLOAD_DOCUMENT)
    url = update.message.text.split(" ")[1]                
    split_instagram_url = update.message.text.split("?")[0].split("/")
    
    parte3 = split_instagram_url[5]
    logger.info(f"Parte3: {parte3}")
    
    
    
    
    shortcode = split_instagram_url[5]
    logger.info(f"Starting download instagram post {url}")

    try:
        os.system('bash yt-dlp/yt-dlp.sh --no-warnings '+ url +' -o '+shortcode+'.mp4')
        logger.info(f"File downloaded: {shortcode}.mp4")
    except Exception as e:
        logger.error(f"yt-dlp no ha descargado nada. Error {url}: {e} on line {sys.exc_info()[-1].tb_lineno} of {__file__}")
        return
    
    try:
        await update.message.reply_video(video=open(shortcode+'.mp4', 'rb'))        
        logger.info(f"File sent: {shortcode}.mp4")
    except Exception as e:
        logger.error(f"Error sending instagram post {url}: {e} on line {sys.exc_info()[-1].tb_lineno} of {__file__}")
        return