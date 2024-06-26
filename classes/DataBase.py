import random

import discord
import pymongo
from pymongo import MongoClient

from classes import FileManager
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

db_auto_post_guilds = client[memes_settings["auto_post_guilds_collection"]]
auto_post_guilds_collection = db_auto_post_guilds["guilds"]


# region Meme
def get_meme(meme_id: int):
    return accepted_memes_collection.find_one({"meme_id": meme_id})


def get_memes_by_tag(tag: str):
    memes = list(accepted_memes_collection.find({"tags": tag}))
    random.shuffle(memes)
    return memes


def get_all_memes():
    return accepted_memes_collection.find()


async def get_random_meme(bot):
    return list(accepted_memes_collection.aggregate([{"$sample": {"size": 1}}]))[0]
    # while True:
    #     meme_col = accepted_memes_collection.aggregate([{"$sample": {"size": 1}}])
        # for meme in meme_col:
        #     if requests.get(meme["url"]).ok:
        #         return meme
            # else:
            #     embed = discord.Embed(
            #         description=f'{"📔 **Описание:**" if meme["description"] != "" else ""} {meme["description"]}',
            #         colour=discord.Colour.red())
            #     embed.add_field(name="👁️ Просмотры", value=f"```{meme['views']} 👁️```")
            #     embed.add_field(name="👍 Лайки", value=f'```{meme["likes"]} 👍```')
            #     embed.add_field(name="🏷️ ID", value=f'```{meme["meme_id"]} 🏷```')
            #     embed.set_image(url=meme["url"])
            #     await send_user_deleted_meme_dm_message(
            #                                             meme_author=bot.get_user(meme["author"]),
            #                                             moderator=None,
            #                                             reason="Мем устарел (пробыл в боте больше 2х недель)",
            #                                             meme_embed=embed,
            #                                             meme_id=meme["meme_id"])
            #     delete_meme_by_id_from_accepted_collection(meme["meme_id"])
            #     continue


async def update_meme(object, arg_name: str, value):
    accepted_memes_collection.update_one(object, {"$set": {arg_name: value}})


async def like_meme(meme_id: int):
    meme = get_meme(meme_id)
    accepted_memes_collection.update_one(meme, {"$set": {"likes": meme["likes"] + 1}})
    profile_collection.update_one({"user_id": meme["author"]}, {"$inc": {"memes_likes": 1}})


def add_meme_in_moderation_collection(url: str, description: str, message_id: int,
                                      interaction: discord.Interaction, tags: list):
    description = description[16:] if description is not None else ""
    memes_on_moderation_collection.insert_one({
        "url": url,
        "description": description,
        "message_id": message_id,
        "author_id": interaction.user.id,
        "tags": tags
    })


def remove_meme_from_moderation_collection(message_id: int):
    memes_on_moderation_collection.delete_one({"message_id": message_id})


def get_meme_from_moderation_collection(message_id: int):
    return memes_on_moderation_collection.find_one({"message_id": message_id})


def get_all_memes_in_moderation():
    return memes_on_moderation_collection.find()


def get_reversed_meme():
    for meme in accepted_memes_collection.find().sort('meme_id', -1).limit(1):
        return meme


def get_top_meme():
    for meme in accepted_memes_collection.find().sort('likes', -1).limit(1):
        return meme


def add_viewing_to_meme(meme_id: int):
    meme = get_meme(meme_id)
    views = meme["views"] + 1
    accepted_memes_collection.update_one(meme, {"$set": {"views": views}})


def transfer_meme_from_moderation_to_accepted(message_id: int) -> int:
    moderation_meme = get_meme_from_moderation_collection(message_id)
    meme_id = 1
    for last_meme in accepted_memes_collection.find().sort('_id', -1).limit(1):
        meme_id = last_meme["meme_id"] + 1

    accepted_memes_collection.insert_one({
        "meme_id": meme_id,
        "author": moderation_meme["author_id"],
        "description": moderation_meme["description"],
        "url": FileManager.save_meme(moderation_meme["url"]),
        "tags": moderation_meme["tags"],
        "views": 0,
        "likes": 0
    })
    profile_collection.update_one({"user_id": moderation_meme["author_id"]}, {"$inc": {"memes_count": 1}})
    remove_meme_from_moderation_collection(message_id)
    return meme_id


def delete_meme_by_id_from_accepted_collection(meme_id: int):
    result = accepted_memes_collection.delete_one({"meme_id": meme_id})
    return True if result.deleted_count > 0 else False

# endregion

#region User
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
#endregion

#region Guild
def get_auto_meme_guilds(time: int=None):
    if time is not None:
        return auto_post_guilds_collection.find({"posting_time": time})
    else:
        return auto_post_guilds_collection.find()


def get_auto_meme_guild(guild_id: int):
    return auto_post_guilds_collection.find_one({"guild_id": guild_id})


def add_auto_meme_guild(guild_id: int, channel_id: int, time: int):
    auto_post_guilds_collection.insert_one({
        "guild_id": guild_id,
        "channel_id": channel_id,
        "posting_time": time
    })


def update_autoposing_in_guild(guild_data: dict, new_channel_id: int, time: int):
    auto_post_guilds_collection.update_one(guild_data, {"$set": {"channel_id": new_channel_id, "posting_time": time}})


def delete_guild_from_auto_meme_list(guild_data: dict):
    auto_post_guilds_collection.delete_one(guild_data)
#endregion

# meme_id = 1
# for meme in db_memes["accepted_memes"].find():
#     new_url = save_meme(meme["url"])
#     print(new_url)
#     if new_url is not None:
#         accepted_memes_collection.insert_one({
#             "meme_id": meme_id,
#             "author": meme["author"],
#             "description": meme["description"],
#             "url": new_url,
#             "likes": meme["likes"],
#             "views": meme["views"],
#             "tags": []
#         })
#         meme_id += 1

# for meme in db_memes["accepted_memes"].find():
#     db_memes["accepted_memes"].delete_one(meme)
#
# for meme in db_memes["accepted_memes_test"].find():
#     db_memes["accepted_memes"].insert_one(meme)