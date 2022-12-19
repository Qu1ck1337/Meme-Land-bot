import asyncio
import random

import discord
import nest_asyncio

from classes import StaticParameters
from classes.DataBase import get_reversed_meme, get_top_meme, get_random_meme, get_meme, get_user, add_viewing_to_meme
from classes.Exp import count_to_next_level
nest_asyncio.apply()


christmas_emoji = ["❄", "🎄", "🎅", "<a:peeposnow:1050783484035203133>", "<a:peepochristmasdance:1050783481237606410>", "🎁"]


class Meme:
    def __init__(self, bot_client, add_view=True):
        self.bot = bot_client
        self.add_view = add_view
        self.meme_data = None

    def get_embed(self, title: str=None) -> discord.Embed:
        if self.meme_data is None:
            return discord.Embed(title="Ощибка!!!",
                                 description=f"Дядя я не найти ващ меме",
                                 colour=discord.Colour.red())
        random_emoji = random.choice(christmas_emoji)
        embed = discord.Embed(
            title=f"{random_emoji} {title} {random_emoji}" if title is not None else None,
            description=f'{"📔 **Описание:**" if self.meme_data["description"] != "" else ""} {self.meme_data["description"]}',
            colour=discord.Colour.from_str(get_user(self.meme_data['author'])["memes_color"]))
        embed.add_field(name="👁️ Просмотры", value=f"```{self.meme_data['views']} 👁️```")
        embed.add_field(name="👍 Лайки", value=f'```{self.meme_data["likes"]} 👍```')
        embed.add_field(name="😀 Автор", value=f"```{self.bot.get_user(self.meme_data['author'])}```")
        embed.set_image(url=self.meme_data["url"])
        embed.set_footer(text=f"🔨 Сервер поддержки: /support | 🏷️ ID мема: {self.meme_data['meme_id']}", icon_url=StaticParameters.main_bot_guild.icon)
        if self.add_view:
            add_viewing_to_meme(self.meme_data["meme_id"])
        return embed

    def get_meme_id(self) -> int:
        return self.meme_data["meme_id"]

    def get_author_id(self) -> int:
        return self.meme_data["author"]


def run_and_get(coro):
    task = asyncio.create_task(coro)
    asyncio.get_running_loop().run_until_complete(task)
    return task.result()


class RandomedMeme(Meme):
    def __init__(self, bot_client):
        super().__init__(bot_client)
        self.meme_data = run_and_get(get_random_meme(self.bot))


class SearchedMeme(Meme):
    def __init__(self, bot_client, meme_id: int, add_view=True):
        super().__init__(bot_client, add_view)
        self.meme_data = get_meme(meme_id)

    def is_meme_exist(self) -> bool:
        return True if self.meme_data is not None else False


class PopularMeme(Meme):
    def __init__(self, bot_client):
        super().__init__(bot_client)
        self.meme_data = get_top_meme()


class NewMeme(Meme):
    def __init__(self, bot_client):
        super().__init__(bot_client)
        self.meme_data = get_reversed_meme()


class Profile:
    def __init__(self, user: discord.User):
        self.user = user
        self.user_data = get_user(user.id)

    async def get_user_profile_embed(self):
        random_emoji = random.choice(christmas_emoji)
        embed = discord.Embed(title=f"{random_emoji} Профиль самого лучшего юзера {random_emoji}", colour=discord.Colour.from_str(self.user_data["memes_color"]))
        embed.add_field(name="Уровень:", value=f"```{self.user_data['level']} 📈```")
        embed.add_field(name="Текущий опыт:", value=f"```{self.user_data['exp']} / {count_to_next_level(current_level=self.user_data['level'])} ⚡``` ")
        embed.add_field(name="Мемов за всё время:", value=f"```{self.user_data['memes_count']} 🗂️```")
        embed.add_field(name="Лайков за всё время:", value=f"```{self.user_data['memes_likes']} 👍```")
        embed.set_thumbnail(url=self.user.avatar)
        embed.set_footer(text="🖌️ Сменить цвет своих мемов: /meme_color")
        return embed

    def get_user_memes_count(self):
        return self.user_data["memes_count"]
