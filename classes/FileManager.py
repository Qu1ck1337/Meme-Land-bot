import requests


def save_meme(url):
    payload = {
        "key": "72ad923255999fbbf26a5dc0b9e56419",
        "image": url
    }
    r = requests.post("https://api.imgbb.com/1/upload", payload)
    try:
        return r.json()["data"]["url"]
    except KeyError:
        return None