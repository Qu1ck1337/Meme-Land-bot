import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.ext.commands import Cog

from classes.DataBase import get_auto_meme_guilds
from classes.Logger import log_to_console
from classes.MemeObjects import RandomedMeme


memes_threads = {
    15: 1064136466659282954,
    30: 1064136522024104027,
    45: 1064136636889309215,
    60: 1064136697752850463
}


class MemeAutoPosting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.time_left = 0
        self.meme_threads = {}
        self.meme_threads_ids = []

    @Cog.listener("on_ready")
    async def on_ready(self):
        for time, channel_id in memes_threads.items():
            self.meme_threads[time] = self.bot.get_channel(channel_id)
            self.meme_threads_ids.append(channel_id)
        self.auto_post_meme.start()

    @tasks.loop(minutes=15)
    async def auto_post_meme(self):
        for time, channel in self.meme_threads.items():
            if self.time_left % time == 0:
                meme = RandomedMeme(self.bot, False)
                message = await channel.send(embed=meme.get_embed(title="Случайный мемчик!"))
                await message.publish()
        self.time_left += 15
        self.time_left %= 180

    @app_commands.command(description="Устанавливает автопостинг мемов раз в 30 минут")
    @app_commands.describe(time="Интервал времени между мемами")
    @app_commands.checks.has_permissions(administrator=True, manage_guild=True)
    @app_commands.choices(time=[
        app_commands.Choice(name="15 минут", value=15),
        app_commands.Choice(name="30 минут", value=30),
        app_commands.Choice(name="45 минут", value=45),
        app_commands.Choice(name="1 час", value=60)
    ])
    async def auto_meme(self, interaction: discord.Interaction, time: app_commands.Choice[int]):
        webhooks = await interaction.channel.webhooks()
        if self.is_webhook_source_channel_in_meme_threads(webhooks):
            web = await self.meme_threads[time.value].follow(destination=interaction.channel,
                                                       reason="Subscribed to meme autoposting thread")
            await web.edit(name=f"Meme Land | {time.name} - рандомный мем")
            embed = discord.Embed(title="Круто! 🎉",
                                  description=f"Автопостинг мемов успешно установлен на канале: {interaction.channel.mention}"
                                              f"\nВремя между мемами: `{time.value} минут`",
                                  colour=discord.Colour.green())
            embed.set_footer(text="🔕 Чтобы остановить автопостинг мемов, используйте /stop_auto_meme")
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title="Ошибка!",
                                  description=f"Этот канал уже подписан на рассылку мемов",
                                  colour=discord.Colour.red())
            await interaction.response.send_message(embed=embed)

    @app_commands.command(description="Останавливает автопостинг мемов на этом сервере")
    @app_commands.checks.has_permissions(administrator=True, manage_guild=True)
    @app_commands.describe(in_server="Остановить автопостинг на всём сервере?")
    async def stop_auto_meme(self, interaction: discord.Interaction, in_server: bool = False):
        ok = False
        if in_server:
            webhooks = await interaction.guild.webhooks()
            for webhook in webhooks:
                if webhook.source_channel.id in self.meme_threads_ids:
                    await webhook.delete()
                    ok = True
            if ok:
                embed = discord.Embed(title="Автопостинг на сервере приостановлен ⛔",
                                      description="Рассылка мемов на этом сервере прекращена",
                                      colour=discord.Colour.red())
                embed.set_footer(text="🚀 Чтобы возобновить рассылку, используйте /auto_meme")
                await interaction.response.send_message(embed=embed)
        else:
            webhooks = await interaction.channel.webhooks()
            for webhook in webhooks:
                if webhook.source_channel.id in self.meme_threads_ids:
                    await webhook.delete()
                    ok = True
                    break
            if ok:
                embed = discord.Embed(title="Автопостинг в канале приостановлен ⛔",
                                      description="Рассылка мемов в этом канале прекращена",
                                      colour=discord.Colour.red())
                embed.set_footer(text="🚀 Чтобы возобновить рассылку, используйте /auto_meme")
                await interaction.response.send_message(embed=embed)
        if ok is False:
            embed = discord.Embed(title="Автопостинг не был установлен на сервере",
                                  colour=discord.Colour.yellow())
            embed.set_footer(text="🚀 Чтобы начать рассылку, используйте /auto_meme")
            await interaction.response.send_message(embed=embed)

    def is_webhook_source_channel_in_meme_threads(self, webhook_list):
        for webhook in webhook_list:
            if webhook.source_channel.id in self.meme_threads_ids:
                return False
        return True


async def setup(bot):
    log_to_console(f"Loaded {__file__}")
    await bot.add_cog(MemeAutoPosting(bot))
