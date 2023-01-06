import datetime
import sys

import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.ext.commands import Cog

from classes.DataBase import get_auto_meme_guilds, get_auto_meme_guild, add_auto_meme_guild, update_autoposing_in_guild, \
    delete_guild_from_auto_meme_list
from classes.Logger import log_to_console
from classes.MemeObjects import RandomedMeme
from cogs.memes_watching import LikeMeme


class MemeAutoPosting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sorted_channels_in_guilds = {}
        self.time_left = 0

    @Cog.listener("on_ready")
    async def on_ready(self):
        unsorted_channels_in_guilds = {}
        auto_meme_guilds = get_auto_meme_guilds()
        for guild in auto_meme_guilds:
            if unsorted_channels_in_guilds.get(guild["posting_time"]) is None:
                unsorted_channels_in_guilds[guild["posting_time"]] = [guild["channel_id"]]
            else:
                unsorted_channels_in_guilds[guild["posting_time"]].append(guild["channel_id"])

        for channel in self.bot.get_all_channels():
            for key, channel_ids in unsorted_channels_in_guilds.items():
                if channel.id in channel_ids:
                    self.add_or_update_to_sorted_list(key, channel)
        self.auto_post_meme.start()

    @tasks.loop(minutes=15)
    async def auto_post_meme(self):
        log_to_console("Starting Auto Posting memes")
        channels = []
        for key, value in self.sorted_channels_in_guilds.items():
            if self.time_left % key == 0:
                channels.extend(value)
        self.time_left += 15

        for channel in channels:
            try:
                meme = RandomedMeme(self.bot, False)
                await channel.send(embed=meme.get_embed(title="❄ Случайный мемчик! ❄"), view=LikeMeme(
                    meme_id=meme.get_meme_id(),
                    bot=self.bot))
            except discord.Forbidden:
                guild = get_auto_meme_guild(channel.guild.id)
                delete_guild_from_auto_meme_list(guild)
                print("done!")
            except discord.HTTPException:
                pass
        log_to_console("Auto Posting meme done")

    @app_commands.command(description="Устанавливает автопостинг мемов раз в 30 минут")
    @app_commands.describe(channel="Канал, где нужно постить мемы (по умолчанию этот канал)")
    @app_commands.checks.has_permissions(administrator=True, manage_guild=True)
    @app_commands.choices(time=[
        app_commands.Choice(name="15 минут", value=15),
        app_commands.Choice(name="30 минут", value=30),
        app_commands.Choice(name="45 минут", value=45),
        app_commands.Choice(name="1 час", value=60)
    ])
    async def auto_meme(self, interaction: discord.Interaction, time: app_commands.Choice[int],
                        channel: discord.TextChannel = None):
        if channel is None:
            channel = interaction.channel

        result = get_auto_meme_guild(interaction.guild_id)
        if result is None:
            add_auto_meme_guild(interaction.guild_id, channel.id, time.value)
        else:
            update_autoposing_in_guild(result, channel.id, time.value)
        self.add_or_update_to_sorted_list(time.value, channel)

        embed = discord.Embed(title="Круто! 🎉",
                              description=f"Автопостинг мемов успешно установлен на канале: {channel.mention}"
                                          f"\nВремя между мемами: `{time.value} минут`",
                              colour=discord.Colour.green())
        embed.set_footer(text="🔕 Чтобы остановить автопостинг мемов используйте /stop_auto_meme")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(description="Останавливает автопостинг мемов на этом сервере")
    @app_commands.checks.has_permissions(administrator=True, manage_guild=True)
    async def stop_auto_meme(self, interaction: discord.Interaction):
        result = get_auto_meme_guild(interaction.guild_id)
        if result is not None:
            self.remove_from_sorted_list(result["posting_time"], result["channel_id"])
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

    @app_commands.command(description="Посмотреть информацио об автопостинге на данном сервере")
    @app_commands.checks.has_permissions(administrator=True, manage_guild=True)
    @app_commands.guilds(892493256129118260, 766386682047365190)
    async def auto_meme_info(self, interaction: discord.Interaction):
        auto_guild_data = get_auto_meme_guild(interaction.guild_id)
        if auto_guild_data is not None:
            await interaction.response.send_message(embed=discord.Embed(title=f"Информация об автопостинге на сервере {interaction.guild}",
                                                                        description=f"Канал для автопостинга: <#{auto_guild_data['channel_id']}>"
                                                                                    f"\nПромежуток времени между мемами: `{auto_guild_data['posting_time']} минут`",
                                                                        colour=discord.Colour.green()))
        else:
            await interaction.response.send_message(embed=discord.Embed(title=f"Информация об автопостинге на сервере {interaction.guild}",
                                                                        description=f"На сервере не установлен автопостинг мемов 😔"
                                                                                    f"\n"
                                                                                    f"\nВозможно вы не устанавливали автопостинг, отказались от рассылки, либо бот не смог скинуть мем в канале, что и привело к остановке рассылки",
                                                                        colour=discord.Colour.red()))

    def add_or_update_to_sorted_list(self, key, value):
        if self.sorted_channels_in_guilds.get(key) is None:
            self.sorted_channels_in_guilds[key] = [value]
        else:
            self.sorted_channels_in_guilds[key].append(value)
        print(self.sorted_channels_in_guilds)

    def remove_from_sorted_list(self, key, value: int):
        print(self.sorted_channels_in_guilds)
        if self.sorted_channels_in_guilds.get(key) is not None:
            list_of_channels = []
            for channel in self.sorted_channels_in_guilds[key]:
                if channel.id != value:
                    list_of_channels.append(channel)
            self.sorted_channels_in_guilds[key] = list_of_channels
        print(self.sorted_channels_in_guilds)


async def setup(bot):
    log_to_console(f"Loaded {__file__}")
    await bot.add_cog(MemeAutoPosting(bot))
