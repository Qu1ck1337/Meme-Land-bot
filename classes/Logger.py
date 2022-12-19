import datetime

import discord

from classes import StaticParameters


async def log_message(message: str):
    await StaticParameters.log_channel.send(embed=discord.Embed(description=message, timestamp=datetime.datetime.now()))


def success_to_console(message: str):
    print(f'\033[32m{datetime.datetime.now().strftime("%H:%M:%S")} [SUCCESS] | {message}')


def log_to_console(message: str):
    print(f'\033[0m{datetime.datetime.now().strftime("%H:%M:%S")} [INFO] | {message}')


def error_to_console(message):
    print(f'\033[31m{datetime.datetime.now().strftime("%H:%M:%S")} [ERROR] | {message}')


def warn_to_console(message):
    print(f'\033[33m{datetime.datetime.now().strftime("%H:%M:%S")} [WARN] | {message}')
