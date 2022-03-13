import datetime

import discord
from discord.ext import commands, tasks
from discord.ext.commands import Cog
from pymongo import MongoClient
from config import meme_rus_settings, settings, beta_settings
import random


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

    @commands.command()
    async def meme(self, ctx, meme_id: int = None):
        dbname = self.client['bot_memes']
        accepted_memes_collection_name = dbname["accepted_memes"]

        if meme_id is None:
            random_record = accepted_memes_collection_name.aggregate([{"$sample": {"size": 1}}])
        else:
            if accepted_memes_collection_name.find_one({"meme_id": meme_id}) is None:
                await ctx.reply("Мема с таким ID не существует :(")
                return
            random_record = accepted_memes_collection_name.find({"meme_id": meme_id}).limit(1)

        for result in random_record:
            embed = discord.Embed(
                title=f'{random.choice(meme_rus_settings["get_meme_phrases"])} <a:trippepe:901514564900913262>',
                description=result["description"], color=0x42aaff)

            try:
                likes = result["likes"]
            except KeyError:
                accepted_memes_collection_name.update_one(result, {"$set": {"likes": 0}})
                likes = result["likes"]

            embed.add_field(name="Лайки:", value=f'{likes} 👍')
            embed.add_field(name="ID мема:", value=f'**{result["meme_id"]}**')
            embed.set_image(url=result["url"])
            embed.set_footer(text="Мы есть в дискорде: "
                                  "\nhttps://discord.gg/VB3CgP9XTW"
                                  "\n💎 Опробуйте автопостинг мемов! Подробнее: ml/help",
                             icon_url=self.bot.get_guild(meme_rus_settings["guild"]).icon_url)
            msg = await ctx.reply(embed=embed)
            await msg.add_reaction("👍")
            print(
                f"{datetime.datetime.now().strftime('%H:%M:%S')} | [USER] User {ctx.author} used <meme> command")

    @commands.command()
    async def last_meme(self, ctx):
        dbname = self.client['bot_memes']
        accepted_memes_collection_name = dbname["accepted_memes"]

        last_meme = accepted_memes_collection_name.find().sort('_id', -1).limit(1)
        for result in last_meme:
            embed = discord.Embed(title="Самый свежий мемчик для тебя! 🍞",
                                  description=result["description"], color=0x42aaff)

            try:
                likes = result["likes"]
            except KeyError:
                accepted_memes_collection_name.update_one(result, {"$set": {"likes": 0}})
                likes = result["likes"]

            embed.add_field(name="Лайки:", value=f'{likes} 👍')
            embed.add_field(name="ID мема:", value=f'**{result["meme_id"]}**')
            embed.set_image(url=result["url"])
            embed.set_footer(text="Мы есть в дискорде: "
                                  "\nhttps://discord.gg/VB3CgP9XTW"
                                  "\n💎 Опробуйте автопостинг мемов! Подробнее: ml/help",
                             icon_url=self.bot.get_guild(meme_rus_settings["guild"]).icon_url)
            msg = await ctx.reply(embed=embed)
            await msg.add_reaction("👍")
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
            embed.set_footer(text="Мы есть в дискорде: "
                                  "\nhttps://discord.gg/VB3CgP9XTW"
                                  "\n💎 Опробуйте автопостинг мемов! Подробнее: ml/help",
                             icon_url=self.bot.get_guild(meme_rus_settings["guild"]).icon_url)
            msg = await ctx.reply(embed=embed)
            await msg.add_reaction("👍")
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

    @Cog.listener("on_reaction_add")
    async def on_reaction_add(self, reaction, user):
        if user.bot:
            return
        if (reaction.message.author.id == settings["id"] or reaction.message.author.id == beta_settings["beta_id"]) and reaction.emoji == "👍":
            dbname = self.client['bot_memes']
            accepted_memes_collection_name = dbname["accepted_memes"]
            result = accepted_memes_collection_name.find_one({"url": reaction.message.embeds[0].image.url})
            if result is not None:
                accepted_memes_collection_name.update_one(result, {"$set": {"likes": result["likes"] + 1}})
            print(
                f"{datetime.datetime.now().strftime('%H:%M:%S')} | [USER] User {user} liked post with {result['meme_id']} id")
        elif reaction.message.channel.id == meme_rus_settings["moderationChannel"] and reaction.emoji == "✅" and \
            (reaction.message.author.id == settings["id"] or reaction.message.author.id == beta_settings["beta_id"]):
            if reaction.message.guild.id != meme_rus_settings["guild"]:
                return

            print("accept_meme")
            dbname = self.client['bot_memes']
            collection_name = dbname["memes_on_moderation"]
            result = collection_name.find_one({"msg_id": reaction.message.id})
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

                msg = await reaction.message.channel.send("Мем принят")
                await msg.delete(delay=30)
                await reaction.message.delete()
            else:
                await reaction.message.channel.send("Такого мема нет в модерации")
        elif reaction.message.channel.id == meme_rus_settings["moderationChannel"] and reaction.emoji == "❌" and \
            (reaction.message.author.id == settings["id"] or reaction.message.author.id == beta_settings["beta_id"]):
            if reaction.message.guild.id != meme_rus_settings["guild"]:
                return

            print("reject_meme")
            dbname = self.client['bot_memes']
            collection_name = dbname["memes_on_moderation"]
            result = collection_name.find_one({"msg_id": reaction.message.id})
            if result is not None:
                channel = await self.bot.get_guild(result["guild"]).get_member(result["author"]).create_dm()
                embed = discord.Embed(title="Мем", description=result["description"], color=0xff0000)
                embed.set_image(url=result["url"])
                await channel.send("К сожалению ваш мем был отклонён(", embed=embed)

                collection_name.delete_one(result)
                msg = await reaction.message.channel.send("Мем отклонён")
                await msg.delete(delay=30)
                await reaction.message.delete()
            else:
                await reaction.message.channel.send("Такого мема нет в модерации")

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

    @tasks.loop(minutes=30)
    async def auto_post_meme(self):
        #if self.post_meme is not True:
        #    self.post_meme = True
        #    return
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
                meme_result = accepted_memes_collection_name.aggregate([{"$sample": {"size": 1}}])

                for meme in meme_result:
                    embed = discord.Embed(
                        title=f'А вот и мем каждые 30 минут) <a:trippepe:901514564900913262>',
                        description=meme["description"], color=0x42aaff)
                    embed.add_field(name="Лайки:", value=f'{meme["likes"]} 👍')
                    embed.add_field(name="ID мема:", value=f'**{meme["meme_id"]}**')
                    embed.set_image(url=meme["url"])
                    embed.set_footer(text="Мы есть в дискорде: "
                                          "\nhttps://discord.gg/VB3CgP9XTW",
                                     icon_url=self.bot.get_guild(meme_rus_settings["guild"]).icon_url)
                    msg = await channel.send(embed=embed)
                    await msg.add_reaction("👍")
            except Exception:
                pass