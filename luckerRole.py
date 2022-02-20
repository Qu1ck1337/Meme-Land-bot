import discord
from discord.ext import commands
from config import luckyRoleSettings, luckyRoles, settings
import random


class LuckerRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="spin", aliases=["спин", "крутить", "spins"])
    async def spin(self, ctx):
        if ctx.guild.id != settings["guild"]:
            return
        if ctx.channel.id == luckyRoleSettings["luckyRoleChannelID"]:
            # await ctx.reply(random.choice(luckyRoleSettings["luckyRolePhraze"]))
            randomNumber = random.randint(0, luckyRoleSettings["luckyRoleMax"])
            if randomNumber in luckyRoles.keys():
                role = ctx.guild.get_role(luckyRoles[randomNumber])
                await ctx.author.add_roles(role)
                if randomNumber != 1000:
                    embed = discord.Embed(title=random.choice(luckyRoleSettings["luckyRoleWinPhraze"]),
                                          description=f"**Выпало число:**"
                                                      f"\n\n✅ **`{randomNumber}`** ✅"
                                                      f"\n\n**Удача на твоей стороне!** 💎"
                                                      f"\nПолучай себе заветную роль: **{role.name}**! Теперь ты можешь перед всеми ей понтоваться) 😎",
                                          colour=0xffd700
                                          )
                else:
                    embed = discord.Embed(title="Что???",
                                          description=f"**Выпало число:**"
                                                      f"\n\n❓ **`1337`** ❓"
                                                      f"\n\n**Но как??? 😦**"
                                                      f"\nПолучай себе невозможную роль: **{role.name}**! Теперь ты можешь перед всеми ей понтоваться) 😎",
                                          colour=0xffd700
                                          )
            else:
                embed = discord.Embed(title="В следующий раз повезёт)",
                                      description=f"**Выпало число:**"
                                                  f"\n\n❌ **`{randomNumber}`** ❌"
                                                  f"\n\nСпины не ограничены. Может быть тебе когда-нибудь повезёт) 😏",
                                      colour=0xff0000
                                      )

            embed.set_thumbnail(url=ctx.guild.icon_url)
            embed.set_footer(text="Meme Land bot | Создатель EBOLA#1337")
            await ctx.reply(embed=embed)
        else:
            await ctx.reply(f"Данная команда работает только на канале: <#{luckyRoleSettings['luckyRoleChannelID']}>")