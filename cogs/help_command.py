import discord
from discord import app_commands, ui
from discord.ext import commands

from classes.Logger import log_to_console


class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Помощь по командам бота")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🔨 Помощь по командам бота", description=f"Выберите определённую категорию, чтобы узнать подробнее о командах бота.",
                              color=0x42aaff)
        embed.add_field(name="🛎️ Доступные категории 🛎️", value="```👥 Пользовательские команды \n/meme /last_meme /popular_meme /send_meme /profile /leaderboard /color_memes```"
                                                          "\n```👮 Административные команды \n/auto_meme /stop_meme```")
        embed.set_footer(text=f"\"Спасибо за выбор нашего бота!\" 💗 - EBOLA (создатель бота)")
        await interaction.response.send_message(embed=embed, view=HelpSliders(self.bot))

    @app_commands.command(name="support", description="Помощь по командам бота")
    async def support(self, interaction: discord.Interaction):
        await interaction.response.send_message(embed=discord.Embed(title="🔨 Поддержка",
                                                                    description="Возникли трудности с ботом, поймали баг, либо хотите удалить мем? "
                                                                                "Переходите на наш сервер поддержки, кнопка внизу) 😉",
                                                                    colour=discord.Colour.green()),
                                                ephemeral=True,
                                                view=SupportView())


class HelpSliders(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.select(placeholder="Выберите категорию", options=[discord.SelectOption(label="Пользовательские команды",
                                                                                       emoji="👥",
                                                                                       value="0"),
                                                                  discord.SelectOption(label="Административные команды",
                                                                                       emoji="👮",
                                                                                       value="1")
                                                                  ])
    async def help_selector(self, interaction: discord.Interaction, selector: ui.Select):
        if selector.values[0] == "0":
            embed = discord.Embed(title="👥 Пользовательские команды",
                                                                  description=f"✨ Данные команды могут использовать все пользователи бота"
                                                                              f"\n```/upload_meme <картинка> - отправить мем на модерацию```"
                                                                              f"\n```/meme - показывает случайный мем```"
                                                                              f"\n```/meme <id мема> - показывает мем с нужным id```"
                                                                              f"\n```/last_meme - показывает последний залитый мем```"
                                                                              f"\n```/top_meme - показывает самый лучший мем бота```"
                                                                              f"\n```/profile - показывает ваш мемный профиль```"
                                                                              f"\n```/leaderboard - показывает таблицу лидеров```"
                                                                              f"\n```/memes_color - изменить цвет своих мемов```",
                                                                  colour=discord.Colour.blue())
            embed.set_thumbnail(url=self.bot.application.icon)
            await interaction.response.edit_message(embed=embed)
        elif selector.values[0] == "1":
            embed = discord.Embed(title="👮 Административные команды",
                                                                  description=f"❗ Данными командами могут пользоваться только участники сервера с правами ***Администратора***"
                                                                              f"```\n/auto_meme <канал> - устанавливает канал для постинга мемов раз в 30 минут```"
                                                                              f"```\n/stop_auto_meme - приостанавливает авто постинг мемов на сервере```",
                                                                  colour=discord.Colour.blue()
                                                                  )
            embed.set_thumbnail(url=self.bot.application.icon)
            await interaction.response.edit_message(embed=embed)


class SupportView(discord.ui.View):
    @ui.button(label="Получить ссылку", emoji="🔗", style=discord.ButtonStyle.blurple)
    async def invite_button(self, interaction, button):
        await interaction.user.send("Ссылка на сервер поддержки:\nhttps://discord.gg/meme-land-server-podderzhki-bota-892493256129118260")
        await interaction.response.send_message("Ссылка на сервер отправлена в личные сообщения", ephemeral=True)


async def setup(bot):
    log_to_console(f"Loaded {__file__}")
    await bot.add_cog(HelpCommand(bot))