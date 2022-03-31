import discord
from discord.ext import commands
from discord import app_commands


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("Pong! 😄")

    '''@app_commands.command(name="test")
    @app_commands.guilds(766386682047365190)
    async def test(self, interaction: discord.Interaction):
        await interaction.response.send_message("Hello from command 1!", ephemeral=True)'''


async def setup(bot):
    print("Setup Fun")
    await bot.add_cog(Fun(bot))