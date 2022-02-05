import datetime
from discord.ext.commands import Cog
from pymongo import MongoClient
import pymongo
from discord.ext import commands, tasks
import discord
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
        await self.create_user_data(member)

    @Cog.listener("on_member_remove")
    async def on_member_remove(self, member):
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
    @commands.has_role(economySettings["moderatorAndAdministratorRolesID"])
    @commands.is_owner()
    @commands.has_permissions(administrator=True)
    async def add_money(self, ctx, member: discord.Member, money: int):
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
                text=f"Запрошено {ctx.author} 🞄 {datetime.datetime.now().strftime('%m.%d.%Y %H:%M:%S')}")
            await ctx.reply(embed=embed)
        else:
            status = await self.create_user_data(member=member)
            if status:
                await self.set_money(ctx=ctx, member=member, money=money)
            else:
                embed = discord.Embed(title="Ошибка", description="Искомый пользователь не найден.", color=economySettings["error_color"])
                embed.set_footer(
                    text=f"Запрошено {ctx.author} 🞄 {datetime.datetime.now().strftime('%m.%d.%Y %H:%M:%S')}")
                await ctx.reply(embed=embed)

    @commands.command()
    @commands.has_role(economySettings["moderatorAndAdministratorRolesID"])
    @commands.is_owner()
    @commands.has_permissions(administrator=True)
    async def set_money(self, ctx, member: discord.Member, money: int):
        dbname = self.client['server_economy']
        collection_name = dbname["users_data"]
        result = collection_name.find_one({"id": member.id})
        if result is not None:
            collection_name.update_one(result, {"$set": {"balance": money}})
            embed = discord.Embed(title="Изменение баланса",
                                  description=f"Баланс пользователя {member.mention} изменён: "
                                              f"\n> Состояние баланса: **{result['balance']} <:memeland_coin:939265285767192626>** >> **{money}** <:memeland_coin:939265285767192626>",
                                  color=economySettings["success_color"])
            embed.set_footer(text=f"Запрошено {ctx.author} 🞄 {datetime.datetime.now().strftime('%m.%d.%Y %H:%M:%S')}")
            await ctx.reply(embed=embed)
        else:
            status = await self.create_user_data(member=member)
            if status:
                await self.set_money(ctx=ctx, member=member, money=money)
            else:
                embed = discord.Embed(title="Ошибка", description="Искомый пользователь не найден.", color=economySettings["error_color"])
                embed.set_footer(
                    text=f"Запрошено {ctx.author} 🞄 {datetime.datetime.now().strftime('%m.%d.%Y %H:%M:%S')}")
                await ctx.reply(embed=embed)

    @commands.command(name="balance", aliases=["баланс"])
    async def balance(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author
        dbname = self.client['server_economy']
        collection_name = dbname["users_data"]
        result = collection_name.find_one({"id": member.id})
        if result is not None:
            embed = discord.Embed(title=f"Состояние баланса",
                                  description=f"Баланс {member.mention} на текущий момент: **{result['balance']}** <:memeland_coin:939265285767192626>",
                                  color=economySettings["success_color"])
            embed.set_footer(text=f"Запрошено {ctx.author} 🞄 {datetime.datetime.now().strftime('%m.%d.%Y %H:%M:%S')}")
            await ctx.reply(embed=embed)
        else:
            await self.create_user_data(member=member)
            await self.balance(ctx=ctx, member=member)

    @commands.command(name="send_money", aliases=["send", "перевести"])
    async def send_money(self, ctx, member: discord.Member, money: int):
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
                title="Ошибка", description="Искомый получатель не найден.", color=economySettings["error_color"]))
                return
            collection_name.update_one(giver_result, {"$set": {"balance": giver_result["balance"] + money}})
            embed = discord.Embed(title="Успешный перевод",
                                  description=f"**{money}** <:memeland_coin:939265285767192626> успешно переведены пользователю {member.mention}",
                                  color=economySettings["success_color"])
            embed.set_footer(
                text=f"Запрошено {ctx.author} 🞄 {datetime.datetime.now().strftime('%m.%d.%Y %H:%M:%S')}")
            await ctx.reply(embed=embed)
        else:
            embed = discord.Embed(
                title="Ошибка", description="Недостаточно средств", color=economySettings["error_color"])
            embed.set_footer(
                text=f"Запрошено {ctx.author} 🞄 {datetime.datetime.now().strftime('%m.%d.%Y %H:%M:%S')}")
            await ctx.reply(embed=embed)

    def dsi_check_user_like(self, message: discord.Message):
        # Лог Канал Лайков на сервере мониторинга
        if message.channel.id != 581415119645573121:
            return None
        # Сообщение от юзера/бота, не от вебхук лога
        if message.webhook_id == None:
            return None
        # Сообщение не содержит ембедов
        if not message.embeds:
            return None

        for embed in message.embeds:
            try:
                server = message.author.name
                server = server.split(" | ")
                server = server[-1].rsplit("#", maxsplit=1)[0]
                server_id = int(server)
                if server_id != economySettings["guild"]:
                    # Лайк для другого сервера
                    return None

                author = embed.author.name
                author = author.split(" | ")
                author = self.bot.get_user(int(author[-1]))

                if not author:
                    # Юзер не найден
                    return None
                # Возвращает лайкнувшего юзера
                return author
            except Exception as e:
                pass
        # Валидный ембед не найден
        return None

    @Cog.listener("on_message")
    async def check_message(self, message):
        user = self.dsi_check_user_like(message)
        if user:
            await message.reply(embed=discord.Embed(title="Награда", description=f"Вы получили вознаграждение за бамп сервера! Получены: {economySettings['monitoringReward']} <:memeland_coin:939265285767192626>",
                                                    color=economySettings["attention_color"]))
            dbname = self.client['server_economy']
            collection_name = dbname["users_data"]
            result = collection_name.find_one({"id": user.id})
            if result is not None:
                collection_name.update_one(result, {"$set": {"balance": economySettings["monitoringReward"]}})
            else:
                await self.create_user_data(message.author)
                dbname = self.client['server_economy']
                collection_name = dbname["users_data"]
                result = collection_name.find_one({"id": user.id})
                collection_name.update_one(result, {"$set": {"balance": economySettings["monitoringReward"]}})

        try:
            if economySettings["memeChannel"] is None or message.channel.id == economySettings["memeChannel"]:
                dbname = self.client['server_economy']
                collection_name = dbname["users_data"]
                result = collection_name.find_one({"id": message.author.id})
                if result["nextReward"] < datetime.datetime.now():
                    randomMoney = random.randint(economySettings["randomMoneyForMessageMin"],
                                                 economySettings["randomMoneyForMessageMax"])
                    res_bal = result['balance'] + randomMoney
                    collection_name.update_one(result, {"$set": {"balance": res_bal,
                                                                 "nextReward": datetime.datetime.now() + datetime.timedelta(
                                                                     seconds=economySettings["delayRewardSeconds"])}})
                    print(f"{message.author.display_name} reached a reward."
                          f"\nAdded Money: {randomMoney}")
        except Exception:
            pass