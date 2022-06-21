import discord
from discord.ext import commands
from discord import app_commands


def Check_if_it_is_me(interaction: discord.Interaction) -> bool:
    return interaction.user.id == 443337837455212545


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("Pong! 😄")

    @app_commands.command()
    @app_commands.guilds(892493256129118260)
    @app_commands.check(Check_if_it_is_me)
    async def send_info_to_all_servers(self, interaction):
        for guild in self.bot.guilds:
            try:
                channel = guild.system_channel
                second_embed = discord.Embed(title="Розыгрыш от создателя бота! 🥳",
                                             description="⚡ На нашем официальном сервере в честь **1000** участников "
                                                         "проходит розыгрыш в общей сумме на `1000 рублей`, включая 🚀 **meme+**! Всего **3** победителя)",
                                             colour=discord.Colour.gold())
                second_embed.add_field(name="\nСкорее участвуй:", value="👉 https://discord.gg/D84dsWug9d", )
                await channel.send(embed=second_embed)
            except Exception:
                pass
        await interaction.response.send_message("Done!")


async def setup(bot):
    print("Setup Fun")
    await bot.add_cog(Fun(bot))
