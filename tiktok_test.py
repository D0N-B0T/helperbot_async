from TikTokApi import TikTokApi
import requests

url = 'https://vm.tiktok.com/ZMYY3LdPG/'
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    video_id = response.text.split("/video/")[1].split("?")[0].split("/")[0]
    username = response.text.split("/video/")[0].split("https://www.tiktok.com/@")[1]
    #video_id = video_id.split("?")[0]
    
    print(video_id)
    print(username)

        
else:
    print("Error, no se pudo obtener el id del video")



