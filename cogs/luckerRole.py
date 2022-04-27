import datetime

import discord
from discord import app_commands
from discord.ext import commands
from pymongo import MongoClient

from config import luckyRoleSettings, luckyRoles, settings
import random


class NextSpinButton(discord.ui.View):
    def __init__(self, *, timeout=180, interaction: discord.Interaction, collection_name):
        self.interaction = interaction
        self.collection_name = collection_name
        super().__init__(timeout=timeout)

    @discord.ui.button(label="Крутить ещё", style=discord.ButtonStyle.green)
    async def next_button(self, interaction_m: discord.Interaction, button: discord.ui.Button):
        if interaction_m.user == self.interaction.user:
            randomNumber = random.randint(0, luckyRoleSettings["luckyRoleMax"])
            result = self.collection_name.find_one({"id": interaction_m.user.id})
            if result is None:
                return
            role = interaction_m.guild.get_role(luckyRoleSettings["artefacts_lucky_role"])
            if luckyRoles["lucky_role_min"] <= randomNumber <= luckyRoles["lucky_role_max"]:
                # role = interaction.guild.get_role(luckyRoles[randomNumber])
                # await interaction.user.add_roles(role)
                if luckyRoleSettings["artefacts_max_count"] == result["lucky_artefacts"] + 1:
                    self.collection_name.update_one(result,
                                                    {"$set": {"lucky_artefacts": result["lucky_artefacts"] + 1}})
                    await interaction_m.user.add_roles(role)
                    embed = discord.Embed(title=random.choice(luckyRoleSettings["luckyRoleWinPhraze"]),
                                          description=f"**Удача на твоей стороне!** 💎"
                                                      f"\nТы нашёл все артефакты и получил особую роль: **{role.name}**! Теперь ты можешь похвастаться ей перед всеми) 😎",
                                          colour=0xffd700
                                          )
                else:
                    if result["lucky_artefacts"] != luckyRoleSettings["artefacts_max_count"]:
                        self.collection_name.update_one(result,
                                                        {"$set": {"lucky_artefacts": result["lucky_artefacts"] + 1}})
                        embed = discord.Embed(title="Ого! Ты нашёл артефакт!",
                                              description=f"Найден артефакт для роли {role.name}, тебе ещё нужно собрать **{luckyRoleSettings['artefacts_max_count'] - result['lucky_artefacts'] - 1}**, чтобы получить эту роль!"
                                                          f"\n"
                                                          f"\n**💎 Всего артефактов у тебя 💎**"
                                                          f"\n\n```{role.name}: {result['lucky_artefacts'] + 1} / {luckyRoleSettings['artefacts_max_count']}```"
                                                          f"\n\nСпины не ограничены. Крути ещё, может тебе повезет) 😏",
                                              colour=0x33FF66
                                              )
                    else:
                        embed = discord.Embed(title="В следующий раз повезёт)",
                                              description=f"**💎 Всего артефактов у тебя 💎**"
                                                          f"\n\n```{role.name}: {result['lucky_artefacts']} / {luckyRoleSettings['artefacts_max_count']}```"
                                                          f"\n\nСпины не ограничены. Может быть тебе когда-нибудь повезёт) 😏",
                                              colour=0xff0000
                                              )
            else:
                embed = discord.Embed(title="В следующий раз повезёт)",
                                      description=f"**💎 Всего артефактов у тебя 💎**"
                                                  f"\n\n```{role.name}: {result['lucky_artefacts']} / {luckyRoleSettings['artefacts_max_count']}```"
                                                  f"\n\nСпины не ограничены. Может быть тебе когда-нибудь повезёт) 😏",
                                      colour=0xff0000
                                      )
            embed.set_thumbnail(url=interaction_m.guild.icon)
            embed.set_footer(
                text=f"Запрошено {interaction_m.user} • {datetime.datetime.now().strftime('%m.%d.%Y %H:%M:%S')}",
                icon_url=interaction_m.user.avatar)
            await interaction_m.response.edit_message(embed=embed, view=NextSpinButton(interaction=interaction_m, collection_name=self.collection_name))


class LuckerRole(commands.Cog):
    def __init__(self, bot):
        self.CONNECTION_STRING = "mongodb+srv://MLB1:xeB-QAG-44s-9c6@cluster0.maorj.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
        # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
        self.client = MongoClient(self.CONNECTION_STRING)
        self.bot = bot
        self.dbname = self.client['server_economy']
        self.collection_name = self.dbname["users_data"]

    @app_commands.command(name="spin", description="Крутить рулетку, чтобы получить новую роль на сервере")
    @app_commands.guilds(892493256129118260)
    async def spin(self, interaction: discord.Interaction):
        if interaction.guild_id != settings["guild"]:
            return
        if interaction.channel_id == luckyRoleSettings["luckyRoleChannelID"]:
            # await ctx.reply(random.choice(luckyRoleSettings["luckyRolePhraze"]))
            randomNumber = random.randint(0, luckyRoleSettings["luckyRoleMax"])
            result = self.collection_name.find_one({"id": interaction.user.id})
            if result is None:
                return
            role = interaction.guild.get_role(luckyRoleSettings["artefacts_lucky_role"])
            if luckyRoles["lucky_role_min"] <= randomNumber <= luckyRoles["lucky_role_max"]:
                #role = interaction.guild.get_role(luckyRoles[randomNumber])
                #await interaction.user.add_roles(role)
                if luckyRoleSettings["artefacts_max_count"] == result["lucky_artefacts"] + 1:
                    self.collection_name.update_one(result,
                                                    {"$set": {"lucky_artefacts": result["lucky_artefacts"] + 1}})
                    await interaction.user.add_roles(role)
                    embed = discord.Embed(title=random.choice(luckyRoleSettings["luckyRoleWinPhraze"]),
                                          description=f"**Удача на твоей стороне!** 💎"
                                                      f"\nТы нашёл все артефакты и получил особую роль: **{role.name}**! Теперь ты можешь похвастаться ей перед всеми) 😎",
                                          colour=0xffd700
                                          )
                else:
                    if result["lucky_artefacts"] != luckyRoleSettings["artefacts_max_count"]:
                        self.collection_name.update_one(result,
                                                        {"$set": {"lucky_artefacts": result["lucky_artefacts"] + 1}})
                        embed = discord.Embed(title="Ого! Ты нашёл артефакт!",
                                              description=f"Найден артефакт для роли {role.name}, тебе ещё нужно собрать **{luckyRoleSettings['artefacts_max_count'] - result['lucky_artefacts'] - 1}**, чтобы получить эту роль!"
                                                          f"\n"
                                                          f"\n**💎 Всего артефактов у тебя 💎**"
                                                          f"\n\n```{role.name}: {result['lucky_artefacts'] + 1} / {luckyRoleSettings['artefacts_max_count']}```"
                                                          f"\n\nСпины не ограничены. Крути ещё, может тебе повезет) 😏",
                                              colour=0x33FF66
                                              )
                    else:
                        embed = discord.Embed(title="В следующий раз повезёт)",
                                              description=f"**💎 Всего артефактов у тебя 💎**"
                                                          f"\n\n```{role.name}: {result['lucky_artefacts']} / {luckyRoleSettings['artefacts_max_count']}```"
                                                          f"\n\nСпины не ограничены. Может быть тебе когда-нибудь повезёт) 😏",
                                              colour=0xff0000
                                              )
            else:
                embed = discord.Embed(title="В следующий раз повезёт)",
                                      description=f"**💎 Всего артефактов у тебя 💎**"
                                                  f"\n\n```{role.name}: {result['lucky_artefacts']} / {luckyRoleSettings['artefacts_max_count']}```"
                                                  f"\n\nСпины не ограничены. Может быть тебе когда-нибудь повезёт) 😏",
                                      colour=0xff0000
                                      )
            embed.set_thumbnail(url=interaction.guild.icon)
            embed.set_footer(
                text=f"Запрошено {interaction.user} • {datetime.datetime.now().strftime('%m.%d.%Y %H:%M:%S')}",
                icon_url=interaction.user.avatar)
            await interaction.response.send_message(embed=embed, view=NextSpinButton(interaction=interaction, collection_name=self.collection_name))
        else:
            await interaction.response.send_message(f"Данная команда работает только на канале: <#{luckyRoleSettings['luckyRoleChannelID']}>")


async def setup(bot):
    print("Setup LuckerRole")
    await bot.add_cog(LuckerRole(bot))