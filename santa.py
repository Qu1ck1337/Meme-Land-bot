from config import santaSettings
import discord
from discord.ext import commands
from discord.ext.commands import Cog



class SantaEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("Santa Ready")

    @Cog.listener("on_message")
    async def check_message(self, message):
        new_year_phrase = ["с новым годом", "с новым годом!", "с новым 2022", "с новым 2022!", "с новым",
                           "с новым!"]
        if " ".join(message.content.lower().split()[0:3]) in new_year_phrase:
            role = message.guild.get_role(santaSettings["santaRoleID"])
            if role not in message.author.roles:
                embed = discord.Embed(title="Дед Мороз 🎅",
                                      description=f"Ну и тебя, {message.author.mention}, с Новым Годом! 🤩"
                                                  f"\n\n❓ Вот и вопрос я задам тебе:"
                                                  f"\n**Какие цели ты поставил себе на новый 2022 год?**"
                                                  f"\n\n*💎А вот тебе от меня подарок, роль: **{role.name}**💎*",
                                      colour=0x42aaff
                                      )
                await message.author.add_roles(role)
            else:
                embed = discord.Embed(title="Дед Мороз 🎅",
                                      description=f"Ну и тебя, {message.author.mention}, с Новым Годом! 😉",
                                      colour=0x42aaff
                                      )
            embed.set_thumbnail(url=message.guild.icon_url)
            embed.set_footer(text="Meme Land bot | Новогодний создатель: EBOLA#1337")
            await message.reply(embed=embed)