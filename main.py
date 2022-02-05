import datetime
import discord
from discord.ext import commands
from config import settings, beta_settings
from luckerRole import LuckerRole
from economic import Economic
from santa import SantaEvent

bot = commands.Bot(command_prefix=settings['prefix'], intents=discord.Intents.all())

bot.add_cog(LuckerRole(bot))
bot.add_cog(Economic(bot))
#bot.add_cog(SantaEvent(bot))


@bot.event
async def on_ready():
    print(f'{datetime.datetime.now().strftime("%H:%M:%S")} | [INFO] Ready!')
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name="Разрабатываюсь EBOLAЙ"))

if settings["isBetaVersion"] is not True:
    bot.run(settings['token'])
else:
    bot.run(beta_settings['beta_token'])