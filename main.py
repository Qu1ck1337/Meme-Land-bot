import asyncio
import datetime
import os
import discord
from discord.ext import commands, tasks

from classes import StaticParameters
from classes.DataBase import get_all_memes_in_moderation
from classes.User import User
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
    StaticParameters.meme_land_guild = bot.get_guild(892493256129118260)
    await bot.tree.sync(guild=bot.get_guild(892493256129118260))
    await bot.tree.sync(guild=bot.get_guild(766386682047365190))
    await bot.tree.sync()
    #update_status.start()
    print(f'{datetime.datetime.now().strftime("%H:%M:%S")} | [INFO] Ready!')
    # user = User(443337837455212545)
    # await user.update_local_data()
    # await user.push_data()
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


@bot.tree.command(name="help", description="Помощь по командам бота")
async def help(interaction: discord.Interaction):
    if interaction.guild_id == settings["guild"]:
        embed = discord.Embed(title="Помощь по командам бота", description=f"**Команды для сервера Meme Land**"
                                                                           f"\n```/balance - узнать свой баланс монеток"
                                                                           f"\n/balance <@участник> - узнать баланс участника сервера Meme Land"
                                                                           f"\n/send_money <@участник> - отправить монетки участнику севрера Meme Land"
                                                                           f"\n/shop - открыть магазин Жорика"
                                                                           f"\n/shop <страница(номер)> - открыть магазин Жорика на определённой странице"
                                                                           f"\n/buy <номер товара> - купить предмет в магазине Жорика```"
                                                                           f"\n"
                                                                           f"\n**Команды для всех серверов**"
                                                                           f"\n```/send_meme <описание мема> + картинка` - команда отправки мема"
                                                                           f"\n/meme - показывает случайный мем"
                                                                           f"\n/meme <id мема> - показывает мем с нужным id"
                                                                           f"\n/last_meme - показывает последний залитый мем"
                                                                           f"\n/top_meme - показывает самый лучший мем бота"
                                                                           f"\n/profile - показывает ваш мемный профиль"
                                                                           f"\n/leaderboard - показывает таблицу лидеров"
                                                                           f"\n/plus_info - узнать преимущества поддержки бота"
                                                                           f"\n/meme_plus - поддержать бота```"
                                                                           f"\n"
                                                                           f"\n**Для meme+ пользователей**"
                                                                           f"\n```/plus_settings - ваши meme+ настройки профиля"
                                                                           f"\n/meme_color <red> <green> <blue> - настроить цвет ваших мемов, параметр RGB"
                                                                           f"\n/set_publicity <показать ник> <показать тег> - настроить публичность"
                                                                           f"\n/set_url <показать URL> <URL> - встроить URL ссылку в мем```"
                                                                           f"\n"
                                                                           f"\n**Для администраторов серверов** (`Администратор` / `Управлять сервером` права)"
                                                                           f"\n```/auto_meme - устанавливает канал, где была использована команда, для автопостинга мема раз в 30 минут"
                                                                           f"\n/auto_meme <#канал> - устанавливает канал, который был задан в параметре, для автопостинга мема раз в 30 минут"
                                                                           f"\n/stop_auto_meme - приостанавливает автопостинг мемов на данном сервере```",
                              color=0x42aaff)
    else:
        embed = discord.Embed(title="Помощь по командам бота", description=f"**Для всех пользователей**"
                                                                           f"```/send_meme <описание мема> + картинка` - команда отправки мема"
                                                                           f"\n/meme - показывает случайный мем"
                                                                           f"\n/meme <id мема> - показывает мем с нужным id"
                                                                           f"\n/last_meme - показывает последний залитый мем"
                                                                           f"\n/top_meme - показывает самый лучший мем бота"
                                                                           f"\n/profile - показывает ваш мемный профиль"
                                                                           f"\n/leaderboard - показывает таблицу лидеров"
                                                                           f"\n/plus_info - узнать преимущества поддержки бота"
                                                                           f"\n/meme_plus - поддержать бота```"
                                                                           f"\n"
                                                                           f"\n**Для meme+ пользователей**"
                                                                           f"\n```/plus_settings - ваши meme+ настройки профиля"
                                                                           f"\n/meme_color <red> <green> <blue> - настроить цвет ваших мемов, параметр RGB"
                                                                           f"\n/set_publicity <показать ник> <показать тег> - настроить публичность"
                                                                           f"\n/set_url <показать URL> <URL> - встроить URL ссылку в мем```"
                                                                           f"\n"
                                                                           f"\n**Для администраторов серверов** (`Администратор` / `Управлять сервером` права)"
                                                                           f"\n```/auto_meme - устанавливает канал, где была использована команда, для автопостинга мема раз в 30 минут"
                                                                           f"\n/auto_meme <#канал> - устанавливает канал, который был задан в параметре, для автопостинга мема раз в 30 минут"
                                                                           f"\n/stop_auto_meme - приостанавливает автопостинг мемов на данном сервере```",
                              color=0x42aaff)
    embed.set_footer(text=f"\"Спасибо за выбор нашего бота!\" 💗 - EBOLA (создатель бота)")
    await interaction.response.send_message(embed=embed)


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