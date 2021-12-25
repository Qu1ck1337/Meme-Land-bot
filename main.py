from discord.ext import commands
from config import settings
from meme import Meme
from luckerRole import LuckerRole

bot = commands.Bot(command_prefix=settings['prefix'])

# bot.add_cog(Meme(bot))
bot.add_cog(LuckerRole(bot))

@bot.event
async def on_ready():
    print('Ready!')

bot.run(settings['token'])