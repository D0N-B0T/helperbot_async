import yt_dlp
from telegram import constants

from utilities import file_in_limits


async def send_facebook_video(update, context):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=constants.ChatAction.UPLOAD_DOCUMENT)

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