import discord
from discord.ext import commands
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

    @commands.command()
    async def send_meme(self, ctx, *content):
        if ctx.author.bot:
            return
        moderation_channel = self.bot.get_guild(meme_rus_settings["guild"]).get_channel(meme_rus_settings["moderationChannel"])
        if len(ctx.message.attachments) > 0:
            dbname = self.client['bot_memes']
            collection_name = dbname["memes_on_moderation"]
            if ctx.message.attachments[0].url.split('.')[-1].lower() not in ['png', 'jpg', 'gif', 'jpeg']:
                await ctx.reply("Вылкадывание видео пока недоступно, в скором времени добавим)")
                return
            if collection_name.find_one({"url": ctx.message.attachments[0].url}) is None:
                description = " ".join(content)
                embed = discord.Embed(title="Новый мем на модерацию", description=description, color=0xFFCC33)
                embed.set_image(url=ctx.message.attachments[0])
                msg = await moderation_channel.send(embed=embed)
                collection_name.insert_one(
                    {
                        "url": ctx.message.attachments[0].url,
                        "msg_id": msg.id,
                        "author": ctx.author.id,
                        "description": description,
                        "guild": ctx.guild.id
                    })
                msg = await ctx.reply("Ваш мем отправлен на модерацию =)")
                await msg.delete(delay=30)
            else:
                ctx.reply("Такой мем уже есть")
        else:
            await ctx.reply("Мема нема")

    @commands.command()
    async def meme(self, ctx):
        dbname = self.client['bot_memes']
        accepted_memes_collection_name = dbname["accepted_memes"]

        random_record = accepted_memes_collection_name.aggregate([{"$sample": {"size": 1}}])
        for result in random_record:
            embed = discord.Embed(title=random.choice(meme_rus_settings["get_meme_phrases"]), description=result["description"], color=0x42aaff)

            try:
                likes = result["likes"]
            except KeyError:
                accepted_memes_collection_name.update_one(result, {"$set": {"likes": 0}})
                likes = result["likes"]

            embed.add_field(name="Лайки:", value=f'{likes} 👍')
            embed.set_image(url=result["url"])
            embed.set_footer(text="Мы есть в дискорде: "
                                  "\nhttps://discord.gg/VB3CgP9XTW", icon_url=self.bot.get_guild(meme_rus_settings["guild"]).icon_url)
            msg = await ctx.reply(embed=embed)
            await msg.add_reaction("👍")

    @commands.command()
    @commands.has_any_role(939801337196073030, 905484393919967252, 906632280376741939)
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

                collection_name.delete_one(result)

                msg = await ctx.reply("Мем принят")
                await msg.delete(delay=30)
                await message.delete()
            else:
                await ctx.reply("Такого мема нет в модерации")
            await ctx.message.delete()

    @commands.command()
    @commands.has_any_role(939801337196073030, 905484393919967252, 906632280376741939)
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
        if (reaction.message.author == settings["id"] or reaction.message.author.id == beta_settings["beta_id"]) and reaction.emoji == "👍":
            dbname = self.client['bot_memes']
            accepted_memes_collection_name = dbname["accepted_memes"]
            result = accepted_memes_collection_name.find_one({"url": reaction.message.embeds[0].image.url})
            if result is not None:
                accepted_memes_collection_name.update_one(result, {"$set": {"likes": result["likes"] + 1}})