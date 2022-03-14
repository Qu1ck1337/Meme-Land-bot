import datetime
import discord
from discord.ext import commands, tasks
from config import settings, beta_settings
from luckerRole import LuckerRole
from economic import Economic
from meme_rus import Meme_Rus
from fun import Fun
from santa import SantaEvent


bot = commands.Bot(command_prefix=settings['prefix'], intents=discord.Intents.all(), help_command=None)

#bot.add_cog(LuckerRole(bot))
#bot.add_cog(Economic(bot))
bot.add_cog(Meme_Rus(bot))
#bot.add_cog(Fun(bot))
#bot.add_cog(SantaEvent(bot))


@bot.event
async def on_ready():
    print(f'{datetime.datetime.now().strftime("%H:%M:%S")} | [INFO] Ready!')
    update_status.start()


@tasks.loop(minutes=1)
async def update_status():
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(bot.guilds)} серверов!"))


@bot.command()
async def help(context):
    if context.guild.id == settings["guild"]:
        embed = discord.Embed(title="Помощь по командам бота", description=f"Команды для сервера **Meme Land**:"
                                                                           f"\n`{settings['prefix']}balance` - узнать свой баланс монеток"
                                                                           f"\n`{settings['prefix']}balance <@участник>` - узнать баланс участника сервера **Meme Land**"
                                                                           f"\n`{settings['prefix']}send_money <@участник>` - отправить монетки участнику севрера **Meme Land**"
                                                                           f"\n`{settings['prefix']}shop` - открыть магазин Жорика"
                                                                           f"\n`{settings['prefix']}shop <страница(номер)>` - открыть магазин Жорика на определённой странице"
                                                                           f"\n`{settings['prefix']}buy <номер товара>` - купить предмет в магазине Жорика"
                                                                           f"\n"
                                                                           f"\nКоманды для всех серверов:"
                                                                           f"\n`{settings['prefix']}send_meme <описание мема>` + ОБЯЗАТЕЛЬНО прикреплённая картинка - команда отправки мема"
                                                                           f"\n`{settings['prefix']}meme` - показывает случайный мем"
                                                                           f"\n`{settings['prefix']}meme <id мема>` - показывает мем с нужным id"
                                                                           f"\n`{settings['prefix']}last_meme` - показывает последний залитый мем"
                                                                           f"\n`{settings['prefix']}top_meme` - показывает самый лучший мем бота"
                                                                           f"\n"
                                                                           f"\n**Новинка!**"
                                                                           f"\n`{settings['prefix']}auto_meme` - устанавливает канал, где была использована команда, для автопостинга мема раз в 30 минут"
                                                                           f"\n > **Это команда работает только для администраторов сервера**"
                                                                           f"\n`{settings['prefix']}auto_meme <#канал>` - устанавливает канал, который был задан в параметре, для автопостинга мема раз в 30 минут"
                                                                           f"\n > **Это команда работает только для администраторов сервера**"
                                                                           f"\n`{settings['prefix']}stop_auto_meme` - приостанавливает автопостинг мемов на данном сервере"
                                                                           f"\n > **Это команда работает только для администраторов сервера**",
                              color=0x42aaff)
        await context.send(embed=embed)
    else:
        embed = discord.Embed(title="Помощь по командам бота", description=f"`{settings['prefix']}send_meme <описание мема>` + ОБЯЗАТЕЛЬНО прикреплённая картинка - команда отправки мема"
                                                                           f"\n`{settings['prefix']}meme` - показывает случайный мем"
                                                                           f"\n`{settings['prefix']}meme <id мема>` - показывает мем с нужным id"
                                                                           f"\n`{settings['prefix']}last_meme` - показывает последний залитый мем"
                                                                           f"\n`{settings['prefix']}top_meme` - показывает самый лучший мем бота"
                                                                           f"\n"
                                                                           f"\n**Новинка!**"
                                                                           f"\n`{settings['prefix']}auto_meme` - устанавливает канал, где была использована команда, для автопостинга мема раз в 30 минут"
                                                                           f"\n > **Это команда работает только для администраторов сервера**"
                                                                           f"\n`{settings['prefix']}auto_meme <#канал>` - устанавливает канал, который был задан в параметре, для автопостинга мема раз в 30 минут"
                                                                           f"\n > **Это команда работает только для администраторов сервера**"
                                                                           f"\n`{settings['prefix']}stop_auto_meme` - приостанавливает автопостинг мемов на данном сервере"
                                                                           f"\n > **Это команда работает только для администраторов сервера**",
                              color=0x42aaff)
        embed.set_footer(text="Это ранняя версия моего бота, спасибо за ваш выбор! 💗 (EBOLA#1337)")
        await context.send(embed=embed)


@bot.event
async def on_command_error(context, exception):
    #if isinstance(exception, discord.ext.commands.errors.CommandNotFound):
    #    await context.send(f"Неизвестная команда :/ "
    #                       f"\n`{settings['prefix']}help` - чтобы узнать все команды бота")
    if isinstance(exception, discord.ext.commands.errors.BadArgument):
        await context.reply(f"Неправильно введена команда :/ "
                    f"\n`{settings['prefix']}help` - чтобы подробнее узнать все команды бота")


#@bot.command()
async def send_info_to_all_servers(ctx):
    if await bot.is_owner(ctx.author):
        for guild in bot.guilds:
            try:
                channel = guild.system_channel
                await channel.send("test")
            except Exception:
                pass


if settings["isBetaVersion"] is not True:
    bot.run(settings['token'])
else:
    bot.run(beta_settings['beta_token'])