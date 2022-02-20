import datetime
import discord
from discord.ext import commands
from config import settings, beta_settings
from luckerRole import LuckerRole
from economic import Economic
from meme_rus import Meme_Rus
from santa import SantaEvent


bot = commands.Bot(command_prefix=settings['prefix'], intents=discord.Intents.all(), help_command=None)

#bot.add_cog(LuckerRole(bot))
#bot.add_cog(Economic(bot))
bot.add_cog(Meme_Rus(bot))
#bot.add_cog(SantaEvent(bot))


@bot.event
async def on_ready():
    print(f'{datetime.datetime.now().strftime("%H:%M:%S")} | [INFO] Ready!')
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name="на Meme Land"))


@bot.command()
async def help(context):
    embed = discord.Embed(title="Помощь по командам бота", description="`!send_meme (прикреплённая картинка-мем)` - команда отправки мема"
                                                                       "\n`!meme` - показывает случайный мем", color=0x42aaff)
    embed.set_footer(text="Это ранняя версия, спасибо за выбор моего бота! (EBOLA#1337)")
    await context.send(embed=embed)


if settings["isBetaVersion"] is not True:
    bot.run(settings['token'])
else:
    bot.run(beta_settings['beta_token'])