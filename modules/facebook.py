from telegram import constants
from loguru import logger
import os


async def send_facebook_video_watch(update, context):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=constants.ChatAction.UPLOAD_DOCUMENT)
    url = update.message.text.split(" ")[1]
    shortcode = url.split("/")[3]
    logger.info(f"Downloading facebook post {url} with shortcode {shortcode}")
    
    try:
        os.system('bash yt-dlp/yt-dlp.sh "'+ url +'" -o '+shortcode + ' -f mp4')   
        logger.info(f"Done downloading facebook post {url} with shortcode {shortcode}")
        
        logger.info(f"Checking if {shortcode}.mp4 exists or is a mkv")
        if os.path.exists(shortcode + '.mp4'):
            logger.info(f"Sending {shortcode}.mp4")
            await update.message.reply_video(video=open(shortcode + '.mp4', 'rb'))
        if os.path.exists(shortcode + '.mp4.mkv'):
            logger.info(f"Sending {shortcode}.mp4.mkv")
            await update.message.reply_video(video=open(shortcode + '.mp4.mkv', 'rb'))
        else:
            logger.info(f"Sending whatever exist with {shortcode} name")
            await update.message.reply_video(video=open(shortcode , 'rb'))
        logger.info(f"Done.")
    except Exception as e:
        logger.error(f"Error downloading facebook post {url} with shortcode {shortcode}: {e}")
        return
    
    
    
async def send_facebook_video_reel(update, context):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=constants.ChatAction.UPLOAD_DOCUMENT)
    url = update.message.text.split(" ")[1]
    parts = url.split("/")
    shortcode = parts[-1].split("?")[0]
    logger.info(f"Downloading facebook post {url} with shortcode {shortcode}")
    try:
        os.system('bash yt-dlp/yt-dlp.sh "' + url + '" -o ' + shortcode + ' -f mp4')

        logger.info(f"Done downloading facebook post {url} with shortcode {shortcode}")
        
        logger.info(f"Checking if {shortcode}.mp4 exists or is a mkv")
        if os.path.exists(shortcode + '.mp4'):
            logger.info(f"Sending {shortcode}.mp4")
            await update.message.reply_video(video=open(shortcode + '.mp4', 'rb'))
        if os.path.exists(shortcode + '.mp4.mkv'):
            logger.info(f"Sending {shortcode}.mp4.mkv")
            await update.message.reply_video(video=open(shortcode + '.mp4.mkv', 'rb'))
        else:
            logger.info(f"Neither {shortcode}.mp4 nor {shortcode} exist")
            await update.message.reply_video(video=open(shortcode , 'rb'))
        
        logger.info(f"Done.")
        
    except Exception as e:
        logger.error(f"Error downloading facebook post {url} with shortcode {shortcode}: {e}")
        return   
    