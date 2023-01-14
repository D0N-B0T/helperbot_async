import yt_dlp
from telegram import constants

from utilities import file_in_limits

async def send_twitter_video(update, context):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=constants.ChatAction.UPLOAD_DOCUMENT)
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'outtmpl': '%(id)s.%(ext)s',
        'format': 'mp4'
    }
    # puede que haya errores, es culpa de outtmpl
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        #ydl.download([testvideourl])
        testvideourl = update.message.text.split(" ")[1]
        info = ydl.extract_info(testvideourl, download=False)
        description = info['description']
        uploader = info['uploader']
        uploader_id = info['uploader_id']
        final_filename = info['id'] +'.mp4'
    
    formats = []
    for f in info['formats']:
        if f['ext'] == 'mp4':
            formats.append(f)
    file_url = formats[-1]['url']
    
    if not await file_in_limits(file_url):
        file_url = formats[-2]['url']
    
    if await file_in_limits(file_url):
        await update.message.reply_video(video=file_url, caption=description[:1000], parse_mode='HTML')
    else:
        await update.message.reply_html(f"El video es muy grande y no puedo subirlo, pero <a href='{file_url}'>si haces clic aca</a> lo podrás ver en el navegador. Es una mierda de solucion pero es lo que tengo para ofrecer por el momento.")
        
        