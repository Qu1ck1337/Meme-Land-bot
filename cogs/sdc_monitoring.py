import sdc_api_py
from discord.ext import commands

from classes.Logger import log_to_console
from config import settings


class BotsSDC(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        # Аргумент fork_name опциональный. Укажите название используемого форка discord.py если таковой используется.
        # Название нужно указыать то, с помощью которого вы импортировали форк в свой проект.
        bots = sdc_api_py.Bots(self.bot, settings["SDC_monitoring_token"], "discord.py",
                               True)  # Аргумент logging опциональный. По умолчанию True.
        bots.create_loop()  # Как аргумент можно использовать время в минутах. Раз в это количество минут будет отправляться статистика.
        # По умолчанию 60 минут. Минимальный порог 30 минут.


async def setup(bot):
    log_to_console(f"Loaded {__file__}")
    await bot.add_cog(BotsSDC(bot))