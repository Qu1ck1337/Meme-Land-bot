import discord
import pymongo
import requests
from pymongo import MongoClient

from classes.configs.DataBase_config import profile_settings, memes_settings

CONNECTION_STRING = \
    "mongodb+srv://dbBot:j5x-Pkq-Q8u-mW2@data.frvp6.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"

client = MongoClient(CONNECTION_STRING)

db_profile = client[profile_settings["db_profile"]]
profile_collection = db_profile[profile_settings["collection_profile"]]

db_memes = client[memes_settings["db_memes"]]  # bot_memes
accepted_memes_collection = db_memes[memes_settings["accepted_memes_collection"]]  # accepted_memes
memes_on_moderation_collection = db_memes[
    memes_settings["memes_on_moderation_collection"]]  # memes_on_moderation

db_auto_post_guilds = client['auto_post_guilds']
auto_post_guilds_collection = db_auto_post_guilds["guilds"]


# region Memes_Interaction
def get_meme(meme_id: int):
    return accepted_memes_collection.find_one({"meme_id": meme_id})


def get_random_meme():
    while True:
        meme_col = accepted_memes_collection.aggregate([{"$sample": {"size": 1}}])
        for meme in meme_col:
            if requests.get(meme["url"]).ok:
                return meme


async def update_meme(object, arg_name: str, value):
    accepted_memes_collection.update_one(object, {"$set": {arg_name: value}})


async def like_meme(meme_id: int):
    meme = get_meme(meme_id)
    accepted_memes_collection.update_one(meme, {"$set": {"likes": meme["likes"] + 1}})


async def add_meme_in_moderation_collection(url: str, description: str, message_id: int,
                                            interaction: discord.Interaction):
    memes_on_moderation_collection.insert_one({
        "url": url,
        "description": description,
        "msg_id": message_id,
        "author_id": interaction.user.id,
        "guild": interaction.guild.id
    })


def get_all_memes_in_moderation():
    return memes_on_moderation_collection.find()


def get_reversed_meme():
    for meme in accepted_memes_collection.find().sort('meme_id', -1).limit(1):
        return meme


def get_top_meme():
    for meme in accepted_memes_collection.find().sort('likes', -1).limit(1):
        return meme


# endregion


def get_user(_id: int):
    user = profile_collection.find_one({"user_id": _id})
    if user is not None: return user

    result = accepted_memes_collection.find({"author": _id})

    memes_count = 0
    likes = 0

    for meme in result:
        memes_count += 1
        likes += meme["likes"]

    user_document = {
        "user_id": _id,
        "exp": 0,
        "level": 0,
        "memes_count": memes_count,
        "memes_likes": likes,
        "memes_color": "0x3498db"
    }

    profile_collection.insert_one(user_document)
    return profile_collection.find_one({"user_id": _id})


def update_user_exp(user: dict, exp: int, level: int):
    profile_collection.update_one(user, {"$set": {"level": level, "exp": exp}})


def get_user_level(_id: int):
    return get_user(_id)["level"]


def update_user_color(_id: int, color: str):
    profile_collection.update_one(get_user(_id), {"$set": {"memes_color": color}})


async def get_meme_ids_from_user(user_id: int):
    memes = accepted_memes_collection.find({"author": user_id})
    ids = [i["meme_id"] for i in memes]
    return ids


def get_top_users():
    return profile_collection.find().sort([("level", pymongo.DESCENDING), ("exp", pymongo.DESCENDING)]).limit(10)


def get_auto_meme_guilds():
    return auto_post_guilds_collection.find()


def get_auto_meme_guild(guild_id: int):
    return auto_post_guilds_collection.find_one({"guild_id": guild_id})


def add_auto_meme_guild(guild_id: int, channel_id: int):
    auto_post_guilds_collection.insert_one({
        "guild_id": guild_id,
        "channel_id": channel_id
    })


def update_channel_in_guild(guild_data: dict, new_channel_id: int):
    auto_post_guilds_collection.update_one(guild_data, {"$set": {"channel_id": new_channel_id}})


def delete_guild_from_auto_meme_list(guild_data: dict):
    auto_post_guilds_collection.delete_one(guild_data)

    # async def update_user_data(self, user_data: dict):
    #     print("start1")
    #     user_data["exp"] = 0  # 571
    #     print(user_data)
    #     db_data = await self.get_user(user_data["id"])
    #     print(db_data)
    #     if db_data is not None:
    #         print("t")
    #         await profile_collection.update_one(db_data, {"$set": user_data})
    #     print("done")
    #     print(await self.get_user(user_data["id"]))
