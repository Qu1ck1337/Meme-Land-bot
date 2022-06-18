import datetime

import discord
import pymongo
import requests
import validators
from discord.ext import commands, tasks
from discord.ext.commands import Cog
from pymongo import MongoClient

from config import meme_rus_settings, settings, beta_settings, profile_settings, economySettings, release_settings
import random
from discord import app_commands, HTTPException

# Provide the mongodb atlas url to connect python to mongodb using pymongo
CONNECTION_STRING = \
    "mongodb+srv://dbBot:j5x-Pkq-Q8u-mW2@data.frvp6.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
# Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
client = MongoClient(CONNECTION_STRING)

db_profile = client[profile_settings["db_profile"]]
profile_collection = db_profile[profile_settings["collection_profile"]]

db_memes = client['bot_memes'] #bot_memes
accepted_memes_collection = db_memes["accepted_memes"] #accepted_memes
memes_on_moderation_collection = db_memes["memes_on_moderation"] #memes_on_moderation

db_auto_post_guilds = client['auto_post_guilds']
auto_post_guilds_collection = db_auto_post_guilds["guilds"]


class NextButton(discord.ui.View):
    def __init__(self, *, timeout=180, bot, cursor):
        self.bot = bot
        self.cursor = cursor
        self.author_meme = self.cursor.next()
        self.is_next = True
        super().__init__(timeout=timeout)

    @discord.ui.button(label="Следующий мем", style=discord.ButtonStyle.green)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.is_next:
            meme_embed = Create_meme_embed_message(self.bot, interaction, self.author_meme)
            try:
                self.author_meme = self.cursor.next()
                await interaction.response.edit_message(embed=meme_embed, view=self)
            except StopIteration:
                self.is_next = False
                button.style = discord.ButtonStyle.gray
                button.label = "Мемы закончились"
                button.disabled = True
                await interaction.response.edit_message(embed=meme_embed, view=self)


class LikeButton(discord.ui.View):
    def __init__(self, *, timeout=180, interaction: discord.Interaction, collection_name, meme_id):
        # Provide the mongodb atlas url to connect python to mongodb using pymongo
        self.CONNECTION_STRING = \
            "mongodb+srv://dbBot:j5x-Pkq-Q8u-mW2@data.frvp6.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
        # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
        self.client = MongoClient(self.CONNECTION_STRING)
        self.interaction = interaction
        self.collection_name = collection_name
        self.meme_id = meme_id
        super().__init__(timeout=timeout)

    @discord.ui.button(label="Лайкнуть мем", style=discord.ButtonStyle.blurple)
    async def likeButton(self, interaction_b: discord.Interaction, button: discord.ui.Button):
        if interaction_b.user == self.interaction.user:
            result = self.collection_name.find_one({"meme_id": self.meme_id})
            if result is not None:
                self.collection_name.update_one(result, {"$set": {"likes": result["likes"] + 1}})

            author_res = profile_collection.find_one({"user_id": self.interaction.user.id})

            if author_res is None:
                Create_user_profile(self.interaction.user.id)
                author_res = profile_collection.find_one({"user_id": self.interaction.user.id})
            profile_collection.update_one(author_res, {"$set": {"memes_likes": author_res["memes_likes"] + 1}})

            button.disabled = True
            button.label = "Мем лайкнут 👍"
            await interaction_b.response.edit_message(view=self)
            print(
                f"{datetime.datetime.now().strftime('%H:%M:%S')} | [USER] User {self.interaction.user} liked post with "
                f"{self.meme_id} id")


class RandomMemeButton(discord.ui.View):
    def __init__(self, *, timeout=180, bot, interaction: discord.Interaction, collection_name, meme_id):
        # Provide the mongodb atlas url to connect python to mongodb using pymongo
        self.CONNECTION_STRING = \
            "mongodb+srv://dbBot:j5x-Pkq-Q8u-mW2@data.frvp6.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
        # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
        self.client = MongoClient(self.CONNECTION_STRING)
        self.bot = bot
        self.interaction = interaction
        self.collection_name = collection_name
        self.meme_id = meme_id
        self.likeButton = None
        super().__init__(timeout=timeout)

    @discord.ui.button(label="Случайный мем", style=discord.ButtonStyle.green)
    async def randomMemeButton(self, interaction_b: discord.Interaction, button: discord.ui.Button):
        if interaction_b.user.id == self.interaction.user.id:
            random_record = None
            search = True
            while search:
                result_r = self.collection_name.aggregate([{"$sample": {"size": 1}}])
                for res in result_r:
                    if await self.valid_meme_checker(res["url"]):
                        search = False
                        random_record = res

            meme_embed = Create_meme_embed_message(self.bot, interaction_b, random_record)

            if self.likeButton is not None:
                self.likeButton.label = "Лайкнуть мем"
                self.likeButton.disabled = False

            await interaction_b.response.edit_message(embed=meme_embed, view=self)
            self.meme_id = random_record["meme_id"]

            user_res = profile_collection.find_one({"user_id": self.interaction.user.id})
            if user_res is None:
                Create_user_profile(self.interaction.user.id)
                user_res = profile_collection.find_one({"user_id": self.interaction.user.id})
            await Add_user_exp(self.interaction, user_res, random.randint(1, 5))

    @discord.ui.button(label="Лайкнуть мем", style=discord.ButtonStyle.blurple)
    async def likeButton(self, interaction_b: discord.Interaction, button: discord.ui.Button):
        if interaction_b.user.id == self.interaction.user.id:
            result = self.collection_name.find_one({"meme_id": self.meme_id})
            if result is not None:
                self.collection_name.update_one(result, {"$set": {"likes": result["likes"] + 1}})

            author_res = profile_collection.find_one({"user_id": self.interaction.user.id})

            if author_res is None:
                Create_user_profile(self.interaction.user.id)
                author_res = profile_collection.find_one({"user_id": self.interaction.user.id})
            profile_collection.update_one(author_res, {"$set": {"memes_likes": author_res["memes_likes"] + 1}})

            button.disabled = True
            button.label = "Мем лайкнут 👍"
            self.likeButton = button
            await interaction_b.response.edit_message(view=self)

            print(
                f"{datetime.datetime.now().strftime('%H:%M:%S')} | [USER] User {self.interaction.user} liked post with "
                f"{self.meme_id} id")

    async def valid_meme_checker(self, url):
        check = requests.head(url)
        if check.status_code == 403 or check.status_code == 404:
            await self.delete_meme_after_validation(url=url)
            return False
        else:
            return True

    async def delete_meme_after_validation(self, url):
        meme_res = accepted_memes_collection.find_one({"url": url})
        if meme_res is not None:
            result_user = profile_collection.find_one({"user_id": meme_res["author"]})
            if result_user is None:
                Create_user_profile(meme_res["author"])
                result_user = profile_collection.find_one({"user_id": meme_res["author"]})
            #profile_collection.update_one(result_user,
            #                              {"$set": {"memes_count": result_user["memes_count"] - 1,
            #                                        "memes_likes": result_user["memes_likes"] - meme_res["likes"]}})
            accepted_memes_collection.delete_one(meme_res)

            user = self.bot.get_user(meme_res["author"])
            if user is not None:
                channel = await user.create_dm()

                embed = discord.Embed(title="Ваш мем был удалён",
                                      description=f"Нам пришлось удалить ваш мем c ID: **{meme_res['meme_id']}**",
                                      color=0xff0000)
                embed.add_field(name="Причина:", value='Мема не существует, оригинал был удалён')

                meme_embed = discord.Embed(title="Удалённый мем", description=meme_res["description"], color=0xff0000)
                meme_embed.set_image(url=meme_res["url"])
                try:
                    await channel.send(embed=embed)
                    await channel.send(embed=meme_embed)
                except discord.errors.Forbidden:
                    pass


def Create_user_profile(author_id):
    result = accepted_memes_collection.find({"author": author_id})

    meme_count = 0
    likes = 0

    for meme in result:
        meme_count += 1
        likes += meme["likes"]

    profile_collection.insert_one({
        "user_id": author_id,
        "level": 0,
        "exp": 0,
        "memes_count": meme_count,
        "memes_likes": likes,
        "premium_status": False,
        "meme_color": [66, 170, 255],
        "show_nickname": False,
        "show_tag": False,
        "show_url": False,
        "custom_url": ""
    })


async def Add_user_exp(interaction: discord.Interaction, user_data, add_exp):
    exp_to_new_level = user_data["level"] * 100 + 100
    if user_data["premium_status"]:
        exp = user_data["exp"] + (add_exp * 2)
    else:
        exp = user_data["exp"] + add_exp
    update_level = True
    level = 0
    while update_level:
        if exp >= exp_to_new_level:
            exp -= exp_to_new_level
            level += 1
            exp_to_new_level += 100
        else:
            update_level = False
    if level != 0:
        level += user_data["level"]
        profile_collection.update_one(user_data, {"$set": {"level": level, "exp": exp}})
        await interaction.channel.send(
            f"{interaction.user.mention} Поздравляю, теперь у тебя **{level} уровень** мемерства! 🥳 🥳 🥳 ")
    else:
        profile_collection.update_one(user_data, {"$set": {"exp": exp}})


def Check_if_it_is_me(interaction: discord.Interaction) -> bool:
    return interaction.user.id == 443337837455212545


def Create_meme_embed_message(bot, interaction: discord.Interaction, result, title_text=None):
    default_color = discord.Colour.from_rgb(r=66, g=170, b=255)
    current_color = default_color
    premium_user = False
    premium_author = False

    meme_author = profile_collection.find_one({"user_id": result["author"]})
    if meme_author is not None and meme_author["premium_status"]:
        premium_author = True
        if meme_author["meme_color"] is not None:
            color_user = meme_author["meme_color"]
            current_color = discord.Colour.from_rgb(color_user[0], color_user[1], color_user[2])

    user_data = profile_collection.find_one({"user_id": interaction.user.id})
    if user_data is not None and user_data["premium_status"]:
        premium_user = True

    try:
        embed = discord.Embed(
            title=f'{random.choice(meme_rus_settings["get_meme_phrases"]) if title_text is None else title_text}',
            description=result["description"], colour=current_color, url=f'{meme_author["custom_url"] if premium_author and meme_author["show_url"] else ""}')
        embed.add_field(name="Лайки:", value=f'{result["likes"]} 👍')
        embed.add_field(name="ID мема:", value=f'**{result["meme_id"]}**')
        embed.set_image(url=result["url"])

        if premium_author:
            if meme_author["show_nickname"]:
                if meme_author["show_tag"]:
                    embed.add_field(name="Автор:", value=f"**{bot.get_user(meme_author['user_id']) if bot.get_user(meme_author['user_id']) else 'user id: ' + str(meme_author['user_id'])}**")
                else:
                    embed.add_field(name="Автор:",
                                    value=f"**{bot.get_user(meme_author['user_id']).display_name if bot.get_user(meme_author['user_id']) else 'user id: ' + str(meme_author['user_id'])}**")

        if premium_user:
            embed.set_footer(text=f'Запрошено в {datetime.datetime.now().strftime("%H:%M:%S")}')
            return embed
        embed.set_footer(text=f"Сервер поддержки: "
                              f"\nhttps://discord.gg/VB3CgP9XTW"
                              f"\n{random.choice(meme_rus_settings['advise_phrases'])}",
                         icon_url=bot.get_guild(meme_rus_settings["guild"]).icon)
        return embed
    except TypeError:
        for res in result:
            embed = discord.Embed(
                title=f'{random.choice(meme_rus_settings["get_meme_phrases"]) if title_text is None else title_text}',
                description=res["description"], colour=current_color, url=f'{user_data["custom_url"] if premium_author and user_data["show_url"] else None}')
            embed.add_field(name="Лайки:", value=f'{res["likes"]} 👍')
            embed.add_field(name="ID мема:", value=f'**{res["meme_id"]}**')
            embed.set_image(url=res["url"])

            if premium_author:
                if meme_author["show_nickname"]:
                    if meme_author["show_tag"]:
                        embed.add_field(name="Автор:",
                                        value=f"**{bot.get_user(meme_author['user_id']) if bot.get_user(meme_author['user_id']) else 'user id: ' + str(meme_author['user_id'])}**")
                    else:
                        embed.add_field(name="Автор:",
                                        value=f"**{bot.get_user(meme_author['user_id']).display_name if bot.get_user(meme_author['user_id']) else 'user id: ' + str(meme_author['user_id'])}**")
                    embed.set_footer(text=f'Запрошено в {datetime.datetime.now().strftime("%H:%M:%S")}')

            if premium_user:
                embed.set_footer(text=f'Запрошено в {datetime.datetime.now().strftime("%H:%M:%S")}')
                return embed
            embed.set_footer(text=f"Сервер поддержки: "
                                  f"\nhttps://discord.gg/VB3CgP9XTW"
                                  f"\n{random.choice(meme_rus_settings['advise_phrases'])}",
                             icon_url=bot.get_guild(meme_rus_settings["guild"]).icon)
            return embed


def Loading_Embed():
    embed = discord.Embed(title="Загружаюсь...",
                         description=f"Ищу для вас мемчик <a:loading:971033648956579840>",
                         color=0x42aaff)
    embed.set_footer(text=f"🔥 Интересный факт: {random.choice(meme_rus_settings['loading_phrases'])}")
    return embed


class Meme_Rus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.moderation_channel = None
        self.post_meme = False

    @Cog.listener("on_ready")
    async def on_ready(self):
        self.moderation_channel = self.bot.get_guild(meme_rus_settings["guild"]).get_channel(
            meme_rus_settings["moderationChannel"])
        self.auto_post_meme.start()

    @app_commands.command(description="Посмотреть свой мемный профиль")
    async def profile(self, interaction: discord.Interaction):
        result = profile_collection.find_one({"user_id": interaction.user.id})

        if result is None:
            Create_user_profile(interaction.user.id)
            result = profile_collection.find_one({"user_id": interaction.user.id})
        await Add_user_exp(interaction, result, 0)
        result = profile_collection.find_one({"user_id": interaction.user.id})

        default_color = discord.Colour.from_rgb(r=66, g=170, b=255)
        current_color = default_color
        if result["premium_status"]:
            r = result['meme_color'][0]
            g = result['meme_color'][1]
            b = result['meme_color'][2]
            current_color = discord.Colour.from_rgb(r=r, g=g, b=b)

        embed = discord.Embed(title=f"Профиль пользователя {interaction.user.display_name}", colour=current_color)
        embed.add_field(name="Уровень:", value=result["level"], inline=True)
        embed.add_field(name="Текущий опыт:", value=f'{result["exp"]} **/** {result["level"] * 100 + 100}', inline=True)
        embed.add_field(name="Мемов за всё время:", value=f'{result["memes_count"]} 🗂️', inline=True)
        embed.add_field(name="Лайков за всё время:", value=f'{result["memes_likes"]} 👍', inline=True)

        if result["premium_status"]:
            embed.add_field(name="Поддержка бота до:", value=f'`🚀 {result["premium_status_end"].strftime("%d.%m.%Y")}`', inline=True)

        embed.set_thumbnail(url=interaction.user.avatar)

        test_meme = accepted_memes_collection.find_one({"author": interaction.user.id})

        if test_meme is None:
            await interaction.response.send_message(embed=embed)
            await interaction.channel.send(f"Мемов пока ещё нет =("
                                           f"\nОтправить мемы можно с помощью команды "
                                           f"`/send_meme <описание мема> + картинка`")
            return

        cursor = accepted_memes_collection.find({"author": interaction.user.id})

        author_memes = cursor.next()
        meme_embed = Create_meme_embed_message(self.bot, interaction, author_memes)
        await interaction.response.send_message(embed=embed)
        await interaction.channel.send(embed=meme_embed, view=NextButton(bot=self.bot, cursor=cursor))

    @app_commands.command(name="send_meme", description="Отправить мемы")
    @app_commands.describe(description="Описание мема")
    @app_commands.describe(meme="Мем (.png .jpg .gif .jpeg)")
    async def send_meme(self, interaction: discord.Interaction, meme: discord.Attachment, description: str = ""):
        if interaction.user.bot:
            return

        if meme.url.split('.')[-1].lower() not in ['png', 'jpg', 'gif', 'jpeg']:
            await interaction.response.send_message("Бот не поддерживает тип данного файла")
            return
        if memes_on_moderation_collection.find_one({"url": meme.url}) is None:
            embed = discord.Embed(title="Новый мем на модерацию", description=description, color=0xFFCC33)
            embed.add_field(name="Сервер:", value=f"{interaction.guild}")
            embed.add_field(name="Автор:", value=f"{interaction.user}")

            embed.set_image(url=meme)
            msg = await self.moderation_channel.send(embed=embed)

            await msg.add_reaction("✅")
            await msg.add_reaction("❌")
            print(interaction.guild_id)

            memes_on_moderation_collection.insert_one(
                {
                    "url": meme.url,
                    "msg_id": msg.id,
                    "author": interaction.user.id,
                    "description": description,
                    "guild": interaction.guild_id,
                })
            embed = discord.Embed(title="Исходный мем", description=description, color=0xFFCC33)
            embed.set_image(url=meme)
            embed.set_footer(text=f"Сервер поддержки: "
                                  f"\nhttps://discord.gg/VB3CgP9XTW",
                             icon_url=self.bot.get_guild(meme_rus_settings["guild"]).icon)
            await interaction.response.send_message("Ваш мем отправлен на модерацию =)"
                                                    "\n**ПРОСЬБА НЕ УДАЛЯТЬ МЕМ, ИНАЧЕ ОН БУДЕТ УДАЛЁН С БОТА**",
                                                    embed=embed)
        else:
            await interaction.response.send_message("Такой мем уже есть")

    @app_commands.command(name="meme", description="Посмотреть мем")
    @app_commands.describe(meme_id="ID мема")
    async def meme(self, interaction: discord.Interaction, meme_id: int = None):
        if interaction.guild.id == settings["guild"] and \
                interaction.channel.id in settings["ignored_commands_channels"]:
            await interaction.response.send_message(embed=discord.Embed(
                title="Ошибка",
                description="Данная команда недоступна на этом канале, чтобы смотреть мемчики переходи в "
                            "<#968940291904114769>)",
                color=economySettings["error_color"]))
            return

        await interaction.response.send_message(embed=Loading_Embed())
        #try:
        random_record = None
        if meme_id is None:
            search = True
            while search:
                random_m = accepted_memes_collection.aggregate([{"$sample": {"size": 1}}])
                for res in random_m:
                    if await self.valid_meme_checker(res["url"]):
                        search = False
                        random_record = res
        else:
            embed_not_founded_meme = discord.Embed(title="Ошибка",
                                                   description="Мема с таким ID не существует :(",
                                                   color=0xff0000)
            if accepted_memes_collection.find_one({"meme_id": meme_id}) is None:
                await interaction.edit_original_message(embed=embed_not_founded_meme)
                return
            random_record = accepted_memes_collection.find_one({"meme_id": meme_id})
            if not await self.valid_meme_checker(random_record["url"]):
                await interaction.edit_original_message(embed=embed_not_founded_meme)
                return

        embed = Create_meme_embed_message(self.bot, interaction, random_record)

        if meme_id is None:
            await interaction.edit_original_message(embed=embed,
                                                    view=RandomMemeButton(interaction=interaction,
                                                                          collection_name=accepted_memes_collection,
                                                                          meme_id=random_record["meme_id"],
                                                                          bot=self.bot))
        else:
            await interaction.edit_original_message(embed=embed,
                                                    view=LikeButton(interaction=interaction,
                                                                    collection_name=accepted_memes_collection,
                                                                    meme_id=random_record["meme_id"]))

        user_res = profile_collection.find_one({"user_id": interaction.user.id})
        if user_res is None:
            Create_user_profile(interaction.user.id)
            user_res = profile_collection.find_one({"user_id": interaction.user.id})
        await Add_user_exp(interaction, user_res, random.randint(1, 5))

        print(
            f"{datetime.datetime.now().strftime('%H:%M:%S')} | [USER] User {interaction.user} used <meme> command")
        #except Exception:
            #await interaction.edit_original_message(content="Произошла ошибка во время выполнения команды, обратитесь к"
            #                                                " разработчику - https://discord.gg/VB3CgP9XTW", embed=None)

    @app_commands.command(name="last_meme", description="Посмотреть последний одобренный мем")
    async def last_meme(self, interaction: discord.Interaction):
        if interaction.guild.id == settings["guild"] and \
                interaction.channel.id in settings["ignored_commands_channels"]:
            await interaction.response.send_message(embed=discord.Embed(
                title="Ошибка",
                description="Данная команда недоступна на этом канале, чтобы смотреть мемчики переходи в "
                            "<#968940291904114769>)",
                color=economySettings["error_color"]))
            return

        await interaction.response.send_message(embed=Loading_Embed())

        last_meme_result = accepted_memes_collection.find().sort('meme_id', -1).limit(1)
        for last_meme in last_meme_result:
            embed = Create_meme_embed_message(self.bot, interaction, last_meme, "Самый свежий мемчик для тебя! 🍞")
            await interaction.edit_original_message(embed=embed, view=LikeButton(interaction=interaction,
                                                                                 collection_name=accepted_memes_collection,
                                                                                 meme_id=last_meme["meme_id"]))

            user_res = profile_collection.find_one({"user_id": interaction.user.id})
            if user_res is None:
                Create_user_profile(interaction.user.id)
                user_res = profile_collection.find_one({"user_id": interaction.user.id})
            await Add_user_exp(interaction, user_res, random.randint(1, 5))

        print(
            f"{datetime.datetime.now().strftime('%H:%M:%S')} | [USER] User {interaction.user} used <last_meme> command")

    @app_commands.command(name="top_meme", description="Посмотреть самый залайканный мем")
    async def top_meme(self, interaction: discord.Interaction):
        if interaction.guild.id == settings["guild"] and \
                interaction.channel.id in settings["ignored_commands_channels"]:
            await interaction.response.send_message(embed=discord.Embed(
                title="Ошибка",
                description="Данная команда недоступна на этом канале, чтобы смотреть мемчики переходи в "
                            "<#968940291904114769>)",
                color=economySettings["error_color"]))
            return

        await interaction.response.send_message(embed=Loading_Embed())

        last_meme = accepted_memes_collection.find().sort('likes', -1).limit(1)
        for result in last_meme:
            embed = Create_meme_embed_message(self.bot, interaction, result, "Самый лучший мем! 🏆")
            await interaction.edit_original_message(embed=embed,
                                                    view=LikeButton(interaction=interaction,
                                                                    collection_name=accepted_memes_collection,
                                                                    meme_id=result["meme_id"]))

            user_res = profile_collection.find_one({"user_id": interaction.user.id})
            if user_res is None:
                Create_user_profile(interaction.user.id)
                user_res = profile_collection.find_one({"user_id": interaction.user.id})
            await Add_user_exp(interaction, user_res, random.randint(1, 5))

            print(
                f"{datetime.datetime.now().strftime('%H:%M:%S')} | [USER] User {interaction.user} used "
                f"<top_meme> command")

    @Cog.listener("on_raw_reaction_add")
    async def on_raw_reaction_add(self, payload):
        if payload.member.bot:
            return
        message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
        author = message.author
        if (author.id == release_settings["id"] or author.id == beta_settings["id"]) and str(payload.emoji) == "👍":
            result = accepted_memes_collection.find_one({"url": message.embeds[0].image.url})
            if result is not None:
                accepted_memes_collection.update_one(result, {"$set": {"likes": result["likes"] + 1}})

                meme_id = int(message.embeds[0].fields[1].value.replace("**", ""))
                meme_res = accepted_memes_collection.find_one({"meme_id": meme_id})

                author_res = profile_collection.find_one({"user_id": meme_res["author"]})

                if author_res is None:
                    Create_user_profile(meme_res["author"])
                    author_res = profile_collection.find_one({"user_id": meme_res["author"]})
                profile_collection.update_one(author_res, {"$set": {"memes_likes": author_res["memes_likes"] + 1}})

                print(
                    f"{datetime.datetime.now().strftime('%H:%M:%S')} | [USER] User {payload.member} liked post with "
                    f"{meme_id} id")
        elif payload.channel_id == meme_rus_settings["moderationChannel"] and str(payload.emoji) == "✅" and \
                (author.id == release_settings["id"] or author.id == beta_settings["id"]):
            if message.guild.id != meme_rus_settings["guild"]:
                return

            result = memes_on_moderation_collection.find_one({"msg_id": message.id})
            if result is not None:
                last_meme = accepted_memes_collection.find().sort('_id', -1).limit(1)
                meme_id = 0
                for rslt in last_meme:
                    meme_id = rslt["meme_id"] + 1

                accepted_memes_collection.insert_one({
                    "url": result["url"],
                    "author": result["author"],
                    "description": result["description"],
                    "likes": 0,
                    "meme_id": meme_id
                })

                result_user = profile_collection.find_one({"user_id": result["author"]})
                if result_user is None:
                    Create_user_profile(result["author"])
                    result_user = profile_collection.find_one({"user_id": result["author"]})
                profile_collection.update_one(result_user, {"$set": {"memes_count": result_user["memes_count"] + 1,
                                                                     "exp": result_user["exp"] + 25}})

                user = self.bot.get_user(result["author"])
                if user is not None:
                    channel = await user.create_dm()
                    embed = discord.Embed(title="Мем", description=result["description"], color=0x33FF66)
                    embed.add_field(name="ID мема", value=f"**{meme_id}**")
                    embed.add_field(name="Одобрил модератор", value=f"{payload.member}")
                    embed.set_image(url=result["url"])
                    try:
                        await channel.send(embed=discord.Embed(title="Ваш мем был одобрен!",
                                                               description="Поздравляем, ваш мем был одобрен ^-^! "
                                                                           "Из-за политики безопасности дискорда мы не "
                                                                           "гарантируем, что ваш мем сможет пробыть "
                                                                           "у бота более **2х** недель.",
                                                               color=0x33FF66))
                        await channel.send(embed=embed)
                    except discord.errors.Forbidden:
                        pass

                meme_channel = self.bot.get_guild(meme_rus_settings["guild"]).get_channel(
                    meme_rus_settings["meme_accepted_channel"])
                embed = discord.Embed(title="Новый мем!", description=result["description"], color=0x42aaff)
                embed.add_field(name="ID мема", value=f"**{meme_id}**")
                embed.add_field(name="Одобрил модератор", value=f"{payload.member}")
                embed.set_image(url=result["url"])
                await meme_channel.send(embed=embed)

                memes_on_moderation_collection.delete_one(result)

                msg = await message.channel.send("Мем принят")
                await msg.delete(delay=30)
                await message.delete()
                print(f"{datetime.datetime.now().strftime('%H:%M:%S')} | [MODERATION] accepted meme with id: "
                      f"{meme_id}")
            else:
                await message.channel.send("Такого мема нет в модерации")
        elif payload.channel_id == meme_rus_settings["moderationChannel"] and str(payload.emoji) == "❌" and \
                (author.id == release_settings["id"] or author.id == beta_settings["id"]):
            if message.guild.id != meme_rus_settings["guild"]:
                return

            result = memes_on_moderation_collection.find_one({"msg_id": message.id})
            if result is not None:
                user = self.bot.get_user(result["author"])
                if user is not None:
                    channel = await user.create_dm()
                    embed = discord.Embed(title="Мем", description=result["description"], color=0xff0000)
                    embed.add_field(name="Отклонил модератор", value=f"{payload.member}")
                    embed.set_image(url=result["url"])
                    try:
                        await channel.send(embed=discord.Embed(title="Мем отклонён",
                                                               description="Модерация бота отклонила ваш мем.",
                                                               color=0xff0000))
                        await channel.send(embed=embed)
                    except discord.errors.Forbidden:
                        pass

                memes_on_moderation_collection.delete_one(result)
                msg = await message.channel.send("Мем отклонён")
                await msg.delete(delay=30)
                await message.delete()
                print(f"{datetime.datetime.now().strftime('%H:%M:%S')} | [MODERATION] declined meme")
            else:
                await message.channel.send("Такого мема нет в модерации")

    @Cog.listener("on_raw_reaction_remove")
    async def on_raw_reaction_remove(self, payload):
        message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
        author = message.author
        if (author.id == release_settings["id"] or author.id == beta_settings["id"]) and str(payload.emoji) == "👍":
            result = accepted_memes_collection.find_one({"url": message.embeds[0].image.url})
            if result is not None:
                accepted_memes_collection.update_one(result, {"$set": {"likes": result["likes"] - 1}})

                meme_id = int(message.embeds[0].fields[1].value.replace("**", ""))
                meme_res = accepted_memes_collection.find_one({"meme_id": meme_id})

                author_res = profile_collection.find_one({"user_id": meme_res["author"]})

                if author_res is None:
                    Create_user_profile(meme_res["author"])
                    author_res = profile_collection.find_one({"user_id": meme_res["author"]})
                profile_collection.update_one(author_res, {"$set": {"memes_likes": author_res["memes_likes"] - 1}})
            print(
                f"{datetime.datetime.now().strftime('%H:%M:%S')} | [USER] User {payload.member} "
                f"removed like from post with {result['meme_id']} id")

    @app_commands.command(description="Устанавливает автопостинг мемов раз в 30 минут")
    @app_commands.describe(channel="Канал, где нужно постить мемы (по умолчанию этот канал)")
    @app_commands.checks.has_permissions(administrator=True, manage_guild=True)
    async def auto_meme(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        if channel is None:
            channel = interaction.channel
        result = auto_post_guilds_collection.find_one({"guild_id": interaction.guild_id})
        if result is None:
            auto_post_guilds_collection.insert_one({
                "guild_id": interaction.guild_id,
                "channel_id": channel.id
            })
            await interaction.response.send_message(f"Автопостинг мемов успешно установлен на канале: "
                                                    f"{channel.mention}")
        else:
            if result["channel_id"] != channel.id:
                auto_post_guilds_collection.update_one(result, {"$set": {"channel_id": channel.id}})
                await interaction.response.send_message(f"Автопостинг мемов успешно установлен на канале: "
                                                        f"{channel.mention}")
            else:
                await interaction.response.send_message("На данном канале уже установлен автопостинг мемов")

        print(f"{datetime.datetime.now().strftime('%H:%M:%S')} | [USER] User {interaction.user} set auto post meme")

    @app_commands.command(description="Останавливает автопостинг мемов на этом сервере")
    @app_commands.checks.has_permissions(administrator=True, manage_guild=True)
    async def stop_auto_meme(self, interaction: discord.Interaction):
        result = auto_post_guilds_collection.find_one({"guild_id": interaction.guild_id})
        if result is not None:
            auto_post_guilds_collection.delete_one(result)
            await interaction.response.send_message(f"Автопостинг мемов на этом сервере приостановлен :(")
        else:
            await interaction.response.send_message(f"На вашем сервере не был включён автопостинг мемов")

        print(f"{datetime.datetime.now().strftime('%H:%M:%S')} | [USER] User {interaction.user} "
              f"stopped auto meme posting")

    @tasks.loop(minutes=30)
    async def auto_post_meme(self):
        if self.post_meme is not True:
            self.post_meme = True
            return
        print(f"{datetime.datetime.now().strftime('%H:%M:%S')} | [INFO] Auto posting meme on servers")
        results = auto_post_guilds_collection.find()
        for result in results:
            try:
                guild = self.bot.get_guild(result["guild_id"])
                channel = guild.get_channel(result["channel_id"])

                search = True
                meme_result = None
                while search:
                    meme_r = accepted_memes_collection.aggregate([{"$sample": {"size": 1}}])
                    for res in meme_r:
                        if await self.valid_meme_checker(res["url"]):
                            search = False
                            meme_result = res

                embed = discord.Embed(
                    title=f'А вот и мем каждые 30 минут) <a:trippepe:901514564900913262>',
                    description=meme_result["description"], color=0x42aaff)
                embed.add_field(name="Лайки:", value=f'{meme_result["likes"]} 👍')
                embed.add_field(name="ID мема:", value=f'**{meme_result["meme_id"]}**')
                embed.set_image(url=meme_result["url"])
                embed.set_footer(text=f"Сервер поддержки: "
                                      f"\nhttps://discord.gg/VB3CgP9XTW"
                                      f"\n{random.choice(meme_rus_settings['advise_phrases'])}",
                                 icon_url=self.bot.get_guild(meme_rus_settings["guild"]).icon)
                msg = await channel.send(embed=embed)
                await msg.add_reaction("👍")
            except Exception:
                pass

    @app_commands.command()
    @app_commands.check(Check_if_it_is_me)
    @app_commands.guilds(892493256129118260)
    @app_commands.describe(meme_id="id мема")
    @app_commands.describe(content="Описание причины")
    async def delete_meme(self, interaction: discord.Interaction, meme_id: int, content: str):
        meme_res = accepted_memes_collection.find_one({"meme_id": meme_id})
        if meme_res is not None:
            user = self.bot.get_user(meme_res["author"])
            await user.create_dm()
            embed = discord.Embed(title="Ваш мем был удалён",
                                  description=f"Нам пришлось удалить ваш мем c ID: **{meme_id}**",
                                  color=0xff0000)
            embed.add_field(name="Причина:", value=f'{content}')
            embed.add_field(name="Модератор:", value=interaction.user.display_name)

            result_user = profile_collection.find_one({"user_id": meme_res["author"]})
            if result_user is None:
                Create_user_profile(user.id)
                result_user = profile_collection.find_one({"user_id": user.id})
            profile_collection.update_one(result_user,
                                          {"$set": {"memes_count": result_user["memes_count"] - 1,
                                                    "memes_likes": result_user["memes_likes"] - meme_res["likes"]}})

            accepted_memes_collection.delete_one(meme_res)

            meme_embed = discord.Embed(title="Удалённый мем", description=meme_res["description"], color=0xff0000)
            meme_embed.set_image(url=meme_res["url"])

            try:
                await user.send(embed=embed)
                await user.send(embed=meme_embed)
            except discord.errors.Forbidden:
                pass

            await interaction.response.send_message(f"Мем с ID {meme_id} был удалён. Пользователь уведомлён об этом.")
        else:
            await interaction.response.send_message(
                embed=discord.Embed(title="Ошибка!",
                                    description=f"Мем с ID **{meme_id}** не существует!",
                                    color=0xff0000))

    @app_commands.command(description="Таблица лидеров")
    async def leaderboard(self, interaction: discord.Interaction):
        result = profile_collection.find().sort([("level", pymongo.DESCENDING), ("exp", pymongo.DESCENDING)]).limit(10)
        embed = discord.Embed(title="Топ-10 лучших мемеров бота Meme Land", color=0x42aaff)
        for num, rez in enumerate(result):
            embed.add_field(
                name=f"**{'🥇 ' if num == 0 else '🥈 ' if num == 1 else '🥉 ' if num == 2 else ''}{num + 1}. {self.bot.get_user(rez['user_id']).name if self.bot.get_user(rez['user_id']) else 'user id: ' + str(rez['user_id'])}**",
                value=f"**{rez['level']}** уровень | **{rez['memes_count']}** 🗂️ | **{rez['memes_likes']}** 👍", inline=False)
        embed.set_thumbnail(url=interaction.guild.icon)
        embed.set_footer(text=f"Запрошено {interaction.user.name} в {datetime.datetime.now().strftime('%H:%M')}",
                         icon_url=interaction.user.avatar)

        await interaction.response.send_message(embed=embed)

    async def valid_meme_checker(self, url):
        check = requests.head(url)
        if check.status_code == 403 or check.status_code == 404:
            await self.delete_meme_after_validation(url=url)
            return False
        else:
            return True

    async def delete_meme_after_validation(self, url):
        meme_res = accepted_memes_collection.find_one({"url": url})
        if meme_res is not None:
            result_user = profile_collection.find_one({"user_id": meme_res["author"]})
            if result_user is None:
                Create_user_profile(meme_res["author"])
                result_user = profile_collection.find_one({"user_id": meme_res["author"]})
            #profile_collection.update_one(result_user,
            #                              {"$set": {"memes_count": result_user["memes_count"] - 1,
            #                                        "memes_likes": result_user["memes_likes"] - meme_res["likes"]}})
            accepted_memes_collection.delete_one(meme_res)

            user = self.bot.get_user(meme_res["author"])
            if user is not None:
                channel = await user.create_dm()

                embed = discord.Embed(title="Ваш мем был удалён",
                                      description=f"Нам пришлось удалить ваш мем c ID: **{meme_res['meme_id']}**",
                                      color=0xff0000)
                embed.add_field(name="Причина:", value='Мема не существует, оригинал был удалён')

                meme_embed = discord.Embed(title="Удалённый мем", description=meme_res["description"], color=0xff0000)
                meme_embed.set_image(url=meme_res["url"])
                try:
                    await channel.send(embed=embed)
                    await channel.send(embed=meme_embed)
                except discord.errors.Forbidden:
                    pass

    @app_commands.command()
    @app_commands.check(Check_if_it_is_me)
    @app_commands.guilds(892493256129118260)
    async def delete_all_non_validate_memes(self, interaction: discord.Interaction):
        memes = accepted_memes_collection.find()
        for meme in memes:
            print(meme["meme_id"], await self.valid_meme_checker(meme["url"]))
        print("Done!")

    @app_commands.command()
    @app_commands.check(Check_if_it_is_me)
    @app_commands.guilds(892493256129118260)
    async def backup(self, interaction: discord.Interaction):
        memes = accepted_memes_collection.find()
        db_memes["backup_accepted_memes"].insert_many(memes)

    @app_commands.command(description="[Только для поддеравших] Настроить цвет ваших мемов, параметр RGB")
    @app_commands.describe(red="Параметр красного")
    @app_commands.describe(green="Параметр зелёного")
    @app_commands.describe(blue="Параметр синего")
    async def meme_color(self, interaction: discord.Interaction, red: int, green: int, blue: int):
        red = red % 256
        blue = blue % 256
        green = green % 256
        user = profile_collection.find_one({"user_id": interaction.user.id})
        if user is not None and user["premium_status"]:
            profile_collection.update_one(user, {"$set": {"meme_color": [red, green, blue]}})
            embed = discord.Embed(title="Успешная смена цвета!",
                                  description=f"Цвет ваших мемов сменён на цвет: "
                                              f"`{red} {green} {blue}`",
                                  color=discord.Colour.from_rgb(r=red,
                                                                g=green,
                                                                b=blue))
            embed.set_author(name=f"[meme+] {interaction.user.display_name}",
                             icon_url=interaction.user.avatar)
            embed.set_footer(text=f'🚀 Команда только для поддержавших бота')
            await interaction.response.send_message(embed=embed)
            return
        await interaction.response.send_message(embed=discord.Embed(title="Ошибка",
                                                                    description=f"Только пользователи с meme+ могут установить цвет мемов",
                                                                    color=0xff0000))

    @app_commands.command(description="[Только для поддеравших] Настроить публичность")
    @app_commands.describe(show_nickname="Показывать ник")
    @app_commands.describe(show_tag="Показывать тег рядом с ником")
    async def set_publicity(self, interaction: discord.Interaction, show_nickname: bool, show_tag: bool):
        user = profile_collection.find_one({"user_id": interaction.user.id})
        if user is not None and user["premium_status"]:
            profile_collection.update_one(user, {"$set": {"show_nickname": show_nickname, "show_tag": show_tag}})
            embed = discord.Embed(title="Успешная настройка публичности!",
                                  description=f"Вы сменили настройки публичности на:"
                                              f"\n\n**Показ ника в мемах:** `{show_nickname}`"
                                              f"\n**Вывод тега рядом с ником:** `{show_tag}`",
                                  color=0x00ff00)
            embed.set_author(name=f"[meme+] {interaction.user.display_name}",
                             icon_url=interaction.user.avatar)
            embed.set_footer(text=f'🚀 Команда только для поддержавших бота')
            await interaction.response.send_message(embed=embed)
            return
        await interaction.response.send_message(embed=discord.Embed(title="Ошибка",
                                                                    description=f"Только пользователи с meme+ могут настроить публичность",
                                                                    color=0xff0000))

    @app_commands.command(description="[Только для поддеравших] Встроить URL ссылку в мем")
    @app_commands.describe(show_url="Встраивать ссылку в ваши мемы")
    @app_commands.describe(url="Ссылка")
    async def set_url(self, interaction: discord.Interaction, show_url: bool, url: str):
        user = profile_collection.find_one({"user_id": interaction.user.id})
        if user is not None and user["premium_status"]:
            if url[0:8] == "https://" or str(url[0:7]) == "http://":
                if validators.url(url):
                    profile_collection.update_one(user, {"$set": {"show_url": show_url, "custom_url": url}})
                    embed = discord.Embed(title="URL ссылка успешно установлена!",
                                          description=f"```Теперь заголовок у мемов будет подсвечиваться, вы можете проверить переход нажав на него```"
                                                      f"\n**Отображение URL в мемах:** `{show_url}`"
                                                      f"\n**Текущая ссылка:** ```{url}```",
                                          color=0x00ff00,
                                          url=url)
                    embed.set_author(name=f"[meme+] {interaction.user.display_name}",
                                     icon_url=interaction.user.avatar)
                    embed.set_footer(text=f'🚀 Команда только для поддержавших бота')
                else:
                    embed = discord.Embed(title="Ошибка",
                                          description=f"Ссылка невалидна (не открывается)",
                                          colour=discord.Colour.red())
                    embed.set_author(name=f"[meme+] {interaction.user.display_name}",
                                     icon_url=interaction.user.avatar)
                    embed.set_footer(text=f'🚀 Команда только для поддержавших бота')
            else:
                embed = discord.Embed(title="Ошибка",
                                      description=f"Ссылка всегда должна начинаться с `https://` или `http://`",
                                      colour=discord.Colour.red())
                embed.set_author(name=f"[meme+] {interaction.user.display_name}",
                                 icon_url=interaction.user.avatar)
                embed.set_footer(text=f'🚀 Команда только для поддержавших бота')
            await interaction.response.send_message(embed=embed)
            return
        await interaction.response.send_message(embed=discord.Embed(title="Ошибка",
                                                                    description=f"Только пользователи с meme+ могут устанавливать ссылки",
                                                                    color=0xff0000))


async def setup(bot):
    print("Setup Meme_Rus")
    await bot.add_cog(Meme_Rus(bot))
