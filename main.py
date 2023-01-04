import asyncio
import os
import discord
from discord import app_commands
from discord.ext import commands, tasks

from classes import StaticParameters
from classes.DataBase import get_all_memes_in_moderation
from classes.Logger import log_to_console, error_to_console, success_to_console, warn_to_console
from classes.configs.memes_channels_config import logs_moderation_logs, new_memes_channel
from cogs.meme_moderation import ModerationButtons
from config import settings, beta_settings, release_settings

intents = discord.Intents(guilds=True, members=True, emojis=True, messages=True, reactions=True, typing=True)
                          #message_content=True)

bot = commands.AutoShardedBot(command_prefix=settings['prefix'], help_command=None, intents=intents,
                   application_id=release_settings["application_id"] if settings["isBetaVersion"] is False else
                   beta_settings["application_id"])


@bot.event
async def on_ready():
    print("coming ready")
    StaticParameters.main_bot_guild = bot.get_guild(892493256129118260)
    StaticParameters.log_channel = bot.get_channel(logs_moderation_logs)
    StaticParameters.new_memes_channel = bot.get_channel(new_memes_channel)
    await bot.tree.sync(guild=bot.get_guild(892493256129118260))
    await bot.tree.sync(guild=bot.get_guild(766386682047365190))
    await bot.tree.sync()
    success_to_console("Bot is ready")
    update_status.start()


@bot.event
async def setup_hook():
    for meme in get_all_memes_in_moderation():
        bot.add_view(ModerationButtons(bot), message_id=meme["message_id"])


@tasks.loop(minutes=60)
async def update_status():
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name=f"/help | {(len(bot.guilds) / 1000):.1f}К серверов"))
    log_to_console("Update Bot activity")


@bot.tree.error
async def on_slash_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(str(error), ephemeral=True)
    else:
        error_to_console(error)


async def main():
    print("Bot powered by Qu1ck_1337 (AKA EBOLA)")
    log_to_console(f"Starting bot")
    async with bot:
        await load_extensions()
        if settings["isBetaVersion"] is not True:
            await bot.start(release_settings['token'])
        else:
            warn_to_console("Test version is running")
            await bot.start(beta_settings['token'])


async def load_extensions():
    log_to_console("Loading extensions from Cogs...")
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            # cut off the .py from the file name
            await bot.load_extension(f"cogs.{filename[:-3]}")


def get_user_name(user_id: int):
    return bot.get_user(user_id).display_name

asyncio.run(main())