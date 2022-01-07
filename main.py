from discord.ext import commands
from config import settings
from luckerRole import LuckerRole
from santa import SantaEvent

bot = commands.Bot(command_prefix=settings['prefix'])

bot.add_cog(LuckerRole(bot))
#bot.add_cog(SantaEvent(bot))

@bot.event
async def on_ready():
    print('Ready!')

bot.run(settings['token'])
