# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from PIL import Image, ImageDraw, ImageFont
import re, requests, json, random,random, os
import datetime as dt
from loguru import logger
from typing import Optional, Tuple
import requests
from telegram import __version__ as TG_VER
from telegram.ext import (ApplicationBuilder,MessageHandler, PicklePersistence, filters)
from telegram import Chat, ChatMember, ChatMemberUpdated, Update, constants
from telegram.constants import ParseMode
from telegram.ext import ChatMemberHandler, CommandHandler, ContextTypes

import config

from modules.twitter import send_twitter_video
from modules.facebook import send_facebook_video_reel, send_facebook_video_watch
from modules.tiktok import main_url_dl
from modules.instagram import send_instagram_video


from modules.yastaba_main import process


if not os.path.exists(f"{config.main_directory}/db"):
    os.makedirs(f"{config.main_directory}/db")

persistence = PicklePersistence(filepath=f'{config.main_directory}/db/persistence.pkl')
application = ApplicationBuilder().token(config.BOT_TOKEN).persistence(persistence).build()

# = ============================  bienvenida ============================ #
def extract_status_change(chat_member_update: ChatMemberUpdated) -> Optional[Tuple[bool, bool]]:

    status_change = chat_member_update.difference().get("status")
    old_is_member, new_is_member = chat_member_update.difference().get("is_member", (None, None))

    if status_change is None:
        return None

    old_status, new_status = status_change
    was_member = old_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (old_status == ChatMember.RESTRICTED and old_is_member is True)
    is_member = new_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (new_status == ChatMember.RESTRICTED and new_is_member is True)

    return was_member, is_member


async def track_chats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = extract_status_change(update.my_chat_member)
    if result is None:
        return
    was_member, is_member = result

    cause_name = update.effective_user.full_name

    chat = update.effective_chat
    if chat.type == Chat.PRIVATE:
        if not was_member and is_member:
            logger.info("%s started the bot", cause_name)
            context.bot_data.setdefault("user_ids", set()).add(chat.id)
        elif was_member and not is_member:
            logger.info("%s blocked the bot", cause_name)
            context.bot_data.setdefault("user_ids", set()).discard(chat.id)
    elif chat.type in [Chat.GROUP, Chat.SUPERGROUP]:
        if not was_member and is_member:
            logger.info("%s added the bot to the group %s", cause_name, chat.title)
            context.bot_data.setdefault("group_ids", set()).add(chat.id)
        elif was_member and not is_member:
            logger.info("%s removed the bot from the group %s", cause_name, chat.title)
            context.bot_data.setdefault("group_ids", set()).discard(chat.id)
    else:
        if not was_member and is_member:
            logger.info("%s added the bot to the channel %s", cause_name, chat.title)
            context.bot_data.setdefault("channel_ids", set()).add(chat.id)
        elif was_member and not is_member:
            logger.info("%s removed the bot from the channel %s", cause_name, chat.title)
            context.bot_data.setdefault("channel_ids", set()).discard(chat.id)

async def greet_chat_members(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = extract_status_change(update.chat_member)
    if result is None:
        return

    was_member, is_member = result
    cause_name = update.chat_member.from_user.mention_html()
    member_name = update.chat_member.new_chat_member.user.mention_html()

    if not was_member and is_member:
        if member_name == cause_name:
            await update.effective_chat.send_message(f"{member_name} se ha unido al grupo. Bienvenido!\nPor favor indique su nombre de usuario de El Antro.\n\n\n??Caf?? con o sin azucar?", parse_mode=ParseMode.HTML)
        else:
            await update.effective_chat.send_message(f"{member_name} fue a??adido por {cause_name}. Bienvenido!\nPor favor indique su nombre de usuario de El Antro.\n\n\n??Caf?? con o sin azucar?",parse_mode=ParseMode.HTML)
    elif was_member and not is_member:
        if member_name == cause_name:
            await update.effective_chat.send_message(f"{member_name} ha abandonado El Grupazo. \n??Volver?? alg??n d??a?", parse_mode=ParseMode.HTML)
        else:
            await update.effective_chat.send_message(f"{member_name} fue expulsado por {cause_name}. \n Raz??n: 'Por Maraca'.", parse_mode=ParseMode.HTML)





# twitter to nitter        
        
twitter_reg = "^http(?:s)?:\/\/(?:www)?twitter\.com\/([a-zA-Z0-9_]+)"
async def twitter_to_nitter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        with open('blacklist.txt', 'r') as a:
            lista = a.readlines()
        link_found= False
        if re.search(twitter_reg, update.message.text):
            for i in lista:
                if i.strip() in update.message.text.strip():
                    if not link_found:
                        await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text.replace('https://twitter.com/', 'https://nitter.net/'))       
                        link_found = True
                    pass

# /nitter command 


async def nitterc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        new_url = update.message.text.replace('/nitter', '')
        new_url = new_url.replace('https://twitter.com/', 'https://nitter.net/')
        await context.bot.send_message(chat_id=update.effective_chat.id, text=new_url)



# dolar command
    
async def usd_to_clp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        headers = {'User-Agent': '...','referer': 'https://...'}
        url = "https://apps.bolchile.com/api/v1/dolarstatd2"
        response = requests.get(url, headers=headers,verify=True)
        data = json.loads(response.text)
        price = data[0]['cp']
        var = data[0]['variacion']
        var = round(var,2)
        varper = data[0]['variacion_porcentual']
        varper = round(varper,2)
        if var > 0:
            flecha = ' ??????'
            signo = '+'
        else:
            flecha = ' ??????'
            signo = ''
        now = dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours= -4)
        hora = now.strftime("%H:%M")
        dia = now.strftime("%d %B")
        hp = data[0]['hp']
        await update.message.reply_text('<b>USD CLP</b> ' + str(price) + flecha +'\n' +'M??xima: $' +str(hp)+'\n'  + signo + str(var) + '  ('+signo+str(varper)+'%)'+ '\n'+ str(dia) +', '+str(hora) +'\n'+'IrinaExchangeRates ????', parse_mode="HTML")
       
    
async def convertusd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        usd = update.message.text
        usd = usd.split()
        usd = usd[1]
        usd = float(usd)
        clp = usd * 780
        clp = str(clp)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=clp)




def saveDivisas():
    logger.info("Guardando divisas...")
    response = requests.get("https://www.cryptomkt.com/api/landing/ticker")
    data = response.json()

    symbols = [item["symbol"] for item in data]

    with open('symbols.txt', 'w') as file:
        for symbol in symbols:
            file.write(symbol + '\n')
    logger.info("Divisas guardadas.")
saveDivisas()

def checkDivisas(mensaje):
    with open('symbols.txt', 'r') as a:
        lista = a.readlines()
    if mensaje.text in lista:
        return True
    else:
        return False




# = ============================  video ============================ #    
async def link_downloader(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:  
        
    # TIKTOK     
        if update.message.text.startswith(("/video https://vm.tiktok.com", "/video https://www.tiktok.com")):
            await main_url_dl(update, context)

            
    #INSTAGRAM
        if update.message.text.startswith(("/video https://www.instagram.com/p/", "/video https://www.instagram.com/reel/")):
            await main_url_dl(update, context)
            
        if update.message.text.startswith(("/video https://www.instagram.com/stories/", "/video https://instagram.com/stories/")):
            await update.message.reply_text("Por el momento no puedo bajar historias de instagram ????")
            
    # FACEBOOK
        if update.message.text.startswith(("/video https://fb.watch/")):
            await send_facebook_video_watch(update, context)

        if update.message.text.startswith(("/video https://www.facebook.com/reel/")):
           await send_facebook_video_reel(update, context)

    # TWITTER
        if update.message.text.startswith(("/video https://twitter.com/","/video https://twitter.com/", "/video https://mobile.twitter.com/", "/video https://www.twitter.com/", "/video https://twtr.com/", "/video https://m.twitter.com/", "/video https://mobile.twitter.com/", "/video https://twitter.com/i/status/")):
            await send_twitter_video(update, context)
            

            
# add command
async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        arg = update.message.text        
        twurl  = arg.replace('/add ', '')
        
        with open('blacklist.txt', 'r') as f:
            if twurl in f.read():
                print("El enlace ya est?? en la lista.")
            else:
                with open('blacklist.txt', 'a') as f:
                    f.write('\n' + twurl)
                print("El enlace se ha agregado a la lista.")

# ids comand
async def get_ids(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        print(update.effective_chat.id)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=update.effective_chat.id)
        
        
# VIDEOS Y AUDIOS
async def sipoapruebo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        lista2 = ['si']
        if random.choice(lista2):
            await context.bot.send_message(chat_id=update.effective_chat.id, text=random.choice(lista2))

async def francoooo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await context.bot.send_video(chat_id=update.effective_chat.id, video=open('videos/FRANCOFRANCOFRANCOmp4.mp4', 'rb'), supports_streaming=True)


async def compadre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await context.bot.send_video(chat_id=update.effective_chat.id, video=open('videos/COMPADRELASTETAS.mp4', 'rb'), supports_streaming=True)

async def satanas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await context.bot.send_video(chat_id=update.effective_chat.id, video=open('videos/satanas.mp4', 'rb'), supports_streaming=True)

async def pengu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        lista = ['videos/PENGU.mp4', 'videos/pengu2.mp4', 'videos/pengu4.mp4']
        await context.bot.send_video(chat_id=update.effective_chat.id, video=open(random.choice(lista), 'rb'), supports_streaming=True)

async def pengu2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await context.bot.send_video(chat_id=update.effective_chat.id, video=open('videos/pengu4.mp4', 'rb'), supports_streaming=True)

async def send_tio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await context.bot.send_video(chat_id=update.effective_chat.id, video=open('videos/TIO.mp4', 'rb'), supports_streaming=True)


async def send_tio2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await context.bot.send_audio(chat_id=update.effective_chat.id, audio=open('audio/tio2.ogg', 'rb')) #


async def send_quelespasa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await context.bot.send_audio(chat_id=update.effective_chat.id, audio=open('audio/quelespasaporlactm.ogg', 'rb'))


async def send_guatona(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await context.bot.send_audio(chat_id=update.effective_chat.id, audio=open('audio/feminazi.ogg', 'rb'))


async def send_senales(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        if update.message.text.startswith(("/se??ales")):
            await context.bot.send_audio(chat_id=update.effective_chat.id, audio=open('audio/SE??ALES.mp3', 'rb'))
        

async def send_yquemeimportaami(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await context.bot.send_video(chat_id=update.effective_chat.id, video=open('videos/yquemeimportaami.mp4', 'rb'), supports_streaming=True)


async def send_espaldita(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await context.bot.send_audio(chat_id=update.effective_chat.id, audio=open('audio/deespaldita.ogg', 'rb'))

async def send_lodereshoumano(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await context.bot.send_audio(chat_id=update.effective_chat.id, audio=open('audio/loereshoumanoh.ogg', 'rb'))
        
async def send_yafue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        pideuno = random.choice(['op1', 'op2','op3','op4'])
        if pideuno == 'op1':
            await context.bot.send_video(chat_id=update.effective_chat.id, video=open('videos/yafuecabros.mp4', 'rb'), supports_streaming=True)
        elif pideuno == 'op2':
            await context.bot.send_video(chat_id=update.effective_chat.id, video=open('videos/yafuecabros2.mp4', 'rb'), supports_streaming=True)
        elif pideuno == 'op3':
            await context.bot.send_video(chat_id=update.effective_chat.id, video=open('videos/yafuecabros3.mp4', 'rb'), supports_streaming=True)
        elif pideuno == 'op4':
            await context.bot.send_video(chat_id=update.effective_chat.id, video=open('videos/yafuecabros4.mp4', 'rb'), supports_streaming=True)

async def send_callatemierda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await context.bot.send_video(chat_id=update.effective_chat.id, video=open('videos/callatemierda.mp4', 'rb'), supports_streaming=True)
        
async def callate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await context.bot.send_video(chat_id=update.effective_chat.id, video=open('videos/callatectm.mp4', 'rb'), supports_streaming=True)

async def esunavilputa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await context.bot.send_video(chat_id=update.effective_chat.id, video=open('videos/esunavilputa.mp4', 'rb'), supports_streaming=True)
        
async def pedropool(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await context.bot.send_video(chat_id=update.effective_chat.id, video=open('videos/pedropool.mp4', 'rb'), supports_streaming=True)
   

async def arriamujeres(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await context.bot.send_audio(chat_id=update.effective_chat.id, audio=open('audio/arriamujereh.ogg', 'rb'))

async def callaolacra(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        eleccion = ['gifs','audio']
        pideuno = random.choice(eleccion)
        if pideuno == 'gifs':
            await context.bot.send_video(chat_id=update.effective_chat.id, video=open(random.choice(['gifs/cl1.mp4','gifs/cl2.mp4','gifs/cl3.mp4']), 'rb'), supports_streaming=True)
        else:
            await context.bot.send_audio(chat_id=update.effective_chat.id, audio=open(random.choice(['audio/CALLAO_LACRA.hd.mp3']), 'rb'))


async def insuficiente(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await context.bot.send_audio(chat_id=update.effective_chat.id, audio=open('audio/INSUFICIENTE.mp3', 'rb'))
        
async def democracia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await context.bot.send_video(chat_id=update.effective_chat.id, video=open('videos/democracia.mp4', 'rb'), supports_streaming=True)

async def conchetumare(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await context.bot.send_video(chat_id=update.effective_chat.id, video=open('videos/conchetumare.mp4', 'rb'), supports_streaming=True)

async def pelotas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await context.bot.send_audio(chat_id=update.effective_chat.id, audio=open('audio/pelotas.ogg', 'rb'))
        
async def estectm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await context.bot.send_audio(chat_id=update.effective_chat.id, audio=open('audio/estectm.ogg', 'rb'))

async def penca(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await context.bot.send_video(chat_id=update.effective_chat.id, video=open('videos/penca.mp4', 'rb'), supports_streaming=True)
        
async def aquimandoyo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await context.bot.send_video(chat_id=update.effective_chat.id, video=open('videos/aquimandoyo.mp4', 'rb'), supports_streaming=True)


async def send_lloronql(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await context.bot.send_voice(chat_id=update.effective_chat.id, voice=open('audio/lloron.ogg', 'rb'))
        
async def ultraderecha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await context.bot.send_video(chat_id=update.effective_chat.id, video=open('videos/ultraderecha.mp4', 'rb'), supports_streaming=True)

async def send_sapo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await context.bot.send_audio(chat_id=update.effective_chat.id, audio=open('audio/sapo.ogg', 'rb'))
        
async def washitarica(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await context.bot.send_audio(chat_id=update.effective_chat.id, audio=open('audio/washitarica.ogg', 'rb'))
        
async def gei(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await context.bot.send_audio(chat_id=update.effective_chat.id, audio=open('audio/gei.ogg', 'rb'))
async def bala(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await context.bot.send_video(chat_id=update.effective_chat.id, video=open('videos/bala.mp4', 'rb'), supports_streaming=True)
    
async def compadre2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await context.bot.send_audio(chat_id=update.effective_chat.id, audio=open('audio/compadre2.ogg', 'rb'))
        
async def pideperdonmierda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await context.bot.send_video(chat_id=update.effective_chat.id, video=open('videos/pideperdonmierda.mp4', 'rb'), supports_streaming=True)
        
async def insolente(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await context.bot.send_video(chat_id=update.effective_chat.id, video=open('videos/insolente.mp4','rb'),supports_streaming=True)

async def respeto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await context.bot.send_video(chat_id=update.effective_chat.id, video=open('videos/respeto23.mp4','rb'),supports_streaming=True)
        
async def merluzo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await context.bot.send_audio(chat_id=update.effective_chat.id, audio=open('audio/merluzo.ogg', 'rb'))

async def comunistasculiaos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await context.bot.send_audio(chat_id=update.effective_chat.id, audio=open('audio/comunistasculiaos.ogg', 'rb'))
        
async def  trabajo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await context.bot.send_video(chat_id=update.effective_chat.id, video=open('videos/trabajo.mp4', 'rb'), supports_streaming=True)
        
async def venecosqls(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await context.bot.send_audio(chat_id=update.effective_chat.id, audio=open('audio/venecosqls.ogg', 'rb'))
        
# ===============================================================================================================

async def archivazo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        archive_args = update.message.text
        archive_args = archive_args.split()
        archive_args = archive_args[1]
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Enviado al Archivazo.')
        
        
async def send_vistipuntos(message):
    vistipuntos = message.text
    vistipuntos = vistipuntos.split()
    vistipuntos = vistipuntos[1]
    text = vistipuntos

    img = Image.open("media/vistipuntos.jpg")
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype('font/Molot.otf', size=100)
    width, height = font.getsize(text)

    image2 = Image.new('RGBA', (width, height), (0, 0, 128, 0))
    draw2 = ImageDraw.Draw(image2)
    draw2.text((0, 0), text=text, font=font, fill=(0, 0, 0))
    draw2.text((0, 0), text=text, font=font, fill=(0, 0, 0))

    image2 = image2.rotate(-33, expand=1)

    if text == str(range(0,9)):
        px, py = 400, 250
    else:   
        px, py = 370, 230
    sx, sy = image2.size
    img.paste(image2, (px, py, px + sx, py + sy), image2)
    img.save('output.png')

async def vistipuntos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await send_vistipuntos(update.message)
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('output.png', 'rb'))


async def clean(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        os.system('pwd')
        os.system('rm *mp4')
        os.system('rm *json')
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Basura eliminada.')
    

async def say_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text.replace('/say ', ''))
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)


# =======================================================================================

if __name__ == '__main__':    
    os.system('clear')
    logger.critical("Bot iniciado")

    link_downloader_handler = MessageHandler(filters.TEXT, link_downloader)
    application.add_handler(link_downloader_handler)

    
    help_handler = CommandHandler('help', help)
    application.add_handler(help_handler, 4)
    

    addcomand_handler = CommandHandler('addcomand', add_command)
    application.add_handler(addcomand_handler, 2)
    
    getids = CommandHandler('ids', get_ids)
    application.add_handler(getids, 3)
    
    usdtoclp_handler = CommandHandler('usdclp', usd_to_clp)    
    application.add_handler(usdtoclp_handler, 6)
    
    twitter_to_nitter_handler = MessageHandler(filters.TEXT, twitter_to_nitter)
    application.add_handler(twitter_to_nitter_handler, 5)
    
    nitterc_handler = CommandHandler('nitter', nitterc)
    application.add_handler(nitterc_handler, 72)
    
    
    
    # add handlers for the videos y audios part
    
    sipoapruebo_handler = CommandHandler('sipoapruebo', sipoapruebo)
    application.add_handler(sipoapruebo_handler, 10)
    
    franco_handler = CommandHandler('franco', francoooo)
    application.add_handler(franco_handler, 11)
    
    compadre_handler = CommandHandler('compadre', compadre)
    application.add_handler(compadre_handler, 12)
    
    pengu_handler = CommandHandler('pengu', pengu)
    application.add_handler(pengu_handler, 13)
    
    send_tio_handler = CommandHandler('tio', send_tio)
    application.add_handler(send_tio_handler, 14)
    
    send_tio2_handler = CommandHandler('tio2', send_tio2)
    application.add_handler(send_tio2_handler, 15)
    
    send_quelespasa_handler = CommandHandler('quelespasa', send_quelespasa)
    application.add_handler(send_quelespasa_handler, 16)
    
    send_guatona_handler = CommandHandler('guatona', send_guatona)
    application.add_handler(send_guatona_handler, 17)
    
    
    send_senales_handler = MessageHandler(filters.TEXT, send_senales)
    application.add_handler(send_senales_handler, 18)
    
    send_yquemeimportaami_handler = CommandHandler('yquemeimportaami', send_yquemeimportaami)
    application.add_handler(send_yquemeimportaami_handler, 19)
    
    send_espaldita_handler = CommandHandler('espaldita', send_espaldita)
    application.add_handler(send_espaldita_handler, 20)
    
    send_loderechoumano_handler = CommandHandler(['loderechoumano','dereshohumanoh'], send_lodereshoumano)
    application.add_handler(send_loderechoumano_handler, 21)
    
    send_yafue_handler = CommandHandler('yafue', send_yafue)
    application.add_handler(send_yafue_handler, 22)
    
    send_callatemierda_handler = CommandHandler('callatemierda', send_callatemierda)
    application.add_handler(send_callatemierda_handler, 23)
    
    send_callate_handler = CommandHandler('callate', callate)
    application.add_handler(send_callate_handler, 24)
    
    send_esunavilputa_handler = CommandHandler('esunavilputa', esunavilputa)
    application.add_handler(send_esunavilputa_handler, 25)
    
    send_pedropool_handler = CommandHandler('pedropool', pedropool)
    application.add_handler(send_pedropool_handler, 26)
    
    send_arriamujeres_handler = CommandHandler('arribamujeres', arriamujeres)
    application.add_handler(send_arriamujeres_handler, 27)
    
    send_callaolacra_handler = CommandHandler('callaolacra', callaolacra)
    application.add_handler(send_callaolacra_handler, 28)
    
    send_insuficiente_handler = CommandHandler('insuficiente', insuficiente)
    application.add_handler(send_insuficiente_handler, 29)
    
    send_democracia_handler = CommandHandler('democracia', democracia)
    application.add_handler(send_democracia_handler, 30)
    
    send_conchetumare_handler = CommandHandler('conchetumare', conchetumare)
    application.add_handler(send_conchetumare_handler, 31)
    
    send_pelotas_handler = CommandHandler('pelotas', pelotas)
    application.add_handler(send_pelotas_handler, 32)
    
    send_estectm_handler = CommandHandler('estectm', estectm)
    application.add_handler(send_estectm_handler, 33)
    
    send_penca_handler = CommandHandler('penca', penca)
    application.add_handler(send_penca_handler, 34)
    
    send_aquimandoyo_handler = CommandHandler('aquimandoyo', aquimandoyo)
    application.add_handler(send_aquimandoyo_handler, 35)
    
    send_lloronql_handler = CommandHandler('lloronql', send_lloronql)
    application.add_handler(send_lloronql_handler, 36)
    
    send_ultraderecha_handler = CommandHandler('ultraderecha', ultraderecha)
    application.add_handler(send_ultraderecha_handler, 37)
    
    send_washitarica_handler = CommandHandler('washitarica', washitarica)
    application.add_handler(send_washitarica_handler, 38)

    send_gei_handler = CommandHandler('gei', gei)
    application.add_handler(send_gei_handler, 39)
    
    send_bala_handler = CommandHandler('bala', bala)
    application.add_handler(send_bala_handler, 40)
    
    send_compadre2_handler = CommandHandler('compadre2', compadre2)
    application.add_handler(send_compadre2_handler, 41)
    
    send_pideperdonmierda = CommandHandler('pideperdonmierda', pideperdonmierda)
    application.add_handler(send_pideperdonmierda, 42)
    
    send_insolente_handler = CommandHandler('insolente', insolente)
    application.add_handler(send_insolente_handler, 43)
    
    send_respeto_handler = CommandHandler('respeto', respeto)
    application.add_handler(send_respeto_handler, 44)
    
    send_satanas_handler = CommandHandler('satanas', satanas)
    application.add_handler(send_satanas_handler, 452)
    
    send_merluzo_handler = CommandHandler('merluzo', merluzo)
    application.add_handler(send_merluzo_handler, 45)
    
    send_comunistasculiaos = CommandHandler('comunistasculiaos', comunistasculiaos)
    application.add_handler(send_comunistasculiaos, 46)
    
    send_trabajo_handler = CommandHandler('trabajo', trabajo)
    application.add_handler(send_trabajo_handler, 47)
    
    send_archivazo = CommandHandler('archivazo', archivazo)
    application.add_handler(send_archivazo, 48)
    
    send_vistipuntos_handler =  CommandHandler('vistipuntos', vistipuntos)
    application.add_handler(send_vistipuntos_handler, 49)
    

    
    send_say_handler = CommandHandler('say', say_command)
    application.add_handler(send_say_handler, 51)
    
    

    
    application.add_handler(ChatMemberHandler(track_chats, ChatMemberHandler.MY_CHAT_MEMBER))
    application.add_handler(ChatMemberHandler(greet_chat_members, ChatMemberHandler.CHAT_MEMBER))
    
    
    send_sapo_handler = CommandHandler('sapo', send_sapo)
    application.add_handler(send_sapo_handler, 53)
    
    venecosqls_handler = CommandHandler('venecosqls', venecosqls)
    application.add_handler(venecosqls_handler, 54)

    pengu2_handler = CommandHandler('pengu2', pengu2)
    application.add_handler(pengu2_handler, 55)
    
    
    # YASTABEO APP
    to_process_filters = filters.TEXT | filters.PHOTO | filters.AUDIO | filters.VIDEO | filters.FORWARDED
    #to_process_filters = filters.TEXT | filters.PHOTO | filters.VIDEO | filters.FORWARDED
    application.add_handler(MessageHandler(to_process_filters, process))







    
application.run_polling(allowed_updates=Update.ALL_TYPES)