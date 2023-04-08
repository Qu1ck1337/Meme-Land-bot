import urllib.request

import discord
import requests

# meme_dir = "./memes/"


def save_meme(url):
    payload = {
        "key": "72ad923255999fbbf26a5dc0b9e56419",
        "image": url
    }
    r = requests.post("https://api.imgbb.com/1/upload", payload)
    return r.json()["data"]["url"]


# memes = get_all_memes()
# for meme in memes:
#     url = meme["url"]
#     r = requests.get(url)
#     ext = url.split("/")[-1].split(".")[-1]
#     with open(f'../memes/{meme["meme_id"]}.{ext}', 'wb') as f:
#         f.write(r.content)
#         f.close()
#     # print(name)
#     # print(url)
#     # urllib.request.urlretrieve(url, f"F:\Meme_Land_Bot_Reloaded\memes\1.jpg")

# memes = get_all_memes()
# for meme in memes:
# url = "https://media.discordapp.net/attachments/766386682047365194/944896032997785672/hello-world.jpg"
# payload = {
#     "key": "72ad923255999fbbf26a5dc0b9e56419",
#     "image": url
# }
# r = requests.post("https://api.imgbb.com/1/upload", payload)
# print(r.json())

# r = requests.post("https://ibb.co/2gTWjxx/1d10942cbc49136d6839936f6def95a9")
# print(r.text)