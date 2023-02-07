
#import inbuilt modules
from ast import main
import os, time, re, requests

#import downloaders
import yt_dlp

#Import Telegram Features
from telegram import InputMediaAudio, InputMediaVideo, Update
from telegram.ext import ContextTypes
from loguru import logger
from telegram import constants

def convert_html(string):
    string= string.replace('<', '&lt')
    string= string.replace('>', '&gt')
    return string


def caption_cleaner(title):
    text = re.sub(r'\d{4}\/\d{2}\/\d{2}|(?:[01]\d|2[0-3]):(?:[0-5]\d):(?:[0-5]\d)|UTC|@[A-Za-z0-9_.]+|\#[A-Za-z0-9_]+|▫️$|•| :\n|\n\.\n|\.\n\.|follow|via|credit|Follow|Via| - |',"",title)
    text = re.sub(r'(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)',"", text)
    text = re.sub(r'[\s]{3}','',text)
    return text

def yt_dlp_tiktok_dl(URLS):
    if re.match(r"(?:https:\/\/)?([vt]+)\.([tiktok]+)\.([com]+)\/([\/\w@?=&\.-]+)", URLS):
        r = requests.head(URLS, allow_redirects=False)
        URLS = r.headers['Location']
    ydl_opts = {'ignoreerrors': True, 'trim_file_name' : 25}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(URLS)
        video_title = info['title']
    video_title = "✨" if video_title == '' else video_title
    video_title = convert_html(video_title)
    CAPTION = '<a href="{}">{}</a>'.format(URLS,video_title)
    return CAPTION

def yt_dlp_ig_reel_dl(URLS):
    ydl_opts = {'ignoreerrors': True, 'trim_file_name' : 25}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(URLS)
        video_title = info['description']
    video_title = caption_cleaner(video_title)
    video_title = convert_html(video_title)
    video_title = "✨" if re.match(r'^[\s|\n]+$',video_title) else video_title
    CAPTION = '<a href="{}">{}</a>'.format(URLS,video_title)
    return CAPTION

def yt_dlp_youtube_dl(URLS):
    ydl_opts = {'trim_file_name' : 20,'max_filesize':50*1024*1024, 'format_sort': ['res:1080','ext:mp4:m4a']}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(URLS)
        video_title = info['title']
    video_title = "✨" if video_title == '' else video_title
    video_title = convert_html(video_title)
    CAPTION = '<a href="{}">{}</a>'.format(URLS,video_title)
    return CAPTION

def yt_dlp_youtube_audio_dl(URLS):
    ydl_opts = {'format': 'm4a/bestaudio/best',
    # ℹ️ See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
    'postprocessors': [{  # Extract audio using ffmpeg
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',}]}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(URLS)
        audio_title = info['title']
    audio_title = "✨" if audio_title == '' else audio_title
    CAPTION = '<a href="{}">{}</a>'.format(URLS,audio_title)
    return CAPTION

def yt_dlp_Others_dl(URLS):
    ydl_opts = {'trim_file_name' : 20, 'max_filesize':50*1024*1024}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(URLS)
        video_title = info['title']
    video_title = "✨" if video_title == '' else video_title
    video_title = convert_html(video_title)
    CAPTION = '<a href="{}">{}</a>'.format(URLS,video_title)
    return CAPTION

async def yt_dlp_sender(update,context,CAPTION):
    downloaded_files = os.listdir('./')
    tosend=list()
    for medias in downloaded_files:
        size =int((os.path.getsize(medias))/(1024*1024))
        if os.path.isdir(medias):
            'is a directory'
        elif medias.endswith(('avi', 'flv', 'mkv', 'mov', 'mp4', 'webm', '3g2', '3gp', 'f4v', 'mk3d', 'divx', 'mpg', 'ogv', 'm4v', 'wmv', 'aiff', 'alac', 'flac', 'm4a', 'mka', 'mp3', 'ogg', 'opus', 'wav','aac', 'ape', 'asf', 'f4a', 'f4b', 'm4b', 'm4p', 'm4r', 'oga', 'ogx', 'spx', 'vorbis', 'wma')):
            tosend.append(medias)
        elif size > 50 or medias.endswith('part'):
            print(medias + "is "+str(size)+" MB."+"\n"+"Which is greater than 50 MB, So removing it !!")
            os.remove(medias)
    #print(tosend)
    if tosend == None:
        return "No Files Downloaded"
    no_of_files = len(tosend)
    if no_of_files == 1:
        files = tosend[0]
        if files.endswith(('avi', 'flv', 'mkv', 'mov', 'mp4', 'webm', '3g2', '3gp', 'f4v', 'mk3d', 'divx', 'mpg', 'ogv', 'm4v', 'wmv')):
                print("Found Short Video and Sending!!!")
                await context.bot.send_video(chat_id=update.message.chat_id, video=open(files, 'rb'), supports_streaming=True,caption = CAPTION, parse_mode='HTML')
                print("Video {} was Sent Successfully!".format(files))
                os.remove(files)
                try:
                    await context.bot.delete_message(chat_id=update.message.chat.id, message_id=update.message.message_id)
                except BaseException:
                    print("Message was already deleted.")
                time.sleep(3)
        elif files.endswith(('aiff', 'alac', 'flac', 'm4a', 'mka', 'mp3', 'ogg', 'opus', 'wav','aac', 'ape', 'asf', 'f4a', 'f4b', 'm4b', 'm4p', 'm4r', 'oga', 'ogx', 'spx', 'vorbis', 'wma')):
                print("Found Short Audio")
                await context.bot.send_audio(chat_id=update.message.chat_id, audio=open(files, 'rb'), caption = CAPTION, parse_mode='HTML')
                print("Audio {} was Sent Successfully!".format(files))
                os.remove(files)
                try:
                    await context.bot.delete_message(chat_id=update.message.chat.id, message_id=update.message.message_id)
                except BaseException:
                    print("Message was already deleted. \n \n")
                time.sleep(2)
    elif no_of_files > 1 and no_of_files<=10:
        media_group=[]
        for multimedias in tosend:
                if multimedias.endswith(('avi', 'flv', 'mkv', 'mov', 'mp4', 'webm', '3g2', '3gp', 'f4v', 'mk3d', 'divx', 'mpg', 'ogv', 'm4v', 'wmv')): #appends videos

                    media_group.append(InputMediaVideo(open(multimedias,'rb'),caption = CAPTION if len(media_group) == 0 else '',parse_mode='HTML'))
                elif multimedias.endswith(('aiff', 'alac', 'flac', 'm4a', 'mka', 'mp3', 'ogg', 'opus', 'wav','aac', 'ape', 'asf', 'f4a', 'f4b', 'm4b', 'm4p', 'm4r', 'oga', 'ogx', 'spx', 'vorbis', 'wma')): #appends audios

                    media_group.append(InputMediaAudio(open(multimedias,'rb'), caption = CAPTION if len(media_group) == 0 else '',parse_mode='HTML'))
        
        await context.bot.send_media_group(chat_id = update.message.chat.id, media = media_group, write_timeout=60)
        media_group = []
        try:
            await context.bot.delete_message(chat_id=update.message.chat.id, message_id=update.message.message_id)
        except BaseException:
            print("Yt-DLP Sender, Message was already deleted.")
    


async def main_url_dl(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=constants.ChatAction.UPLOAD_DOCUMENT)
    if not update.message.text.startswith('/video'):
        return
    
    string = update.message.text.split(' ', 1)[1]
    string = update.message.text
    print(string)
    
    
    pattern = '([^\s\.]+\.[^\s]{2,}|www\.[^\s]+\.[^\s]{2,})'
    entries = re.findall(pattern, string)
    for URLS in entries:
        if re.match(r"(?:https:\/\/)?([vt]+|[www]+)\.?([tiktok]+)\.([com]+)\/([\/\w@?=&\.-]+)", URLS):
            CAPTION = yt_dlp_tiktok_dl(URLS)
            await yt_dlp_sender(update,context,CAPTION)
        
        elif re.match(r"((?:http|https):\/\/)(?:www.)?(?:instagram.com|instagr.am|instagr.com)\/(\w+)\/([\w\-/?=&]+)",URLS):
            try:
                print("Instaloader Module Failed, retrying with yt-dlp")
                CAPTION = yt_dlp_ig_reel_dl(URLS)
                await yt_dlp_sender(update,context,CAPTION)
            except BaseException:
                print("yt-dlp module failed downloading this video. \n Maybe not a video or private one.")
        
        elif re.match(r"(?:https?:\/\/)?(?:www\.|m\.)?youtu\.?be(?:\.com)?\/?.*(?:watch|embed)?(?:.*v=|v\/|\/)([\w\-_\&=]+)?", URLS):
            CAPTION = yt_dlp_youtube_dl(URLS)
            await yt_dlp_sender(update,context,CAPTION)
        
        else:
            try:
                CAPTION = yt_dlp_Others_dl(URLS)
                await yt_dlp_sender(update,context,CAPTION)
            except BaseException:
                print("Unsupported URL : {}".format(URLS))

