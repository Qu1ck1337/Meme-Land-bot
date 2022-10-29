from classes import DataBase


class User:
    def __init__(self, user_id):
        self.data = {
            "id": user_id,
            "exp": 0,
            "lvl": 0,
            "memes_count": 0,
            "memes_likes": 0,
            "premium_status": False,
            "meme_color": [
                66, 170, 255
            ],
            "show_nickname": False,
            "show_tag": False,
            "show_url": False,
            "custom_url": ""
        }

    async def update_local_data(self):
        user_data = await DataBase.get_user(self.data["id"])
        for key in user_data:
            if key != "_id":
                self.data[key] = user_data[key]

    async def push_data(self):
        print("start")
        await DataBase.update_user_data(self.data)


