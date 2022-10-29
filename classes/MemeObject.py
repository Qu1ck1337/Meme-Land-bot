import discord

from classes import StaticParameters
from classes.DataBase import get_meme, get_reversed_meme, get_top_meme, get_random_meme


class MemeObj:
    def __init__(self, meme_id: int = None):
        self.meme_id = meme_id
        self.is_reverse = False
        self.is_random = True if meme_id is None else False
        self.is_top = False
        self.is_meme_exists = False

    def get_meme_id(self):
        return self.meme_id

    def meme_exist(self):
        return self.is_meme_exists

    def get_reversed_meme_embed(self):
        self.is_reverse = True
        return self.get_embed()

    # def get_random_meme_embed(self):
    #     self.is_random = True
    #     return self.get_embed()

    def get_top_meme_embed(self):
        self.is_top = True
        return self.get_embed()

    def find_meme(self):
        if self.is_reverse: return get_reversed_meme()
        if self.is_top: return get_top_meme()
        if self.is_random: return get_random_meme()
        return get_meme(self.meme_id)

    def get_embed(self):
        meme = self.find_meme()
        if meme is None:
            return discord.Embed(title="Ощибка!!!",
                                 description=f"Дядя я не найти ващ меме под айди `{self.meme_id}`",
                                 colour=discord.Colour.red())

        embed = discord.Embed(
            title=f'Мем',
            description=f'{"📔 **Описание:**" if meme["description"] != "" else ""} {meme["description"]}',
            colour=discord.Colour.blue())
        embed.add_field(name="Просмотры:", value="None 👁️")
        embed.add_field(name="Лайки:", value=f'{meme["likes"]} 👍')
        embed.add_field(name="ID мема:", value=f'```{meme["meme_id"]}```')
        embed.set_image(url=meme["url"])
        embed.set_footer(text="Сервер поддержки: /support", icon_url=StaticParameters.meme_land_guild.icon)

        self.embed = embed
        self.meme_id = meme["meme_id"]
        self.is_meme_exists = True
        return embed

    # def add_like(self):
    # await DataBase.update_meme(self.meme_id, "likes", (self.meme["likes"] + 1))
