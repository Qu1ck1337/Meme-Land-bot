import discord
from discord.ext import commands
from pymongo import MongoClient
from config import profile_settings


class User_profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Provide the mongodb atlas url to connect python to mongodb using pymongo
        self.CONNECTION_STRING = "mongodb+srv://dbBot:j5x-Pkq-Q8u-mW2@data.frvp6.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
        # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
        self.client = MongoClient(self.CONNECTION_STRING)

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
        embed.set_thumbnail(url=ctx.author.avatar_url)
        await ctx.reply(embed=embed)

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