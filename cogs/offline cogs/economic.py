import datetime

import discord
from discord.ext.commands import Cog
from pymongo import MongoClient
import pymongo
from discord.ext import commands, tasks
from config import economySettings
import random


class Economic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Provide the mongodb atlas url to connect python to mongodb using pymongo
        self.CONNECTION_STRING = "mongodb+srv://MLB1:xeB-QAG-44s-9c6@cluster0.maorj.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
        # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
        self.client = MongoClient(self.CONNECTION_STRING)

    @Cog.listener("on_ready")
    async def on_ready(self):
        self.bot.loop.create_task(self.check_server_members())
        self.leaderboard.start()

    @tasks.loop(minutes=1)
    async def leaderboard(self):
        schedule_time_minutes = ["0", "15", "30", "45"]
        try:
            if str(datetime.datetime.now().minute) in schedule_time_minutes:
                guild = self.bot.get_guild(economySettings["guild"])
                channel = guild.get_channel(economySettings["leaderBoardChannel"])

                await channel.purge(limit=1)

                dbname = self.client["server_economy"]
                collection_name = dbname["users_data"]
                result = collection_name.find().sort("balance", pymongo.DESCENDING).limit(10)
                embed = discord.Embed(title="Топ-10 лучших мемеров сервера Meme Land", color=0x42aaff)
                for num, rez in enumerate(result):
                    embed.add_field(name=f"**{ '🥇 ' if num == 0 else '🥈 ' if num == 1 else '🥉 ' if num == 2 else ''}{num + 1}. {guild.get_member(rez['id'])}**", value=f"**Memecoins:** {rez['balance']} <:memeland_coin:939265285767192626>", inline=False)
                embed.set_thumbnail(url=guild.icon_url)
                await channel.send(embed=embed)
                print(f"{datetime.datetime.now().strftime('%H:%M:%S')} | [INFO] Leaderboard was sent")
        except AttributeError:
            pass

    @Cog.listener("on_member_join")
    async def on_member_join(self, member):
        if member.guild == self.bot.get_guild(economySettings["guild"]):
            await self.create_user_data(member)

    @Cog.listener("on_member_remove")
    async def on_member_remove(self, member):
        if member.guild == self.bot.get_guild(economySettings["guild"]):
            await self.remove_user_data(member)

    async def check_server_members(self):
        dbname = self.client['server_economy']
        collection_name = dbname["users_data"]
        guild = self.bot.get_guild(economySettings["guild"])

        for member in guild.members:
            if not member.bot and collection_name.find_one({"id": member.id}) is None:
                await self.create_user_data(member)
        print(f"{datetime.datetime.now().strftime('%H:%M:%S')} | [INFO] Members checked")

    @commands.command()
    @commands.is_owner()
    async def send_data(self, ctx, member: discord.Member):
        if member is not None:
            await self.create_user_data(member)
        else:
            await self.create_user_data(ctx.author)

    async def create_user_data(self, member: discord.Member):
        # Create the database for our example (we will use the same database throughout the tutorial
        dbname = self.client['server_economy']
        collection_name = dbname["users_data"]
        if collection_name.find_one({"id": member.id}) is None:
            user_data = {
                "id": member.id,
                "balance": 0,
                "nextReward": datetime.datetime.now() + datetime.timedelta(seconds=economySettings["delayRewardSeconds"])
            }
            collection_name.insert_one(user_data)
            print(f"{datetime.datetime.now().strftime('%H:%M:%S')} | [INFO] Created and sent data of user {member.display_name}")
            return True
        else:
            print(f"{datetime.datetime.now().strftime('%H:%M:%S')} | [INFO] Sent data of user {member.display_name}")
            return True

    async def remove_user_data(self, member: discord.Member):
        # Create the database for our example (we will use the same database throughout the tutorial
        dbname = self.client['server_economy']
        collection_name = dbname["users_data"]
        collection_name.delete_one({'id': member.id})
        print(f"{datetime.datetime.now().strftime('%H:%M:%S')} | [INFO] Data of {member.display_name} was deleted")

    @commands.command()
    @commands.has_any_role(939801337196073030, 905484393919967252, 906632280376741939)
    #@commands.is_owner()
    #@commands.has_permissions(administrator=True)
    async def add_money(self, ctx, member: discord.Member, money: int):
        if ctx.guild == self.bot.get_guild(economySettings["guild"]):
            dbname = self.client['server_economy']
            collection_name = dbname["users_data"]
            result = collection_name.find_one({"id": member.id})
            if result is not None:
                var = result["balance"] + money
                collection_name.update_one(result, {"$set": {"balance": var}})
                embed = discord.Embed(title="Изменение баланса",
                                      description=f"Пользователю {member.mention} начислилось **{money}** <:memeland_coin:939265285767192626>: "
                                                  f"\n> Состояние баланса: **{result['balance']} <:memeland_coin:939265285767192626>** >> **{result['balance'] + money}** <:memeland_coin:939265285767192626>",
                                      color=economySettings["success_color"])
                embed.set_footer(
                    text=f"Запрошено {ctx.author} • {datetime.datetime.now().strftime('%m.%d.%Y %H:%M:%S')}", icon_url=ctx.author.avatar_url)
                await ctx.reply(embed=embed)
            else:
                status = await self.create_user_data(member=member)
                if status:
                    await self.set_money(ctx=ctx, member=member, money=money)
                else:
                    embed = discord.Embed(title="Ошибка", description="Искомый пользователь не найден.",
                                          color=economySettings["error_color"])
                    embed.set_footer(
                        text=f"Запрошено {ctx.author} • {datetime.datetime.now().strftime('%m.%d.%Y %H:%M:%S')}", icon_url=ctx.author.avatar_url)
                    await ctx.reply(embed=embed)

    @commands.command()
    @commands.has_any_role(939801337196073030, 905484393919967252, 906632280376741939)
    #@commands.is_owner()
    #@commands.has_permissions(administrator=True)
    async def set_money(self, ctx, member: discord.Member, money: int):
        if ctx.guild == self.bot.get_guild(economySettings["guild"]):
            dbname = self.client['server_economy']
            collection_name = dbname["users_data"]
            result = collection_name.find_one({"id": member.id})
            if result is not None:
                collection_name.update_one(result, {"$set": {"balance": money}})
                embed = discord.Embed(title="Изменение баланса",
                                      description=f"Баланс пользователя {member.mention} изменён: "
                                                  f"\n> Состояние баланса: **{result['balance']} <:memeland_coin:939265285767192626>** >> **{money}** <:memeland_coin:939265285767192626>",
                                      color=economySettings["success_color"])
                embed.set_footer(
                    text=f"Запрошено {ctx.author} • {datetime.datetime.now().strftime('%m.%d.%Y %H:%M:%S')}", icon_url=ctx.author.avatar_url)
                await ctx.reply(embed=embed)
            else:
                status = await self.create_user_data(member=member)
                if status:
                    await self.set_money(ctx=ctx, member=member, money=money)
                else:
                    embed = discord.Embed(title="Ошибка", description="Искомый пользователь не найден.",
                                          color=economySettings["error_color"])
                    embed.set_footer(
                        text=f"Запрошено {ctx.author} • {datetime.datetime.now().strftime('%m.%d.%Y %H:%M:%S')}", icon_url=ctx.author.avatar_url)
                    await ctx.reply(embed=embed)

    @commands.command(name="balance", aliases=["баланс"])
    async def balance(self, ctx, member: discord.Member = None):
        if ctx.guild == self.bot.get_guild(economySettings["guild"]):
            if member is None:
                member = ctx.author
            dbname = self.client['server_economy']
            collection_name = dbname["users_data"]
            result = collection_name.find_one({"id": member.id})
            if result is not None:
                embed = discord.Embed(title=f"Состояние баланса",
                                      description=f"Баланс {member.mention} на текущий момент: **{result['balance']}** <:memeland_coin:939265285767192626>",
                                      color=economySettings["success_color"])
                embed.set_footer(
                    text=f"Запрошено {ctx.author} • {datetime.datetime.now().strftime('%m.%d.%Y %H:%M:%S')}", icon_url=ctx.author.avatar_url)
                await ctx.reply(embed=embed)
            else:
                await self.create_user_data(member=member)
                await self.balance(ctx=ctx, member=member)

    @commands.command(name="send_money", aliases=["send", "перевести"])
    async def send_money(self, ctx, member: discord.Member, money: int):
        if money <= 0:
            embed = discord.Embed(title="Ошибка", description="Отправка невозможна",
                                  color=economySettings["error_color"])
            await ctx.reply(embed=embed)
            return
        if ctx.guild == self.bot.get_guild(economySettings["guild"]):
            dbname = self.client['server_economy']
            collection_name = dbname["users_data"]

            sender_result = collection_name.find_one({"id": ctx.author.id})

            if sender_result is None:
                await self.create_user_data(member=ctx.author)

            if sender_result["balance"] >= money:
                collection_name.update_one(sender_result, {"$set": {"balance": sender_result["balance"] - money}})

                giver_result = collection_name.find_one({"id": member.id})
                if giver_result is None:
                    await ctx.send(embed=discord.Embed(
                        title="Ошибка", description="Искомый получатель не найден.",
                        color=economySettings["error_color"]))
                    return
                collection_name.update_one(giver_result, {"$set": {"balance": giver_result["balance"] + money}})
                embed = discord.Embed(title="Успешный перевод",
                                      description=f"**{money}** <:memeland_coin:939265285767192626> успешно переведены пользователю {member.mention}",
                                      color=economySettings["success_color"])
                embed.set_footer(
                    text=f"Запрошено {ctx.author} • {datetime.datetime.now().strftime('%m.%d.%Y %H:%M:%S')}", icon_url=ctx.author.avatar_url)
                await ctx.reply(embed=embed)
            else:
                embed = discord.Embed(
                    title="Ошибка", description="Недостаточно средств", color=economySettings["error_color"])
                embed.set_footer(
                    text=f"Запрошено {ctx.author} • {datetime.datetime.now().strftime('%m.%d.%Y %H:%M:%S')}", icon_url=ctx.author.avatar_url)
                await ctx.reply(embed=embed)

    @Cog.listener("on_message")
    async def check_message(self, message):
        try:
            if message.guild == self.bot.get_guild(economySettings["guild"]) and message.channel.id not in economySettings["bannedChannelToGetMoney"]:
                dbname = self.client['server_economy']
                collection_name = dbname["users_data"]
                result = collection_name.find_one({"id": message.author.id})
                if result["nextReward"] < datetime.datetime.now():
                    randomMoney = random.randint(economySettings["randomMoneyForMessageMin"],
                                                 economySettings["randomMoneyForMessageMax"])
                    if message.channel.id in economySettings["doubleMoneyChannel"]:
                        res_bal = result['balance'] + randomMoney * 2
                    else:
                        res_bal = result['balance'] + randomMoney
                    collection_name.update_one({"id": message.author.id}, {"$set": {"balance": res_bal,
                                                                 "nextReward": datetime.datetime.now() + datetime.timedelta(
                                                                     seconds=economySettings[
                                                                         "delayRewardSeconds"])}})
                    print(f"{message.author.display_name} reached a reward."
                          f"\nAdded Money: {randomMoney}")
        except Exception as ex:
            pass

    @commands.command(name="shop", aliases=["магазин"])
    async def shop(self, ctx, page: int=1):
        if ctx.guild == self.bot.get_guild(economySettings["guild"]):
            dbname = self.client['server_economy_settings']
            collection_name = dbname["server_shop"]

            embed = discord.Embed(title=f"Магазин Жорика "
                                        f"\nСтраница {page}",
                                  description=f"Чтобы купить что-то в магазине Жорика, используйте команду `ml/buy <номер товара>` или `ml/купить <номер товара>`",
                                  color=economySettings["attention_color"])
            embed.set_thumbnail(url=ctx.guild.icon_url)
            embed.set_footer(
                text=f"Запрошено {ctx.author} • {datetime.datetime.now().strftime('%m.%d.%Y %H:%M:%S')}", icon_url=ctx.author.avatar_url)

            result = collection_name.find_one()
            is_page_exists = False
            for num, res in enumerate(result):
                if res != "_id" and num > 10 * (page - 1) and num <= 10 * page:
                    is_page_exists = True
                    role_id = result[res][1]
                    role = ctx.guild.get_role(role_id)
                    embed.add_field(name=f"Товар #{num}",
                                    value=f"{role.mention} | Стоимость: **{result[res][0]}** <:memeland_coin:939265285767192626>",
                                    inline=False)
            if is_page_exists is True:
                if page == 1:
                    embed.add_field(name=f"Страница {page}",
                                    value=f"Перейти на следующую страницу `ml/shop {page + 1}`",
                                    inline=False)
                else:
                    embed.add_field(name=f"Страница {page}",
                                    value=f"Перейти на следующую страницу `ml/shop {page + 1}`"
                                          f"\nПерейти на предыдущую страницу `ml/shop {page - 1}`",
                                    inline=False)
                await ctx.reply(embed=embed)
            else:
                await ctx.reply("Такой страницы магазина Жорика не существует :(")

    @commands.command(name="buy", aliases=["купить"])
    async def buy(self, ctx, nums: int):
        if ctx.guild == self.bot.get_guild(economySettings["guild"]):
            dbname = self.client['server_economy_settings']
            collection_name = dbname["server_shop"]

            result = collection_name.find_one()

            for num, res in enumerate(result):
                if res != "_id":
                    if num == nums:
                        role_id = result[res][1]
                        cost = result[res][0]

                        role = ctx.guild.get_role(role_id)

                        dbname_user = self.client['server_economy']
                        collection_name_user = dbname_user["users_data"]

                        user_result = collection_name_user.find_one({"id": ctx.author.id})

                        if role not in ctx.author.roles:
                            if user_result["balance"] >= cost:
                                new_balance = user_result["balance"] - cost
                                collection_name_user.update_one(user_result, {"$set": {"balance": new_balance}})
                                await ctx.author.add_roles(role)
                                embed = discord.Embed(title="Успешная покупка",
                                                      description=f"Покупка прошла успешно. Вы получили роль {role.mention}, купив за **{cost}** <:memeland_coin:939265285767192626>",
                                                      color=economySettings["success_color"])
                                embed.set_footer(
                                    text=f"Запрошено {ctx.author} • {datetime.datetime.now().strftime('%m.%d.%Y %H:%M:%S')}", icon_url=ctx.author.avatar_url)
                                await ctx.reply(embed=embed)
                            else:
                                embed = discord.Embed(title="Ошибка",
                                                      description=f"Недостаточно <:memeland_coin:939265285767192626>"
                                                                  f"\nЧтобы купить {role.mention} вам нужно ещё **{cost - user_result['balance']}** <:memeland_coin:939265285767192626>",
                                                      color=economySettings["error_color"])
                                embed.set_footer(
                                    text=f"Запрошено {ctx.author} • {datetime.datetime.now().strftime('%m.%d.%Y %H:%M:%S')}", icon_url=ctx.author.avatar_url)
                                await ctx.reply(embed=embed)
                                return
                        else:
                            embed = discord.Embed(title="Ошибка",
                                                  description=f"У вас уже есть {role.mention}",
                                                  color=economySettings["error_color"])
                            embed.set_footer(
                                text=f"Запрошено {ctx.author} • {datetime.datetime.now().strftime('%m.%d.%Y %H:%M:%S')}", icon_url=ctx.author.avatar_url)
                            await ctx.reply(embed=embed)
                            return


async def setup(bot):
    print("Setup Economic")
    await bot.add_cog(Economic(bot))