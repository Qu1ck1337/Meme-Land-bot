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

            is_win_existed = False
            embed = discord.Embed()
            for role, luck_list in luckyRoles.items():
                if randomNumber == luck_list[0] and is_win_existed is False:
                    is_win_existed = True
                    role = interaction_m.guild.get_role(luck_list[1])
                    if luck_list[3] == result[luck_list[2]] + 1:
                        self.collection_name.update_one(result,
                                                        {"$set": {luck_list[2]: result[luck_list[2]] + 1}})
                        await interaction_m.user.add_roles(role)
                        embed = discord.Embed(title=random.choice(luckyRoleSettings["luckyRoleWinPhraze"]),
                                              description=f"**Удача на твоей стороне!** 💎"
                                                          f"\nТы нашёл все артефакты и получил особую роль: **{role.name}**! Теперь ты можешь похвастаться ей перед всеми) 😎",
                                              colour=0xffd700
                                              )
                    else:
                        if luck_list[3] != result[luck_list[2]]:
                            self.collection_name.update_one(result,
                                                            {"$set": {luck_list[2]: result[luck_list[2]] + 1}})
                            embed = discord.Embed(title="Ого! Ты нашёл артефакт!",
                                                  description=f"Найден артефакт для роли **{role.name}**, тебе ещё нужно собрать **{luck_list[3] - result[luck_list[2]] - 1}**, чтобы получить эту роль!"
                                                              f"\n"
                                                              f"\n**💎 Всего артефактов у тебя 💎**"
                                                              f"\n\n```{Create_list_of_artefacts(result=result, guild=interaction_m.guild, what_to_add_plus=luck_list[2])}```"
                                                              f"\n\nСпины не ограничены. Крути ещё, может тебе повезет) 😏",
                                                  colour=0x33FF66
                                                  )
                        else:
                            embed = discord.Embed(title="В следующий раз повезёт)",
                                                  description=f"**💎 Всего артефактов у тебя 💎**"
                                                              f"\n\n```{Create_list_of_artefacts(result=result, guild=interaction_m.guild)}```"
                                                              f"\n\nСпины не ограничены. Может быть тебе когда-нибудь повезёт) 😏",
                                                  colour=0xff0000
                                                  )
            if is_win_existed is False:
                embed = discord.Embed(title="В следующий раз повезёт)",
                                      description=f"**💎 Всего артефактов у тебя 💎**"
                                                  f"\n\n```{Create_list_of_artefacts(result=result, guild=interaction_m.guild)}```"
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

            is_win_existed = False
            embed = discord.Embed()
            for role, luck_list in luckyRoles.items():
                if randomNumber == luck_list[0] and is_win_existed is False:
                    is_win_existed = True
                    role = interaction.guild.get_role(luck_list[1])
                    if luck_list[3] == result[luck_list[2]] + 1:
                        self.collection_name.update_one(result,
                                                        {"$set": {luck_list[2]: result[luck_list[2]] + 1}})
                        await interaction.user.add_roles(role)
                        embed = discord.Embed(title=random.choice(luckyRoleSettings["luckyRoleWinPhraze"]),
                                              description=f"**Удача на твоей стороне!** 💎"
                                                          f"\nТы нашёл все артефакты и получил особую роль: **{role.name}**! Теперь ты можешь похвастаться ей перед всеми) 😎",
                                              colour=0xffd700
                                              )
                    else:
                        if luck_list[3] != result[luck_list[2]]:
                            self.collection_name.update_one(result,
                                                            {"$set": {luck_list[2]: result[luck_list[2]] + 1}})
                            embed = discord.Embed(title="Ого! Ты нашёл артефакт!",
                                                  description=f"Найден артефакт для роли **{role.name}**, тебе ещё нужно собрать **{luck_list[3] - result[luck_list[2]] - 1}**, чтобы получить эту роль!"
                                                              f"\n"
                                                              f"\n**💎 Всего артефактов у тебя 💎**"
                                                              f"\n\n```{Create_list_of_artefacts(result=result, guild=interaction.guild, what_to_add_plus=luck_list[2])}```"
                                                              f"\n\nСпины не ограничены. Крути ещё, может тебе повезет) 😏",
                                                  colour=0x33FF66
                                                  )
                        else:
                            embed = discord.Embed(title="В следующий раз повезёт)",
                                                  description=f"**💎 Всего артефактов у тебя 💎**"
                                                              f"\n\n```{Create_list_of_artefacts(result=result, guild=interaction.guild)}```"
                                                              f"\n\nСпины не ограничены. Может быть тебе когда-нибудь повезёт) 😏",
                                                  colour=0xff0000
                                                  )
            if is_win_existed is False:
                embed = discord.Embed(title="В следующий раз повезёт)",
                                      description=f"**💎 Всего артефактов у тебя 💎**"
                                                  f"\n\n```{Create_list_of_artefacts(result=result, guild=interaction.guild)}```"
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

    @app_commands.command()
    @app_commands.guilds(892493256129118260)
    async def update_user_data(self, interaction: discord.Interaction):
        dbname = self.client['server_economy']
        collection_name = dbname["users_data"]
        result = collection_name.find()
        for user in result:
            print(user)
            collection_name.update_one(user, {"$set": {"konch_artefacts": 0, "shnip_shnap_artefacts": 0, "ebolas_son_artefacts": 0, "el_primo_artefacts": 0}})
        print("Done!")


def Create_list_of_artefacts(result, guild, what_to_add_plus: str=None):
    artefacts_list = []
    for list_of_des in luckyRoles.values():
        role = guild.get_role(list_of_des[1])
        if list_of_des[2] == what_to_add_plus:
            artefacts_list.append(f"{role.name}: {result[list_of_des[2]] + 1} / {list_of_des[3]}")
        else:
            artefacts_list.append(f"{role.name}: {result[list_of_des[2]]} / {list_of_des[3]}")
    return "\n".join(artefacts_list)


async def setup(bot):
    print("Setup LuckerRole")
    await bot.add_cog(LuckerRole(bot))