from discord.ext import commands


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.reply("Pong! 😄")


async def setup(bot):
    print("Setup Fun")
    await bot.add_cog(Fun(bot))