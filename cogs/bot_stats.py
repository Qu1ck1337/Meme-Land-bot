import asyncio
import discord
from discord import app_commands
from discord.ext import tasks
from discord.ext import commands

from classes.Logger import log_to_console


class BotStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.shards = {}
        self.update_stats_loop.start()

    @tasks.loop(minutes=60)
    async def update_stats_loop(self):
        self.shards = {}
        for shard in self.bot.shards.values():
            shard_id = shard.id
            # shard_ping = shard.latency
            shard_servers = [guild for guild in self.bot.guilds if guild.shard_id == shard_id]
            members = sum([guild.member_count for guild in shard_servers])
            self.shards[shard.shard_count] = [len(shard_servers), members]

        await self.bot.change_presence(
            activity=discord.Activity(type=discord.ActivityType.watching,
                                      name=f"/help | {(len(self.bot.guilds) / 1000):.1f}К серверов"))
        log_to_console("Update Bot activity")

    @app_commands.command(name="stats", description="Статистика бота")
    async def stats(self, interaction: discord.Interaction):
        await interaction.response.defer()
        embed = discord.Embed(title="Статистика бота",
                              description=f"Cерверов: `{len(self.bot.guilds)}`\n"
                                          f"Пользователей: `{len(self.bot.users)}`\n"
                                          f"\n"
                                          f"Текущий пинг: `{int(self.bot.latency * 1000)} ms`\n"
                                          f"Номер шарда этого сервера: `#{self.bot.get_shard(interaction.guild.shard_id).shard_count}`",
                              colour=discord.Colour.blue())
        shard_list = ""
        for shard_count, value in self.shards.items():
            shard_list += f"**Шард #{shard_count}** | Серверов: `{value[0]}` Пользователей: `{value[1]}`\n"
        embed.add_field(name="Информация по шардам:", value=shard_list)
        await interaction.edit_original_response(embed=embed)

    @app_commands.command(name="vote", description="Проголосовать за Meme Land")
    async def vote(self, interaction: discord.Interaction):
        await interaction.response.send_message(embed=discord.Embed(description="Апать бота можно раз в 4 часа, но ваш вклад для меня очень ценен ❤️\n"
                                                                                "[Мониторинг](https://bots.server-discord.com/894952935442747393)",
                                                                    colour=discord.Colour.blurple()))


async def setup(bot):
    log_to_console(f"Loaded {__file__}")
    await bot.add_cog(BotStats(bot))