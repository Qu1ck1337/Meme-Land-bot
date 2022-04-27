import datetime

import discord
import pymongo
import requests
from discord.ext import commands, tasks
from discord.ext.commands import Cog
from pymongo import MongoClient
from config import meme_rus_settings, settings, beta_settings, profile_settings, economySettings
import random
from discord import app_commands


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
            # button.style = discord.ButtonStyle.green
            meme_embed = discord.Embed(
                title=f'{random.choice(meme_rus_settings["get_meme_phrases"])} <a:trippepe:901514564900913262>',
                description=self.author_meme["description"], color=0x42aaff)
            meme_embed.add_field(name="Лайки:", value=f'{self.author_meme["likes"]} 👍')
            meme_embed.add_field(name="ID мема:", value=f'**{self.author_meme["meme_id"]}**')
            meme_embed.set_image(url=self.author_meme["url"])
            meme_embed.set_footer(text=f"Сервер поддержки: "
                                       f"\nhttps://discord.gg/VB3CgP9XTW"
                                       f"\n{random.choice(meme_rus_settings['advise_phrases'])}",
                                  icon_url=self.bot.get_guild(meme_rus_settings["guild"]).icon)
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
        self.CONNECTION_STRING = "mongodb+srv://dbBot:j5x-Pkq-Q8u-mW2@data.frvp6.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
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

            dbname_p = self.client[profile_settings["db_profile"]]
            profile_collection_name = dbname_p[profile_settings["collection_profile"]]
            author_res = profile_collection_name.find_one({"user_id": self.interaction.user.id})

            if author_res is None:
                self.create_user_profile(self.interaction.user.id)
                author_res = profile_collection_name.find_one({"user_id": self.interaction.user.id})
            profile_collection_name.update_one(author_res, {"$set": {"memes_likes": author_res["memes_likes"] + 1}})

            button.disabled = True
            button.label = "Мем лайкнут 👍"
            await interaction_b.response.edit_message(view=self)
            print(
                f"{datetime.datetime.now().strftime('%H:%M:%S')} | [USER] User {self.interaction.user} liked post with {self.meme_id} id")

    def create_user_profile(self, author_id):
        dbname = self.client[profile_settings["db_profile"]]
        collection_name = dbname[profile_settings["collection_profile"]]

        dbname_m = self.client['bot_memes']
        accepted_memes_collection_name_m = dbname_m["accepted_memes"]
        result = accepted_memes_collection_name_m.find({"author": author_id})

        meme_count = 0
        likes = 0

        for meme in result:
            meme_count += 1
            likes += meme["likes"]

        collection_name.insert_one({
            "user_id": author_id,
            "level": 0,
            "exp": 0,
            "memes_count": meme_count,
            "memes_likes": likes,
            "premium_status": False
        })
        print("Профиль пользователя создан")


class RandomMemeButton(discord.ui.View):
    def __init__(self, *, timeout=180, bot, interaction: discord.Interaction, collection_name, meme_id):
        # Provide the mongodb atlas url to connect python to mongodb using pymongo
        self.CONNECTION_STRING = "mongodb+srv://dbBot:j5x-Pkq-Q8u-mW2@data.frvp6.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
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
        if interaction_b.user == self.interaction.user:
            random_record = None
            search = True
            while search:
                result_r = self.collection_name.aggregate([{"$sample": {"size": 1}}])
                for res in result_r:
                    if await self.valid_meme_checker(res["url"]):
                        search = False
                        random_record = res

            meme_embed = discord.Embed(
                title=f'{random.choice(meme_rus_settings["get_meme_phrases"])} <a:trippepe:901514564900913262>',
                description=random_record["description"], color=0x42aaff)
            meme_embed.add_field(name="Лайки:", value=f'{random_record["likes"]} 👍')
            meme_embed.add_field(name="ID мема:", value=f'**{random_record["meme_id"]}**')
            meme_embed.set_image(url=random_record["url"])
            meme_embed.set_footer(text=f"Сервер поддержки: "
                                       f"\nhttps://discord.gg/VB3CgP9XTW"
                                       f"\n{random.choice(meme_rus_settings['advise_phrases'])}",
                                  icon_url=self.bot.get_guild(meme_rus_settings["guild"]).icon)
            if self.likeButton is not None:
                self.likeButton.label = "Лайкнуть мем"
                self.likeButton.disabled = False

            await interaction_b.response.edit_message(embed=meme_embed, view=self)
            self.meme_id = random_record["meme_id"]

            dbname_u = self.client[profile_settings["db_profile"]]
            collection_name_u = dbname_u[profile_settings["collection_profile"]]
            user_res = collection_name_u.find_one({"user_id": self.interaction.user.id})
            if user_res is None:
                self.create_user_profile(self.interaction.user.id)
                user_res = collection_name_u.find_one({"user_id": self.interaction.user.id})
            await self.add_user_exp(self.interaction, user_res, collection_name_u, random.randint(1, 5))

    @discord.ui.button(label="Лайкнуть мем", style=discord.ButtonStyle.blurple)
    async def likeButton(self, interaction_b: discord.Interaction, button: discord.ui.Button):
        if interaction_b.user == self.interaction.user:
            result = self.collection_name.find_one({"meme_id": self.meme_id})
            if result is not None:
                self.collection_name.update_one(result, {"$set": {"likes": result["likes"] + 1}})

            dbname_p = self.client[profile_settings["db_profile"]]
            profile_collection_name = dbname_p[profile_settings["collection_profile"]]
            author_res = profile_collection_name.find_one({"user_id": self.interaction.user.id})

            if author_res is None:
                self.create_user_profile(self.interaction.user.id)
                author_res = profile_collection_name.find_one({"user_id": self.interaction.user.id})
            profile_collection_name.update_one(author_res, {"$set": {"memes_likes": author_res["memes_likes"] + 1}})

            button.disabled = True
            button.label = "Мем лайкнут 👍"
            self.likeButton = button
            await interaction_b.response.edit_message(view=self)
            print(
                f"{datetime.datetime.now().strftime('%H:%M:%S')} | [USER] User {self.interaction.user} liked post with {self.meme_id} id")

    async def add_user_exp(self, interation: discord.Interaction, user_data, collection, add_exp):
        exp_to_new_level = user_data["level"] * 100 + 100
        exp = user_data["exp"] + add_exp
        if exp >= exp_to_new_level:
            final_exp = exp - exp_to_new_level
            level = user_data["level"] + 1
            collection.update_one(user_data, {"$set": {"level": level, "exp": final_exp}})
            await interation.channel.send(f"{interation.user.mention} Поздравляю, теперь у тебя **{level} уровень** мемерства! 🥳 🥳 🥳 ")
        else:
            collection.update_one(user_data, {"$set": {"exp": exp}})

    def create_user_profile(self, author_id):
        dbname = self.client[profile_settings["db_profile"]]
        collection_name = dbname[profile_settings["collection_profile"]]

        dbname_m = self.client['bot_memes']
        accepted_memes_collection_name_m = dbname_m["accepted_memes"]
        result = accepted_memes_collection_name_m.find({"author": author_id})

        meme_count = 0
        likes = 0

        for meme in result:
            meme_count += 1
            likes += meme["likes"]

        collection_name.insert_one({
            "user_id": author_id,
            "level": 0,
            "exp": 0,
            "memes_count": meme_count,
            "memes_likes": likes,
            "premium_status": False
        })
        print("Профиль пользователя создан")

    async def valid_meme_checker(self, url):
        check = requests.head(url)
        if check.status_code == 403 or check.status_code == 404:
            await self.delete_meme_after_validation(url=url)
            return False
        else:
            return True

    async def delete_meme_after_validation(self, url):
        dbname = self.client['bot_memes']
        accepted_memes_collection_name = dbname["accepted_memes"]
        meme_res = accepted_memes_collection_name.find_one({"url": url})
        if meme_res is not None:
            user = self.bot.get_user(meme_res["author"])
            try:
                await user.create_dm()
            except Exception:
                pass
            embed = discord.Embed(title="Ваш мем был удалён", description=f"Нам пришлось удалить ваш мем c ID: **{meme_res['meme_id']}**", color=0xff0000)
            embed.add_field(name="Причина:", value='Мема не существует, оригинал был удалён')
            dbname_user = self.client[profile_settings["db_profile"]]
            collection_name_user = dbname_user[profile_settings["collection_profile"]]
            result_user = collection_name_user.find_one({"user_id": user.id})
            if result_user is None:
                self.create_user_profile(user.id)
                result_user = collection_name_user.find_one({"user_id": user.id})
            collection_name_user.update_one(result_user, {"$set": {"memes_count": result_user["memes_count"] - 1, "memes_likes": result_user["memes_likes"] - meme_res["likes"]}})
            accepted_memes_collection_name.delete_one(meme_res)
            meme_embed = discord.Embed(title="Удалённый мем", description=meme_res["description"], color=0xff0000)
            meme_embed.set_image(url=meme_res["url"])
            await user.send(embed=embed)
            await user.send(embed=meme_embed)


class Meme_Rus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Provide the mongodb atlas url to connect python to mongodb using pymongo
        self.CONNECTION_STRING = "mongodb+srv://dbBot:j5x-Pkq-Q8u-mW2@data.frvp6.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
        # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
        self.client = MongoClient(self.CONNECTION_STRING)
        self.post_meme = False

    @Cog.listener("on_ready")
    async def on_ready(self):
        print("start")
        self.auto_post_meme.start()

    def create_user_profile(self, author_id):
        dbname = self.client[profile_settings["db_profile"]]
        collection_name = dbname[profile_settings["collection_profile"]]

        dbname_m = self.client['bot_memes']
        accepted_memes_collection_name_m = dbname_m["accepted_memes"]
        result = accepted_memes_collection_name_m.find({"author": author_id})

        meme_count = 0
        likes = 0

        for meme in result:
            meme_count += 1
            likes += meme["likes"]

        collection_name.insert_one({
            "user_id": author_id,
            "level": 0,
            "exp": 0,
            "memes_count": meme_count,
            "memes_likes": likes,
            "premium_status": False
        })
        print("Профиль пользователя создан")

    @app_commands.command(description="Посмотреть свой мемный профиль")
    async def profile(self, interaction: discord.Interaction):
        dbname = self.client[profile_settings["db_profile"]]
        collection_name = dbname[profile_settings["collection_profile"]]
        result = collection_name.find_one({"user_id": interaction.user.id})

        if result is None:
            self.create_user_profile(interaction.user.id)
            result = collection_name.find_one({"user_id": interaction.user.id})
        await self.add_user_exp(interaction, result, collection_name, 0)
        result = collection_name.find_one({"user_id": interaction.user.id})

        embed = discord.Embed(title=f"Профиль пользователя {interaction.user.display_name}", color=0x42aaff)
        embed.add_field(name="Уровень:", value=result["level"], inline=True)
        embed.add_field(name="Текущий опыт:", value=f'{result["exp"]} **/** {result["level"] * 100 + 100}', inline=True)
        embed.add_field(name="Всего мемов:", value=f'{result["memes_count"]} 🗂️', inline=True)
        embed.add_field(name="Всего лайков:", value=f'{result["memes_likes"]} 👍', inline=True)
        embed.set_thumbnail(url=interaction.user.avatar)

        meme_db = self.client['bot_memes']
        accepted_memes_collection_name = meme_db["accepted_memes"]

        test_meme = accepted_memes_collection_name.find_one({"author": interaction.user.id})

        if test_meme is None:
            await interaction.response.send_message(embed=embed)
            await interaction.channel.send(f"Мемов пока ещё нет =("
                           f"\nОтправить мемы можно с помощью команды `{settings['prefix']}send_meme <описание мема> + картинка`")
            return

        cursor = accepted_memes_collection_name.find({"author": interaction.user.id})
        author_memes = cursor.next()
        meme_embed = discord.Embed(
            title=f'{random.choice(meme_rus_settings["get_meme_phrases"])} <a:trippepe:901514564900913262>',
            description=author_memes["description"], color=0x42aaff)
        meme_embed.add_field(name="Лайки:", value=f'{author_memes["likes"]} 👍')
        meme_embed.add_field(name="ID мема:", value=f'**{author_memes["meme_id"]}**')
        meme_embed.set_image(url=author_memes["url"])
        meme_embed.set_footer(text=f"Сервер поддержки: "
                              f"\nhttps://discord.gg/VB3CgP9XTW"
                              f"\n{random.choice(meme_rus_settings['advise_phrases'])}",
                         icon_url=self.bot.get_guild(meme_rus_settings["guild"]).icon)
        await interaction.response.send_message(embed=embed)
        await interaction.channel.send(embed=meme_embed, view=NextButton(bot=self.bot, cursor=cursor))

    async def add_user_exp(self, interaction: discord.Interaction, user_data, collection, add_exp):
        exp_to_new_level = user_data["level"] * 100 + 100
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
            collection.update_one(user_data, {"$set": {"level": level, "exp": exp}})
            await interaction.channel.send(
                f"{interaction.user.mention} Поздравляю, теперь у тебя **{level} уровень** мемерства! 🥳 🥳 🥳 ")
        else:
            collection.update_one(user_data, {"$set": {"exp": exp}})

    @app_commands.command(name="send_meme", description="Отправить мемы")
    @app_commands.describe(description="Описание мема")
    @app_commands.describe(meme="Мем (.png .jpg .gif .jpeg)")
    async def send_meme(self, interaction: discord.Interaction, meme: discord.Attachment, description: str = ""):
        if interaction.user.bot:
            return

        moderation_channel = self.bot.get_guild(meme_rus_settings["guild"]).get_channel(meme_rus_settings["moderationChannel"])
        dbname = self.client['bot_memes']
        collection_name = dbname["memes_on_moderation"]

        if meme.url.split('.')[-1].lower() not in ['png', 'jpg', 'gif', 'jpeg']:
            await interaction.response.send_message("Выкладывание видео пока недоступно, в скором времени добавим)")
            return
        if collection_name.find_one({"url": meme.url}) is None:
            embed = discord.Embed(title="Новый мем на модерацию", description=description, color=0xFFCC33)
            embed.add_field(name="Сервер:", value=f"{interaction.guild}")
            embed.add_field(name="Автор:", value=f"{interaction.user}")
            embed.set_image(url=meme)
            msg = await moderation_channel.send(embed=embed)

            await msg.add_reaction("✅")
            await msg.add_reaction("❌")
            print(interaction.guild_id)

            collection_name.insert_one(
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
                                                    "\n**ПРОСЬБА НЕ УДАЛЯТЬ МЕМ, ИНАЧЕ ОН БУДЕТ УДАЛЁН С БОТА**", embed=embed)
        else:
            await interaction.response.send_message("Такой мем уже есть")

    async def valid_meme_checker(self, url):
        check = requests.head(url)
        if check.status_code == 403 or check.status_code == 404:
            await self.delete_meme_after_validation(url=url)
            return False
        else:
            return True

    @app_commands.command(name="meme", description="Посмотреть мем")
    @app_commands.describe(id="ID мема")
    async def meme(self, interaction: discord.Interaction, id: int = None):
        if interaction.guild == settings["guild"] and interaction.channel.id in settings["ignored_commands_channels"]:
            await interaction.response.send_message(embed=discord.Embed(
                title="Ошибка",
                description="Данная команда недоступна на этом канале, чтобы смотреть мемчики переходи в <#968940291904114769>)",
                color=economySettings["error_color"]))
            return

        dbname = self.client['bot_memes']
        accepted_memes_collection_name = dbname["accepted_memes"]

        random_record = None
        if id is None:
            search = True
            while search:
                random_m = accepted_memes_collection_name.aggregate([{"$sample": {"size": 1}}])
                for res in random_m:
                    if await self.valid_meme_checker(res["url"]):
                        search = False
                        random_record = res
        else:
            if accepted_memes_collection_name.find_one({"meme_id": id}) is None:
                await interaction.response.send_message("Мема с таким ID не существует :(")
                return
            random_record = accepted_memes_collection_name.find_one({"meme_id": id})
            if not await self.valid_meme_checker(random_record["url"]):
                await interaction.response.send_message("Мема с таким ID не существует :(")
                return

        embed = discord.Embed(
            title=f'{random.choice(meme_rus_settings["get_meme_phrases"])} <a:trippepe:901514564900913262>',
            description=random_record["description"], color=0x42aaff)

        try:
            likes = random_record["likes"]
        except KeyError:
            accepted_memes_collection_name.update_one(random_record, {"$set": {"likes": 0}})
            likes = random_record["likes"]

        embed.add_field(name="Лайки:", value=f'{likes} 👍')
        embed.add_field(name="ID мема:", value=f'**{random_record["meme_id"]}**')
        embed.set_image(url=random_record["url"])
        embed.set_footer(text=f"Сервер поддержки: "
                              f"\nhttps://discord.gg/VB3CgP9XTW"
                              f"\n{random.choice(meme_rus_settings['advise_phrases'])}",
                         icon_url=self.bot.get_guild(meme_rus_settings["guild"]).icon)
        if id is None:
            await interaction.response.send_message(embed=embed, view=RandomMemeButton(interaction=interaction,
                                                                                 collection_name=accepted_memes_collection_name,
                                                                                 meme_id=random_record["meme_id"], bot=self.bot))
        else:
            await interaction.response.send_message(embed=embed, view=LikeButton(interaction=interaction,
                                                                            collection_name=accepted_memes_collection_name,
                                                                            meme_id=random_record["meme_id"]))
        dbname_u = self.client[profile_settings["db_profile"]]
        collection_name_u = dbname_u[profile_settings["collection_profile"]]
        user_res = collection_name_u.find_one({"user_id": interaction.user.id})
        if user_res is None:
            self.create_user_profile(interaction.user.id)
            user_res = collection_name_u.find_one({"user_id": interaction.user.id})
        await self.add_user_exp(interaction, user_res, collection_name_u, random.randint(1, 5))

        print(
            f"{datetime.datetime.now().strftime('%H:%M:%S')} | [USER] User {interaction.user} used <meme> command")

    @app_commands.command(name="last_meme", description="Посмотреть последний одобренный мем")
    async def last_meme(self, interaction: discord.Interaction):
        if interaction.guild == settings["guild"] and interaction.channel.id in settings["ignored_commands_channels"]:
            await interaction.response.send_message(embed=discord.Embed(
                title="Ошибка",
                description="Данная команда недоступна на этом канале, чтобы смотреть мемчики переходи в <#968940291904114769>)",
                color=economySettings["error_color"]))
            return

        dbname = self.client['bot_memes']
        accepted_memes_collection_name = dbname["accepted_memes"]

        search = True
        meme_l = accepted_memes_collection_name.find().sort('_id', -1).limit(1)
        last_meme = None
        id = 0
        while search:
            for meme in meme_l:
                id = meme["meme_id"]
                if await self.valid_meme_checker(meme["url"]):
                    last_meme = meme
                    search = False
            if search:
                meme_l = accepted_memes_collection_name.find({"meme_id": id - 1})

        embed = discord.Embed(title="Самый свежий мемчик для тебя! 🍞",
                              description=last_meme["description"], color=0x42aaff)

        try:
            likes = last_meme["likes"]
        except KeyError:
            accepted_memes_collection_name.update_one(last_meme, {"$set": {"likes": 0}})
            likes = last_meme["likes"]

        embed.add_field(name="Лайки:", value=f'{likes} 👍')
        embed.add_field(name="ID мема:", value=f'**{last_meme["meme_id"]}**')
        embed.set_image(url=last_meme["url"])
        embed.set_footer(text=f"Сервер поддержки: "
                              f"\nhttps://discord.gg/VB3CgP9XTW"
                              f"\n{random.choice(meme_rus_settings['advise_phrases'])}",
                         icon_url=self.bot.get_guild(meme_rus_settings["guild"]).icon)
        await interaction.response.send_message(embed=embed, view=LikeButton(interaction=interaction,
                                                                             collection_name=accepted_memes_collection_name,
                                                                             meme_id=last_meme["meme_id"]))

        dbname_u = self.client[profile_settings["db_profile"]]
        collection_name_u = dbname_u[profile_settings["collection_profile"]]
        user_res = collection_name_u.find_one({"user_id": interaction.user.id})
        if user_res is None:
            self.create_user_profile(interaction.user.id)
            user_res = collection_name_u.find_one({"user_id": interaction.user.id})
        await self.add_user_exp(interaction, user_res, collection_name_u, random.randint(1, 5))

        print(
            f"{datetime.datetime.now().strftime('%H:%M:%S')} | [USER] User {interaction.user} used <last_meme> command")

    @app_commands.command(name="top_meme", description="Посмотреть самый залайканный мем")
    async def top_meme(self, interaction: discord.Interaction):
        if interaction.guild == settings["guild"] and interaction.channel.id in settings["ignored_commands_channels"]:
            await interaction.response.send_message(embed=discord.Embed(
                title="Ошибка",
                description="Данная команда недоступна на этом канале, чтобы смотреть мемчики переходи в <#968940291904114769>)",
                color=economySettings["error_color"]))
            return

        dbname = self.client['bot_memes']
        accepted_memes_collection_name = dbname["accepted_memes"]

        last_meme = accepted_memes_collection_name.find().sort('likes', -1).limit(1)
        for result in last_meme:
            embed = discord.Embed(title="Самый лучший мем! 🏆",
                                  description=result["description"], color=0x42aaff)

            try:
                likes = result["likes"]
            except KeyError:
                accepted_memes_collection_name.update_one(result, {"$set": {"likes": 0}})
                likes = result["likes"]

            embed.add_field(name="Лайки:", value=f'{likes} 👍')
            embed.add_field(name="ID мема:", value=f'**{result["meme_id"]}**')
            embed.set_image(url=result["url"])
            embed.set_footer(text=f"Сервер поддержки: "
                                  f"\nhttps://discord.gg/VB3CgP9XTW"
                                  f"\n{random.choice(meme_rus_settings['advise_phrases'])}",
                             icon_url=self.bot.get_guild(meme_rus_settings["guild"]).icon)
            await interaction.response.send_message(embed=embed, view=LikeButton(interaction=interaction,
                                                                            collection_name=accepted_memes_collection_name,
                                                                            meme_id=result["meme_id"]))

            dbname_u = self.client[profile_settings["db_profile"]]
            collection_name_u = dbname_u[profile_settings["collection_profile"]]
            user_res = collection_name_u.find_one({"user_id": interaction.user.id})
            if user_res is None:
                self.create_user_profile(interaction.user.id)
                user_res = collection_name_u.find_one({"user_id": interaction.user.id})
            await self.add_user_exp(interaction, user_res, collection_name_u, random.randint(1, 5))

            print(
                f"{datetime.datetime.now().strftime('%H:%M:%S')} | [USER] User {interaction.user} used <top_meme> command")

    #@commands.command()
    #@commands.has_any_role(939801337196073030, 905484393919967252, 906632280376741939)
    async def accept_meme(self, ctx, message: discord.Message):
        if ctx.guild.id != meme_rus_settings["guild"] or ctx.channel.id != meme_rus_settings["moderationChannel"]:
            return
        if message.author.id == settings["id"] or message.author.id == beta_settings["beta_id"]:
            dbname = self.client['bot_memes']
            collection_name = dbname["memes_on_moderation"]
            result = collection_name.find_one({"msg_id": message.id})
            if result is not None:
                accepted_memes_collection_name = dbname["accepted_memes"]
                accepted_memes_collection_name.insert_one({
                    "url": result["url"],
                    "author": result["author"],
                    "description": result["description"],
                    "likes": 0
                })

                channel = await self.bot.get_guild(result["guild"]).get_member(result["author"]).create_dm()
                embed = discord.Embed(title="Мем", description=result["description"], color=0x33FF66)
                embed.set_image(url=result["url"])
                await channel.send("Поздравляем, модерация одобрила ваш мем ^-^", embed=embed)

                meme_channel = self.bot.get_guild(meme_rus_settings["guild"]).get_channel(
                    meme_rus_settings["meme_accepted_channel"])
                embed = discord.Embed(title="Новый мем!", description=result["description"], color=0x42aaff)
                embed.set_image(url=result["url"])
                await meme_channel.send(embed=embed)

                collection_name.delete_one(result)

                msg = await ctx.reply("Мем принят")
                await msg.delete(delay=30)
                await message.delete()
            else:
                await ctx.reply("Такого мема нет в модерации")
            await ctx.message.delete()

    #@commands.command()
    #@commands.has_any_role(939801337196073030, 905484393919967252, 906632280376741939)
    async def reject_meme(self, ctx, message: discord.Message):
        if ctx.guild.id != meme_rus_settings["guild"] or ctx.channel.id != meme_rus_settings["moderationChannel"]:
            return
        if message.author.id == settings["id"] or message.author.id == beta_settings["beta_id"]:
            dbname = self.client['bot_memes']
            collection_name = dbname["memes_on_moderation"]
            result = collection_name.find_one({"msg_id": message.id})
            if result is not None:
                channel = await self.bot.fetch_user(result["author"]).create_dm()
                embed = discord.Embed(title="Мем", description=result["description"], color=0xff0000)
                embed.set_image(url=result["url"])
                await channel.send("К сожалению ваш мем был отклонён(", embed=embed)

                collection_name.delete_one(result)
                msg = await ctx.reply("Мем отклонён")
                await msg.delete(delay=30)
                await message.delete()
            else:
                await ctx.reply("Такого мема нет в модерации")
            await ctx.message.delete()

    @Cog.listener("on_raw_reaction_add")
    async def on_raw_reaction_add(self, payload):
        if payload.member.bot:
            return
        message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
        author = message.author
        if (author.id == settings["id"] or author.id == beta_settings["beta_id"]) and str(payload.emoji) == "👍":
            dbname = self.client['bot_memes']
            accepted_memes_collection_name = dbname["accepted_memes"]
            result = accepted_memes_collection_name.find_one({"url": message.embeds[0].image.url})
            if result is not None:
                accepted_memes_collection_name.update_one(result, {"$set": {"likes": result["likes"] + 1}})

                dbname = self.client['bot_memes']
                accepted_memes_collection_name = dbname["accepted_memes"]
                meme_id = int(message.embeds[0].fields[1].value.replace("**", ""))
                meme_res = accepted_memes_collection_name.find_one({"meme_id": meme_id})

                dbname_p = self.client[profile_settings["db_profile"]]
                profile_collection_name = dbname_p[profile_settings["collection_profile"]]
                author_res = profile_collection_name.find_one({"user_id": meme_res["author"]})

                if author_res is None:
                    self.create_user_profile(meme_res["author"])
                    author_res = profile_collection_name.find_one({"user_id": meme_res["author"]})
                print(author_res)
                profile_collection_name.update_one(author_res, {"$set": {"memes_likes": author_res["memes_likes"] + 1}})
            print(
                f"{datetime.datetime.now().strftime('%H:%M:%S')} | [USER] User {payload.member} liked post with {result['meme_id']} id")
        elif payload.channel_id == meme_rus_settings["moderationChannel"] and str(payload.emoji) == "✅" and \
            (author.id == settings["id"] or author.id == beta_settings["beta_id"]):
            if message.guild.id != meme_rus_settings["guild"]:
                return

            print("accept_meme")
            dbname = self.client['bot_memes']
            collection_name = dbname["memes_on_moderation"]
            result = collection_name.find_one({"msg_id": message.id})
            if result is not None:
                channel = await self.bot.fetch_user(result["author"]).create_dm()

                accepted_memes_collection_name = dbname["accepted_memes"]

                last_meme = accepted_memes_collection_name.find().sort('_id', -1).limit(1)
                meme_id = 0
                for rslt in last_meme:
                    meme_id = rslt["meme_id"] + 1

                accepted_memes_collection_name.insert_one({
                    "url": result["url"],
                    "author": result["author"],
                    "description": result["description"],
                    "likes": 0,
                    "meme_id": meme_id
                })

                dbname_user = self.client[profile_settings["db_profile"]]
                collection_name_user = dbname_user[profile_settings["collection_profile"]]
                result_user = collection_name_user.find_one({"user_id": result["author"]})
                if result_user is None:
                    self.create_user_profile(result["author"])
                    result_user = collection_name_user.find_one({"user_id": result["author"]})
                collection_name_user.update_one(result_user, {"$set": {"memes_count": result_user["memes_count"] + 1, "exp": result_user["exp"] + 25}})

                embed = discord.Embed(title="Мем", description=result["description"], color=0x33FF66)
                embed.add_field(name="ID мема", value=f"**{meme_id}**")
                embed.set_image(url=result["url"])
                await channel.send("Поздравляем, модерация одобрила ваш мем ^-^", embed=embed)

                meme_channel = self.bot.get_guild(meme_rus_settings["guild"]).get_channel(
                    meme_rus_settings["meme_accepted_channel"])
                embed = discord.Embed(title="Новый мем!", description=result["description"], color=0x42aaff)
                embed.add_field(name="ID мема", value=f"**{meme_id}**")
                embed.set_image(url=result["url"])
                await meme_channel.send(embed=embed)

                collection_name.delete_one(result)

                msg = await message.channel.send("Мем принят")
                await msg.delete(delay=30)
                await message.delete()
            else:
                await message.channel.send("Такого мема нет в модерации")
        elif payload.channel_id == meme_rus_settings["moderationChannel"] and str(payload.emoji) == "❌" and \
            (author.id == settings["id"] or author.id == beta_settings["beta_id"]):
            if message.guild.id != meme_rus_settings["guild"]:
                return

            print("reject_meme")
            dbname = self.client['bot_memes']
            collection_name = dbname["memes_on_moderation"]
            result = collection_name.find_one({"msg_id": message.id})
            if result is not None:
                channel = await self.bot.fetch_user(result["author"]).create_dm()
                embed = discord.Embed(title="Мем", description=result["description"], color=0xff0000)
                embed.set_image(url=result["url"])
                await channel.send("К сожалению ваш мем был отклонён(", embed=embed)

                collection_name.delete_one(result)
                msg = await message.channel.send("Мем отклонён")
                await msg.delete(delay=30)
                await message.delete()
            else:
                await message.channel.send("Такого мема нет в модерации")

    @Cog.listener("on_raw_reaction_remove")
    async def on_raw_reaction_remove(self, payload):
        message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
        author = message.author
        if (author.id == settings["id"] or author.id == beta_settings["beta_id"]) and str(payload.emoji) == "👍":
            dbname = self.client['bot_memes']
            accepted_memes_collection_name = dbname["accepted_memes"]
            result = accepted_memes_collection_name.find_one({"url": message.embeds[0].image.url})
            if result is not None:
                accepted_memes_collection_name.update_one(result, {"$set": {"likes": result["likes"] - 1}})

                dbname = self.client['bot_memes']
                accepted_memes_collection_name = dbname["accepted_memes"]
                meme_id = int(message.embeds[0].fields[1].value.replace("**", ""))
                meme_res = accepted_memes_collection_name.find_one({"meme_id": meme_id})

                dbname_p = self.client[profile_settings["db_profile"]]
                profile_collection_name = dbname_p[profile_settings["collection_profile"]]
                author_res = profile_collection_name.find_one({"user_id": meme_res["author"]})

                if author_res is None:
                    self.create_user_profile(meme_res["author"])
                    author_res = profile_collection_name.find_one({"user_id": meme_res["author"]})
                profile_collection_name.update_one(author_res, {"$set": {"memes_likes": author_res["memes_likes"] - 1}})
            print(
                f"{datetime.datetime.now().strftime('%H:%M:%S')} | [USER] User {payload.member} removed like from post with {result['meme_id']} id")

    @commands.command()
    @commands.is_owner()
    async def add_ids(self, ctx):
        count = 1
        dbname = self.client['bot_memes']
        accepted_memes_collection_name = dbname["accepted_memes"]
        results = accepted_memes_collection_name.find()
        for result in results:
            accepted_memes_collection_name.update_one(result, {"$set": {"meme_id": count}})
            count += 1
        print("indexes ended")

    @app_commands.command(description="Устанавливает автопостинг мемов раз в 30 минут")
    @app_commands.describe(channel="Канал, где нужно постить мемы (по умолчанию этот канал)")
    @app_commands.checks.has_permissions(administrator=True, manage_guild=True)
    async def auto_meme(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        if channel is None:
            channel = interaction.channel
        dbname = self.client['auto_post_guilds']
        collection_name = dbname["guilds"]
        result = collection_name.find_one({"guild_id": interaction.guild_id})
        if result is None:
            collection_name.insert_one({
                "guild_id": interaction.guild_id,
                "channel_id": channel.id
            })
            await interaction.response.send_message(f"Автопостинг мемов успешно установлен на канале: {channel.mention}")
        else:
            if result["channel_id"] != channel.id:
                collection_name.update_one(result, {"$set": {"channel_id": channel.id}})
                await interaction.response.send_message(f"Автопостинг мемов успешно установлен на канале: {channel.mention}")
            else:
                await interaction.response.send_message("На данном канале уже установлен автопостинг мемов")
        print(f"{datetime.datetime.now().strftime('%H:%M:%S')} | [USER] User {interaction.user} set auto post meme")

    @app_commands.command(description="Останавливает автопостинг мемов на этом сервере")
    @app_commands.checks.has_permissions(administrator=True, manage_guild=True)
    async def stop_auto_meme(self, interaction: discord.Interaction):
        dbname = self.client['auto_post_guilds']
        collection_name = dbname["guilds"]
        result = collection_name.find_one({"guild_id": interaction.guild_id})
        if result is not None:
            collection_name.delete_one(result)
            await interaction.response.send_message(f"Автопостинг мемов на этом сервере приостановлен :(")
        else:
            await interaction.response.send_message(f"На вашем сервере не был включён автопостинг мемов")
        print(f"{datetime.datetime.now().strftime('%H:%M:%S')} | [USER] User {interaction.user} stopped auto meme posting")

    @tasks.loop(minutes=30)
    async def auto_post_meme(self):
        if self.post_meme is not True:
            self.post_meme = True
            return
        print(f"{datetime.datetime.now().strftime('%H:%M:%S')} | [INFO] Auto posting meme on servers")
        dbname = self.client['auto_post_guilds']
        collection_name = dbname["guilds"]
        results = collection_name.find()
        for result in results:
            try:
                guild = self.bot.get_guild(result["guild_id"])
                channel = guild.get_channel(result["channel_id"])

                dbname_meme = self.client['bot_memes']
                accepted_memes_collection_name = dbname_meme["accepted_memes"]

                search = True
                meme_result = None
                while search:
                    meme_r = accepted_memes_collection_name.aggregate([{"$sample": {"size": 1}}])
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

    def check_if_it_is_me(interaction: discord.Interaction) -> bool:
        return interaction.user.id == 443337837455212545

    @app_commands.command()
    @app_commands.check(check_if_it_is_me)
    @app_commands.guilds(892493256129118260)
    @app_commands.describe(meme_id="id мема")
    @app_commands.describe(content="Описание причины")
    async def delete_meme(self, interaction: discord.Interaction, meme_id: int, content: str):
        dbname = self.client['bot_memes']
        accepted_memes_collection_name = dbname["accepted_memes"]
        meme_res = accepted_memes_collection_name.find_one({"meme_id": meme_id})
        if meme_res is not None:
            user = self.bot.get_user(meme_res["author"])
            await user.create_dm()
            embed = discord.Embed(title="Ваш мем был удалён", description=f"Нам пришлось удалить ваш мем c ID: **{meme_id}**", color=0xff0000)
            embed.add_field(name="Причина:", value=f'{content}')

            dbname_user = self.client[profile_settings["db_profile"]]
            collection_name_user = dbname_user[profile_settings["collection_profile"]]
            result_user = collection_name_user.find_one({"user_id": user.id})
            if result_user is None:
                self.create_user_profile(user.id)
                result_user = collection_name_user.find_one({"user_id": user.id})
            collection_name_user.update_one(result_user, {"$set": {"memes_count": result_user["memes_count"] - 1, "memes_likes": result_user["memes_likes"] - meme_res["likes"]}})

            accepted_memes_collection_name.delete_one(meme_res)

            meme_embed = discord.Embed(title="Удалённый мем", description=meme_res["description"], color=0xff0000)
            meme_embed.set_image(url=meme_res["url"])
            await user.send(embed=embed)
            await user.send(embed=meme_embed)
            await interaction.response.send_message(f"Мем с ID {meme_id} был удалён. Пользователь уведомлён об этом.")
        else:
            await interaction.response.send_message(embed=discord.Embed(title="Ошибка!", description=f"Мем с ID **{meme_id}** не существует!", color=0xff0000))

    async def delete_meme_after_validation(self, url):
        dbname = self.client['bot_memes']
        accepted_memes_collection_name = dbname["accepted_memes"]
        meme_res = accepted_memes_collection_name.find_one({"url": url})
        if meme_res is not None:
            user = self.bot.get_user(meme_res["author"])
            try:
                await user.create_dm()
            except Exception:
                pass
            embed = discord.Embed(title="Ваш мем был удалён", description=f"Нам пришлось удалить ваш мем c ID: **{meme_res['meme_id']}**", color=0xff0000)
            embed.add_field(name="Причина:", value='Мема не существует, оригинал был удалён')
            dbname_user = self.client[profile_settings["db_profile"]]
            collection_name_user = dbname_user[profile_settings["collection_profile"]]
            result_user = collection_name_user.find_one({"user_id": user.id})
            if result_user is None:
                self.create_user_profile(user.id)
                result_user = collection_name_user.find_one({"user_id": user.id})
            collection_name_user.update_one(result_user, {"$set": {"memes_count": result_user["memes_count"] - 1, "memes_likes": result_user["memes_likes"] - meme_res["likes"]}})
            accepted_memes_collection_name.delete_one(meme_res)
            meme_embed = discord.Embed(title="Удалённый мем", description=meme_res["description"], color=0xff0000)
            meme_embed.set_image(url=meme_res["url"])
            await user.send(embed=embed)
            await user.send(embed=meme_embed)

    @app_commands.command(description="Таблица лидеров")
    async def leaderboard(self, interaction: discord.Interaction):
        dbname = self.client[profile_settings["db_profile"]]
        collection_name = dbname[profile_settings["collection_profile"]]
        result = collection_name.find().sort([("level", pymongo.DESCENDING), ("exp", pymongo.DESCENDING)]).limit(10)
        embed = discord.Embed(title="Топ-10 лучших мемеров бота Meme Land", color=0x42aaff)
        for num, rez in enumerate(result):
            embed.add_field(
                name=f"**{'🥇 ' if num == 0 else '🥈 ' if num == 1 else '🥉 ' if num == 2 else ''}{num + 1}. {self.bot.get_user(rez['user_id']).name}**",
                value=f"**Уровень:** {rez['level']}\n**Опыт: {rez['exp']}**", inline=False)
        embed.set_thumbnail(url=interaction.guild.icon)
        embed.set_footer(text=f"Запрошено {interaction.user.name} в {datetime.datetime.now().strftime('%H:%M')}", icon_url=interaction.user.avatar)
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    print("Setup Meme_Rus")
    await bot.add_cog(Meme_Rus(bot))