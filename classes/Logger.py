import datetime

import discord

from classes import StaticParameters


async def log_message(message: str):
    await StaticParameters.log_channel.send(embed=discord.Embed(description=message, timestamp=datetime.datetime.now()))
