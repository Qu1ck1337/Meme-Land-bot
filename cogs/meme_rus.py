import datetime

import discord
import requests
from discord.ext import commands, tasks
from discord.ext.commands import Cog
from pymongo import MongoClient
from config import meme_rus_settings, settings, beta_settings, profile_settings
import random


class Buttons(discord.ui.View):
    def __init__(self, *, timeout=180, bot, cursor):
        self.bot = bot
        self.cursor = cursor
        self.author_meme = self.cursor.next()
        self.is_next = True
        super().__init__(timeout=timeout)

    @discord.ui.button(label="Следующий мем", style=discord.ButtonStyle.green)
    async def next_button(self, button: discord.ui.Button, interaction: discord.Interaction):
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

    @commands.command()
    async def profile(self, ctx):
        dbname = self.client[profile_settings["db_profile"]]
        collection_name = dbname[profile_settings["collection_profile"]]
        result = collection_name.find_one({"user_id": ctx.author.id})
        if result is None:
            self.create_user_profile(ctx.author.id)
            result = collection_name.find_one({"user_id": ctx.author.id})

        embed = discord.Embed(title=f"Профиль пользователя {ctx.author.display_name}", color=0x42aaff)
        embed.add_field(name="Уровень:", value=result["level"], inline=True)
        embed.add_field(name="Текущий опыт:", value=f'{result["exp"]} **/** {result["level"] * 100 + 100}', inline=True)
        embed.add_field(name="Всего мемов:", value=f'{result["memes_count"]} 🗂️', inline=True)
        embed.add_field(name="Всего лайков:", value=f'{result["memes_likes"]} 👍', inline=True)
        embed.set_thumbnail(url=ctx.author.avatar)

        meme_db = self.client['bot_memes']
        accepted_memes_collection_name = meme_db["accepted_memes"]

        test_meme = accepted_memes_collection_name.find_one({"author": ctx.author.id})

        if test_meme is None:
            await ctx.reply(embed=embed)
            await ctx.send(f"Мемов пока ещё нет =("
                           f"\nОтправить мемы можно с помощью команды `{settings['prefix']}send_meme <описание мема>` + прикреплённая картинка")
            return

        cursor = accepted_memes_collection_name.find({"author": ctx.author.id})
        author_memes = cursor.next()
        print(author_memes)
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
        await ctx.reply(embed=embed)
        await ctx.send(embed=meme_embed, view=Buttons(bot=self.bot, cursor=cursor))

    async def add_user_exp(self, ctx, user_data, collection, add_exp):
        exp_to_new_level = user_data["level"] * 100 + 100
        exp = user_data["exp"] + add_exp
        if exp >= exp_to_new_level:
            final_exp = exp - exp_to_new_level
            level = user_data["level"] + 1
            collection.update_one(user_data, {"$set": {"level": level, "exp": final_exp}})
            await ctx.send(f"{ctx.author.mention} Поздравляю, теперь у тебя **{level} уровень** мемерства! 🥳 🥳 🥳 ")
        else:
            collection.update_one(user_data, {"$set": {"exp": exp}})

    @commands.command()
    async def send_meme(self, ctx, *content):
        if ctx.author.bot:
            return
        moderation_channel = self.bot.get_guild(meme_rus_settings["guild"]).get_channel(meme_rus_settings["moderationChannel"])
        if len(ctx.message.attachments) > 0:
            dbname = self.client['bot_memes']
            collection_name = dbname["memes_on_moderation"]
            if ctx.message.attachments[0].url.split('.')[-1].lower() not in ['png', 'jpg', 'gif', 'jpeg']:
                await ctx.reply("Выкладывание видео пока недоступно, в скором времени добавим)")
                return
            if collection_name.find_one({"url": ctx.message.attachments[0].url}) is None:
                description = " ".join(content)
                embed = discord.Embed(title="Новый мем на модерацию", description=description, color=0xFFCC33)
                embed.add_field(name="Сервер:", value=f"{ctx.guild}")
                embed.add_field(name="Автор:", value=f"{ctx.author}")
                embed.set_image(url=ctx.message.attachments[0])
                msg = await moderation_channel.send(embed=embed)

                await msg.add_reaction("✅")
                await msg.add_reaction("❌")
                print(ctx.guild.id)

                collection_name.insert_one(
                    {
                        "url": ctx.message.attachments[0].url,
                        "msg_id": msg.id,
                        "author": ctx.author.id,
                        "description": description,
                        "guild": ctx.guild.id,
                    })
                message = await ctx.reply("Ваш мем отправлен на модерацию =)")
                await message.delete(delay=30)
            else:
                await ctx.reply("Такой мем уже есть")
        else:
            await ctx.reply(f"Вы не прикрепили мем к команде. Правильное использование команды: `{settings['prefix']}send_meme <описание мема>` + прикреплённая картинка")

    def valid_meme_checker(self, url):
        check = requests.head(url)
        if check.status_code == 403:
            return False
        else:
            return True

    @commands.command()
    async def meme(self, ctx, meme_id: int = None):
        dbname = self.client['bot_memes']
        accepted_memes_collection_name = dbname["accepted_memes"]

        random_record = None
        if meme_id is None:
            search = True
            while search:
                random_m = accepted_memes_collection_name.aggregate([{"$sample": {"size": 1}}])
                for res in random_m:
                    if self.valid_meme_checker(res["url"]):
                        search = False
                        random_record = res
        else:
            if accepted_memes_collection_name.find_one({"meme_id": meme_id}) is None:
                await ctx.reply("Мема с таким ID не существует :(")
                return
            random_record = accepted_memes_collection_name.find_one({"meme_id": meme_id})
            if not self.valid_meme_checker(random_record["url"]):
                await ctx.reply("Мема с таким ID не существует :(")
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
        msg = await ctx.reply(embed=embed)
        await msg.add_reaction("👍")

        dbname_u = self.client[profile_settings["db_profile"]]
        collection_name_u = dbname_u[profile_settings["collection_profile"]]
        user_res = collection_name_u.find_one({"user_id": ctx.author.id})
        if user_res is None:
            self.create_user_profile(ctx.author.id)
            user_res = collection_name_u.find_one({"user_id": ctx.author.id})
        await self.add_user_exp(ctx, user_res, collection_name_u, random.randint(1, 5))

        print(
            f"{datetime.datetime.now().strftime('%H:%M:%S')} | [USER] User {ctx.author} used <meme> command")

    @commands.command()
    async def last_meme(self, ctx):
        dbname = self.client['bot_memes']
        accepted_memes_collection_name = dbname["accepted_memes"]

        search = True
        meme_l = accepted_memes_collection_name.find().sort('_id', -1).limit(1)
        last_meme = None
        id = 0
        while search:
            for meme in meme_l:
                id = meme["meme_id"]
                if self.valid_meme_checker(meme["url"]):
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
        msg = await ctx.reply(embed=embed)
        await msg.add_reaction("👍")

        dbname_u = self.client[profile_settings["db_profile"]]
        collection_name_u = dbname_u[profile_settings["collection_profile"]]
        user_res = collection_name_u.find_one({"user_id": ctx.author.id})
        if user_res is None:
            self.create_user_profile(ctx.author.id)
            user_res = collection_name_u.find_one({"user_id": ctx.author.id})
        await self.add_user_exp(ctx, user_res, collection_name_u, random.randint(1, 5))

        print(
            f"{datetime.datetime.now().strftime('%H:%M:%S')} | [USER] User {ctx.author} used <last_meme> command")

    @commands.command()
    async def top_meme(self, ctx):
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
            msg = await ctx.reply(embed=embed)
            await msg.add_reaction("👍")

            dbname_u = self.client[profile_settings["db_profile"]]
            collection_name_u = dbname_u[profile_settings["collection_profile"]]
            user_res = collection_name_u.find_one({"user_id": ctx.author.id})
            if user_res is None:
                self.create_user_profile(ctx.author.id)
                user_res = collection_name_u.find_one({"user_id": ctx.author.id})
            await self.add_user_exp(ctx, user_res, collection_name_u, random.randint(1, 5))

            print(
                f"{datetime.datetime.now().strftime('%H:%M:%S')} | [USER] User {ctx.author} used <top_meme> command")

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
                channel = await self.bot.get_guild(result["guild"]).get_member(result["author"]).create_dm()
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
                channel = await self.bot.get_guild(result["guild"]).get_member(result["author"]).create_dm()

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
                channel = await self.bot.get_guild(result["guild"]).get_member(result["author"]).create_dm()
                embed = discord.Embed(title="Мем", description=result["description"], color=0xff0000)
                embed.set_image(url=result["url"])
                await channel.send("К сожалению ваш мем был отклонён(", embed=embed)

                collection_name.delete_one(result)
                msg = await message.channel.send("Мем отклонён")
                await msg.delete(delay=30)
                await message.delete()
            else:
                await message.channel.send("Такого мема нет в модерации")

    @Cog.listener("on_reaction_remove")
    async def on_reaction_remove(self, reaction, user):
        if (reaction.message.author.id == settings["id"] or reaction.message.author.id == beta_settings["beta_id"]) and reaction.emoji == "👍":
            dbname = self.client['bot_memes']
            accepted_memes_collection_name = dbname["accepted_memes"]
            result = accepted_memes_collection_name.find_one({"url": reaction.message.embeds[0].image.url})
            if result is not None:
                accepted_memes_collection_name.update_one(result, {"$set": {"likes": result["likes"] - 1}})
            print(
                f"{datetime.datetime.now().strftime('%H:%M:%S')} | [USER] User {user} removed like from post with {result['meme_id']} id")

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

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def auto_meme(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel
        dbname = self.client['auto_post_guilds']
        collection_name = dbname["guilds"]
        result = collection_name.find_one({"guild_id": ctx.guild.id})
        if result is None:
            collection_name.insert_one({
                "guild_id": ctx.guild.id,
                "channel_id": channel.id
            })
            await ctx.reply(f"Автопостинг мемов успешно установлен на канале: {channel.mention}")
        else:
            if result["channel_id"] != channel.id:
                collection_name.update_one(result, {"$set": {"channel_id": channel.id}})
                await ctx.reply(f"Автопостинг мемов успешно установлен на канале: {channel.mention}")
            else:
                await ctx.reply("На данном канале уже установлен автопостинг мемов")
        print(f"{datetime.datetime.now().strftime('%H:%M:%S')} | [USER] User {ctx.author} set auto post meme")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def stop_auto_meme(self, ctx):
        dbname = self.client['auto_post_guilds']
        collection_name = dbname["guilds"]
        result = collection_name.find_one({"guild_id": ctx.guild.id})
        if result is not None:
            collection_name.delete_one(result)
            await ctx.reply(f"Автопостинг мемов на этом сервере приостановлен :(")
        else:
            await ctx.reply(f"На вашем сервере не был включён автопостинг мемов")
        print(f"{datetime.datetime.now().strftime('%H:%M:%S')} | [USER] User {ctx.author} stopped auto meme posting")

    @tasks.loop(minutes=1)
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
                        if self.valid_meme_checker(res["url"]):
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


async def setup(bot):
    print("Setup Meme_Rus")
    await bot.add_cog(Meme_Rus(bot))