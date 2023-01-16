from loguru import logger
import os

def send_instagram_video(url):    
    url = url.split(" ")[1]                
    split_instagram_url = url("?")[0].split("/")
    shortcode = split_instagram_url[5]
    try:
        logger.info(f"Downloading instagram post {url}")
        os.system('bash yt-dlp/yt-dlp.sh '+ url +' -o '+shortcode+'.mp4')
    except Exception as e:
        logger.error(f"Error downloading instagram post {split_instagram_url} with shortcode {shortcode}: {e}")
        return
