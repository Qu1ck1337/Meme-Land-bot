import asyncio
import datetime
import os
import discord
from discord.ext import commands, tasks

from classes import StaticParameters
from classes.DataBase import get_all_memes_in_moderation
from classes.User import User
from classes.configs.memes_channels_config import logs_moderation_logs, new_memes_channel
from cogs.meme_moderation import ModerationButtons
from config import settings, beta_settings, release_settings

intents = discord.Intents(guilds=True, members=True, emojis=True, messages=True, reactions=True, typing=True)
                          #message_content=True)

bot = commands.Bot(command_prefix=settings['prefix'], help_command=None, intents=intents,
                   application_id=release_settings["application_id"] if settings["isBetaVersion"] is False else
                   beta_settings["application_id"])
status_id = 0


@bot.event
async def on_ready():
    StaticParameters.main_bot_guild = bot.get_guild(892493256129118260)
    StaticParameters.log_channel = bot.get_channel(logs_moderation_logs)
    StaticParameters.new_memes_channel = bot.get_channel(new_memes_channel)
    await bot.tree.sync(guild=bot.get_guild(892493256129118260))
    await bot.tree.sync(guild=bot.get_guild(766386682047365190))
    await bot.tree.sync()
    print(f'{datetime.datetime.now().strftime("%H:%M:%S")} | [INFO] Ready!')
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.playing, name=f"Testing Version 3 Alpha"))

@bot.event
async def setup_hook():
    for meme in get_all_memes_in_moderation():
        bot.add_view(ModerationButtons(bot), message_id=meme["message_id"])


# @tasks.loop(minutes=1)
# async def update_status():
    # global status_id
    # if status_id == 0:
    #     await bot.change_presence(
    #         activity=discord.Activity(type=discord.ActivityType.playing, name=f"/help | {len(bot.guilds)} серверов!"))
    #     status_id += 1
    # elif status_id == 1:
    #     await bot.change_presence(
    #         activity=discord.Activity(type=discord.ActivityType.playing, name=f"/help | {len(bot.users)} пользователей!"))
    #     status_id = 0


@bot.tree.error
async def on_slash_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    print(error)
    # if error == discord.app_commands.errors.MissingPermissions:
    #     await interaction.response.send_message(f"У вас недостаточно прав, чтобы использовать эту команду"
    #                                             f"\n`Администратор` / `Управлять сервером` права нужны для этой команды.")
    # else:
    #     await interaction.response.send_message(f"Произошла ошибка во время выполнения команды, возможно у вас недостаточно прав, чтобы использовать команду, либо произошла ошибка в самом боте.")


async def main():
    print("Starting Bot")
    async with bot:
        await load_extensions()
        if settings["isBetaVersion"] is not True:
            await bot.start(release_settings['token'])
        else:
            await bot.start(beta_settings['token'])


async def load_extensions():
    print("Loading extensions from Cogs \n---------------------")
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            # cut off the .py from the file name
            await bot.load_extension(f"cogs.{filename[:-3]}")

    # print("Loading extensions from Classes \n---------------------")
    # for filename in os.listdir("./classes"):
    #     if filename.endswith(".py"):
    #         # cut off the .py from the file name
    #         await bot.load_extension(f"classes.{filename[:-3]}")


def get_user_name(user_id: int):
    return bot.get_user(user_id).display_name



asyncio.run(main())