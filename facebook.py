import yt_dlp
from telegram import constants
from loguru import logger
import uuid

from utilities import file_in_limits

from video import FileDownload

name = "youtube_dl"
TMP_FOLDER = "tmp/"

    
async def send_facebook_video(update, context):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=constants.ChatAction.UPLOAD_DOCUMENT)
    logger.debug(f"Sending facebook video from {update.message.from_user.username} ({update.message.from_user.id})")
    
    ydl_opts = {'outtmpl': '%(id)s.%(ext)s'}
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url=update.message.text.split(" ")[1], download=False)
        
    caption = f"{info['title']}"
    logger.debug(f"Video title: {info['title']}")
    formats = []
    for f in info['formats']:
        if f['ext'] == 'mp4':
            formats.append(f)
            
    logger.debug(f"Formats: {formats}")
    file_url = formats[-1]['url']  
    logger.debug(f"File url: {file_url}")  
    
    file_name = str(uuid.uuid4())+".mp4"
    FileDownload().download_video(file_url, TMP_FOLDER, file_name)
    logger.debug(f"File name downloaded: {file_name}")
    await update.message.reply_video(video="tmp/"+file_name, caption=caption[:1000], parse_mode='HTML') 
    #this is a check to see if the file is too big to be sent
    if not await file_in_limits(file_url):
        file_url = formats[-2]['url']
    #if file is not too big, send it
    if await file_in_limits(file_url):
        await update.message.reply_video(video="tmp/"+file_name, caption=caption[:1000], parse_mode='HTML') 
    else:
        print("File too big")
        await update.message.reply_html(f"El video es muy grande y no puedo subirlo, pero <a href='{file_url}'>si haces clic aca</a> lo podrás ver en el navegador. Es una mierda de solucion pero es lo que tengo para ofrecer por el momento.")