import yt_dlp
from telegram import constants
from loguru import logger

from utilities import file_in_limits

name = "youtube_dl"
TMP_FOLDER = "tmp/"
ydl_opts = {'outtmpl': f'{TMP_FOLDER}%(id)s.%(ext)s', 'quiet': False}
    
async def send_facebook_video(update, context):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=constants.ChatAction.UPLOAD_DOCUMENT)
    print(f"Sending facebook video from {update.message.from_user.username} ({update.message.from_user.id})")
    print(f"URL: {update.message.text.split(' ')[1]}")

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'mp4'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url=update.message.text.split(" ")[1], download=False)
    caption = f"{info['title']}"

    formats = []
    for f in info['formats']:
        if f['ext'] == 'mp4':
            formats.append(f)

    file_url = formats[-1]['url']

    if not await file_in_limits(file_url):
        file_url = formats[-2]['url']

    if await file_in_limits(file_url):
        await update.message.reply_video(video=file_url, caption=caption[:1000], parse_mode='HTML')

    else:
        await update.message.reply_html(f"El video es muy grande y no puedo subirlo, pero <a href='{file_url}'>si haces clic aca</a> lo podrás ver en el navegador. Es una mierda de solucion pero es lo que tengo para ofrecer por el momento.")
        
async def send_facebook_video(update, context):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=constants.ChatAction.UPLOAD_DOCUMENT)
    logger.debug(f"Sending facebook video from {update.message.from_user.username} ({update.message.from_user.id})")
    url = update.message.text.split(" ")[1]
    
    ydl = yt_dlp.YoutubeDL(ydl_opts)
    cdn_url = None
    status = 'success'

    try:
        info = ydl.extract_info(url, download=False)
    except yt_dlp.utils.DownloadError as e:
        logger.debug(f'No video - Youtube normal control flow: {e}')
        return False
    except Exception as e:
        logger.debug(f'ytdlp exception which is normal for example a facebook page with images only will cause a IndexError: list index out of range. Exception here is: \n  {e}')
        return False

    if info.get('is_live', False):
        logger.warning("Live streaming media, not archiving now")
        return False