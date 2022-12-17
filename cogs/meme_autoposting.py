import datetime

import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.ext.commands import Cog

from classes.DataBase import get_auto_meme_guilds, get_auto_meme_guild, add_auto_meme_guild, update_channel_in_guild, \
    delete_guild_from_auto_meme_list
from classes.MemeObjects import RandomedMeme
from cogs.memes_watching import LikeMeme


class MemeAutoPosting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener("on_ready")
    async def on_ready(self):
        self.auto_post_meme.start()

    @tasks.loop(seconds=1)
    async def auto_post_meme(self):
        channels = self.bot.get_all_channels()
        channels_in_guilds = []
        sorted_channels_in_guilds = []
        for guild in get_auto_meme_guilds():
            channels_in_guilds.append(guild["channel_id"])
        for channel in channels:
            if channel.id in channels_in_guilds:
                sorted_channels_in_guilds.append(channel)

        for channel in sorted_channels_in_guilds:
            try:
                meme = RandomedMeme(self.bot)
                await channel.send(embed=meme.get_embed(title="❄ Случайный мемчик! ❄"), view=LikeMeme(
                    meme_id=meme.get_meme_id(),
                    bot=self.bot))
            except AttributeError as ex:
                pass

    @app_commands.guilds(766386682047365190)
    @app_commands.command(description="Устанавливает автопостинг мемов раз в 30 минут")
    @app_commands.describe(channel="Канал, где нужно постить мемы (по умолчанию этот канал)")
    @app_commands.checks.has_permissions(administrator=True, manage_guild=True)
    async def auto_meme(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        if channel is None:
            channel = interaction.channel

        result = get_auto_meme_guild(interaction.guild_id)
        if result is None:
            add_auto_meme_guild(interaction.guild_id, channel.id)
        else:
            update_channel_in_guild(result, channel.id)

        await interaction.response.send_message(
            embed=discord.Embed(title="Круто! 🎉",
                                description=f"Автопостинг мемов успешно установлен на канале: {channel.mention}",
                                colour=discord.Colour.green(),
                                timestamp=datetime.datetime.now()))

    @app_commands.guilds(766386682047365190)
    @app_commands.command(description="Останавливает автопостинг мемов на этом сервере")
    @app_commands.checks.has_permissions(administrator=True, manage_guild=True)
    async def stop_auto_meme(self, interaction: discord.Interaction):
        result = get_auto_meme_guild(interaction.guild_id)
        if result is not None:
            delete_guild_from_auto_meme_list(result)
            await interaction.response.send_message(
                embed=discord.Embed(title="Приостановление 🔕",
                                    description=f"Автопостинг мемов на этом сервере приостановлен 😢",
                                    colour=discord.Colour.yellow(),
                                    timestamp=datetime.datetime.now()))
        else:
            await interaction.response.send_message(
                embed=discord.Embed(title="Ахтунг! ❌",
                                    description=f"На сервере не был установлен автопостинг мемов",
                                    colour=discord.Colour.red(),
                                    timestamp=datetime.datetime.now()))


async def setup(bot):
    print("Setup MemeAutoPosting")
    await bot.add_cog(MemeAutoPosting(bot))