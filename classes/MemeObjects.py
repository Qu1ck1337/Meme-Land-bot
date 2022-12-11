import discord

from classes import StaticParameters
from classes.DataBase import get_meme, get_reversed_meme, get_top_meme, get_random_meme, get_user, add_viewing_to_meme
from classes.Exp import count_to_next_level


class Meme:
    def __init__(self, bot_client, meme_id: int = None):
        self.bot = bot_client
        self.meme_id = meme_id
        self.is_reverse = False
        self.is_random = True if meme_id is None else False
        self.is_top = False
        self.is_meme_exists = False
        self.meme = self.find_meme()

    def get_meme_id(self) -> int:
        return self.meme_id

    def get_author_id(self) -> int:
        return self.meme["author"]

    def meme_exist(self) -> bool:
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

    def get_embed(self, title: str="Мем") -> discord.Embed:
        author = get_user(self.meme["author"])
        if self.meme is None:
            return discord.Embed(title="Ощибка!!!",
                                 description=f"Дядя я не найти ващ меме под айди `{self.meme_id}`",
                                 colour=discord.Colour.red())

        embed = discord.Embed(
            title=f'{title}',
            description=f'{"📔 **Описание:**" if self.meme["description"] != "" else ""} {self.meme["description"]}',
            colour=discord.Colour.blue()) #discord.Colour.from_str(author["memes_color"])
        #todo убрать коментирование и exception
        try:
            views = self.meme["views"]
        except Exception:
            views = 0
        embed.add_field(name="👁️ Просмотры", value=f"```{views} 👁️```")
        embed.add_field(name="👍 Лайки", value=f'```{self.meme["likes"]} 👍```')
        embed.add_field(name="😀 Автор", value=f"```{self.bot.get_user(self.meme['author'])}```")
        # embed.add_field(name="ID мема:", value=f'{meme["meme_id"]}')
        embed.set_image(url=self.meme["url"])
        embed.set_footer(text=f"🔨 Сервер поддержки: /support | 🏷️ ID мема: {self.meme['meme_id']}", icon_url=StaticParameters.meme_land_guild.icon)

        self.meme_id = self.meme["meme_id"]
        self.is_meme_exists = True
        add_viewing_to_meme(self.meme_id)
        return embed

    # def add_like(self):
    # await DataBase.update_meme(self.meme_id, "likes", (self.meme["likes"] + 1))


class Profile:
    def __init__(self, user: discord.User):
        self.user = user

    async def get_user_profile(self):
        user = get_user(self.user.id)
        embed = discord.Embed(title="Профиль самого лучшего юзера", colour=discord.Colour.from_str(user["memes_color"]))
        embed.add_field(name="Уровень:", value=f"```{user['level']} 📈```")
        embed.add_field(name="Текущий опыт:", value=f"```{user['exp']} / {count_to_next_level(current_level=user['level'])} ⚡``` ")
        embed.add_field(name="Мемов за всё время:", value=f"```{user['memes_count']} 🗂️```")
        embed.add_field(name="Лайков за всё время:", value=f"```{user['memes_likes']} 👍```")
        embed.set_thumbnail(url=self.user.avatar)
        return embed
