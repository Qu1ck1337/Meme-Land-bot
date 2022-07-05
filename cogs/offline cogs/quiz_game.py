import datetime
import random

import asyncio
import discord
from discord.ext import commands
from discord import app_commands
from discord.ext.commands import Cog
from pymongo import MongoClient

import meme_quiz

# Provide the mongodb atlas url to connect python to mongodb using pymongo
from config import profile_settings

CONNECTION_STRING = \
    "mongodb+srv://dbBot:j5x-Pkq-Q8u-mW2@data.frvp6.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
# Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
CLIENT = MongoClient(CONNECTION_STRING)

DB_PROFILE = CLIENT[profile_settings["db_profile"]]
PROFILE_COLLECTION = DB_PROFILE[profile_settings["collection_profile"]]

DB_GAMES = CLIENT["bot_games"]
CURRENT_GAMES_COLLECTION = DB_GAMES["current_games"]

CHANNELS_WITH_GAMES = []


class Quiz_Game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(description="Сыграть в мемную викторину")
    @app_commands.guilds(892493256129118260)
    async def quiz(self, interaction: discord.Interaction):
        question_num = random.choice(list(meme_quiz.Questions.keys()))
        question_list = meme_quiz.Questions[question_num]
        question = question_list[0]
        answers_not_sorted = question_list[1:5]
        answers = ""
        for num, answer in enumerate(answers_not_sorted):
            answers += f"\n> {num + 1}. {answer}"
        question_embed = discord.Embed(title="Мемная викторина",
                                       description=f"{question}"
                                                   f"{answers}",
                                       colour=discord.Colour.blue())
        game_ids = CURRENT_GAMES_COLLECTION.find().sort('game_id', -1).limit(1)
        game_id = None

        for _id in game_ids:
            game_id = _id + 1
        if game_id is None:
            game_id = 0

        CURRENT_GAMES_COLLECTION.insert_one({
            "game_id": game_id,
            "game_guild_id": interaction.guild.id,
            "game_channel_id": interaction.channel.id,
            "right_answer": str(question_list[5]),
            "winners": [],
            "losers": [],
            "end_time": datetime.datetime.now() + datetime.timedelta(minutes=1)
        })

        await asyncio.wait_for(self.end_game(game_id), timeout=60)
        await interaction.response.send_message(embed=question_embed)

    @Cog.listener("on_message")
    async def on_message(self, message):
        if len(message.content) == 1 and message.content in "1234":
            result = CURRENT_GAMES_COLLECTION.find({"game_guild_id": message.guild.id, "game_channel_id": message.channel.id})
            if result is not None and message.author.id not in result["winners"] and message.author.id not in result["losers"]:
                if message.content == result["right_answer"]:
                    CURRENT_GAMES_COLLECTION.update_one(result, {"winners": result["winners"].append(message.author.id)})
                    print(CURRENT_GAMES_COLLECTION.find_one({"game_guild_id": message.guild.id, "game_channel_id": message.channel.id})["winners"])
                else:
                    CURRENT_GAMES_COLLECTION.update_one(result, {"losers": result["losers"].append(message.author.id)})

    async def end_game(self, game_id):
        game = CURRENT_GAMES_COLLECTION.find_one_and_delete({"game_id": game_id})
        final_embed = discord.Embed(title="Стоп игра!", description="Тест")
        await self.bot.get_guild(game["game_guild_id"]).get_channel(game["game_channel_id"]).send(embed=final_embed)


async def setup(bot):
    print("Setup Quiz_Game")
    await bot.add_cog(Quiz_Game(bot))
