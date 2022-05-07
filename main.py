import asyncio
import datetime
import os
import discord
from discord.ext import commands, tasks
from config import settings, beta_settings

intents = discord.Intents(guilds=True, members=True, emojis=True, messages=True, reactions=True, typing=True)

bot = commands.Bot(command_prefix=settings['prefix'], help_command=None, intents=intents,
                   application_id=934900322634190878)

@bot.event
async def on_ready():
    await bot.tree.sync(guild=bot.get_guild(892493256129118260))
    await bot.tree.sync(guild=bot.get_guild(766386682047365190))
    await bot.tree.sync()
    update_status.start()
    print(await bot.tree.fetch_commands())
    print(f'{datetime.datetime.now().strftime("%H:%M:%S")} | [INFO] Ready!')


status_id = 0
@tasks.loop(minutes=1)
async def update_status():
    global status_id
    if status_id == 0:
        await bot.change_presence(
            activity=discord.Activity(type=discord.ActivityType.watching, name=f"/help | {len(bot.guilds)} серверов!"))
        status_id += 1
    elif status_id == 1:
        await bot.change_presence(
            activity=discord.Activity(type=discord.ActivityType.watching, name=f"/help | {len(bot.users)} пользователей!"))
        status_id = 0


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
                                                                           f"\n/leaderboard - показывает таблицу лидеров```"
                                                                           f"\n"
                                                                           f"\n**Для администраторов** (`Администратор` / `Управлять сервером` права)"
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
                                                                           f"\n/leaderboard - показывает таблицу лидеров```"
                                                                           f"\n"
                                                                           f"\n**Для администраторов** (`Администратор` / `Управлять сервером` права)"
                                                                           f"\n```/auto_meme - устанавливает канал, где была использована команда, для автопостинга мема раз в 30 минут"
                                                                           f"\n/auto_meme <#канал> - устанавливает канал, который был задан в параметре, для автопостинга мема раз в 30 минут"
                                                                           f"\n/stop_auto_meme - приостанавливает автопостинг мемов на данном сервере```",
                              color=0x42aaff)
    embed.set_footer(text=f"\"Спасибо за выбор нашего бота!\" 💗 - EBOLA (создатель бота)")
    await interaction.response.send_message(embed=embed)


@bot.tree.error
async def on_slash_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    print(error)
    if error == discord.app_commands.errors.MissingPermissions:
        await interaction.response.send_message(f"У вас недостаточно прав, чтобы использовать эту команду"
                                                f"\n`Администратор` / `Управлять сервером` права нужны для этой команды.")
    else:
        await interaction.response.send_message(f"Произошла ошибка во время выполнения команды, возможно у вас недостаточно прав, чтобы использовать команду, либо произошла ошибка в самом боте.")


#@bot.command()
async def send_info_to_all_servers(ctx):
    if await bot.is_owner(ctx.author):
        for guild in bot.guilds:
            try:
                channel = guild.system_channel
                second_embed = discord.Embed(title="Срочные новости!",
                                             description="Все старые команды бота с этого момента доступны через **slash-команды** (`/`). Это удобно для пользователя, а также разработчика 😉"
                                                         "\nЕсли у вас недоступны команды бота (не видны в контекстном меню) при использовании `/`, тогда **ПЕРЕПРИГЛАСИТЕ БОТА**"
                                                         "\n**Примечание**: перепригласить бота можно нажав на кнопку `Добавить на сервер` в профиле бота.",
                                             color=0x42aaff)
                await channel.send(embed=second_embed)
            except Exception:
                pass
        await ctx.reply("Done!")


'''@bot.command()
async def dele(ctx):
    print(bot.remove_command("help"))


@bot.command()
async def fetc(ctx):
    print(await bot.tree.fetch_commands())
    print(bot.tree.get_command("help"))

@bot.command()
async def sync_bot(ctx):
    print("sync commands")
    await bot.tree.sync(guild=ctx.guild)
    await bot.tree.sync()'''


async def main():
    async with bot:
        await load_extensions()
        if settings["isBetaVersion"] is not True:
            await bot.start(settings['token'])
        else:
            await bot.start(beta_settings['beta_token'])


async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            # cut off the .py from the file name
            await bot.load_extension(f"cogs.{filename[:-3]}")

asyncio.run(main())