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
    
    file_name = str(uuid.uuid4())+".mp4"
    FileDownload().download_video(file_url, TMP_FOLDER, file_name)
    logger.debug(f"File url: {file_url}")
               
    
    if not await file_in_limits(file_url):
        file_url = formats[-2]['url']
        
    if await file_in_limits(file_url):
        await update.message.reply_video(video=file_url, caption=caption[:1000], parse_mode='HTML')    
    else:
        logger.debug(f"File size: {formats[-2]['filesize']}")
        await update.message.reply_html(f"El video es muy grande y no puedo subirlo, pero <a href='{file_url}'>si haces clic aca</a> lo podrás ver en el navegador. Es una mierda de solucion pero es lo que tengo para ofrecer por el momento.")

FileDownload().download_video("https://video.xx.fbcdn.net/v/t42.1790-2/324251287_686159519651800_898228869206165013_n.mp4?_nc_cat=102&ccb=1-7&_nc_sid=985c63&efg=eyJybHIiOjQ4NywicmxhIjoxMTg5LCJ2ZW5jb2RlX3RhZyI6InN2ZV9zZCJ9&_nc_ohc=HJfL3vGLyegAX8r16Ci&rl=487&vabr=271&_nc_ht=video.xx&oh=00_AfBQJ1NE6amsiFwAuDupsQ6rxhwtLZhMu7LCxOPLdy120w&oe=63C262A1", "tmp", "test")