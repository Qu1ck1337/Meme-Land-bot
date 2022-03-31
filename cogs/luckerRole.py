import datetime

import discord
from discord import app_commands
from discord.ext import commands
from config import luckyRoleSettings, luckyRoles, settings
import random


class NextSpinButton(discord.ui.View):
    def __init__(self, *, timeout=180, interaction: discord.Interaction):
        self.interaction = interaction
        super().__init__(timeout=timeout)

    @discord.ui.button(label="Крутить ещё", style=discord.ButtonStyle.green)
    async def next_button(self, interaction_m: discord.Interaction, button: discord.ui.Button):
        if interaction_m.user == self.interaction.user:
            randomNumber = random.randint(0, luckyRoleSettings["luckyRoleMax"])
            if randomNumber in luckyRoles.keys():
                role = interaction_m.guild.get_role(luckyRoles[randomNumber])
                await interaction_m.user.add_roles(role)
                if randomNumber != 1000:
                    embed = discord.Embed(title=random.choice(luckyRoleSettings["luckyRoleWinPhraze"]),
                                          description=f"**Выпало число:**"
                                                      f"\n\n✅ **`{randomNumber}`** ✅"
                                                      f"\n\n**Удача на твоей стороне!** 💎"
                                                      f"\nПолучай себе заветную роль: **{role.name}**! Теперь ты можешь похвастаться ей перед всеми) 😎",
                                          colour=0xffd700
                                          )
                else:
                    embed = discord.Embed(title="Что???",
                                          description=f"**Выпало число:**"
                                                      f"\n\n❓ **`1337`** ❓"
                                                      f"\n\n**Но как??? 😦**"
                                                      f"\nПолучай себе невозможную роль: **{role.name}**! Теперь ты можешь похвастаться ей перед всеми) 😎",
                                          colour=0xffd700
                                          )
            else:
                embed = discord.Embed(title="В следующий раз повезёт)",
                                      description=f"**Выпало число:**"
                                                  f"\n\n❌ **`{randomNumber}`** ❌"
                                                  f"\n\nСпины не ограничены. Может быть тебе когда-нибудь повезёт) 😏",
                                      colour=0xff0000
                                      )
            embed.set_footer(
                text=f"Запрошено {interaction_m.user} • {datetime.datetime.now().strftime('%m.%d.%Y %H:%M:%S')}",
                icon_url=interaction_m.user.avatar)
            embed.set_thumbnail(url=interaction_m.guild.icon)
            await interaction_m.response.edit_message(embed=embed, view=self)


class LuckerRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="spin", description="Крутить рулетку, чтобы получить новую роль на сервере")
    @app_commands.guilds(892493256129118260)
    async def spin(self, interaction: discord.Interaction):
        if interaction.guild_id != settings["guild"]:
            return
        if interaction.channel_id == luckyRoleSettings["luckyRoleChannelID"]:
            # await ctx.reply(random.choice(luckyRoleSettings["luckyRolePhraze"]))
            randomNumber = random.randint(0, luckyRoleSettings["luckyRoleMax"])
            if randomNumber in luckyRoles.keys():
                role = interaction.guild.get_role(luckyRoles[randomNumber])
                await interaction.user.add_roles(role)
                if randomNumber != 1000:
                    embed = discord.Embed(title=random.choice(luckyRoleSettings["luckyRoleWinPhraze"]),
                                          description=f"**Выпало число:**"
                                                      f"\n\n✅ **`{randomNumber}`** ✅"
                                                      f"\n\n**Удача на твоей стороне!** 💎"
                                                      f"\nПолучай себе заветную роль: **{role.name}**! Теперь ты можешь похвастаться ей перед всеми) 😎",
                                          colour=0xffd700
                                          )
                else:
                    embed = discord.Embed(title="Что???",
                                          description=f"**Выпало число:**"
                                                      f"\n\n❓ **`1337`** ❓"
                                                      f"\n\n**Но как??? 😦**"
                                                      f"\nПолучай себе невозможную роль: **{role.name}**! Теперь ты можешь похвастаться ей перед всеми) 😎",
                                          colour=0xffd700
                                          )
            else:
                embed = discord.Embed(title="В следующий раз повезёт)",
                                      description=f"**Выпало число:**"
                                                  f"\n\n❌ **`{randomNumber}`** ❌"
                                                  f"\n\nСпины не ограничены. Может быть тебе когда-нибудь повезёт) 😏",
                                      colour=0xff0000
                                      )
            embed.set_thumbnail(url=interaction.guild.icon)
            embed.set_footer(
                text=f"Запрошено {interaction.user} • {datetime.datetime.now().strftime('%m.%d.%Y %H:%M:%S')}",
                icon_url=interaction.user.avatar)
            await interaction.response.send_message(embed=embed, view=NextSpinButton(interaction=interaction))
        else:
            await interaction.response.send_message(f"Данная команда работает только на канале: <#{luckyRoleSettings['luckyRoleChannelID']}>")


async def setup(bot):
    print("Setup LuckerRole")
    await bot.add_cog(LuckerRole(bot))