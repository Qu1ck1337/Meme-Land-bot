import datetime

import discord
from discord.ext import commands, tasks
from discord import app_commands
from discord.ext.commands import Cog
from glQiwiApi import QiwiP2PClient
from pymongo import MongoClient
from config import profile_settings

# Provide the mongodb atlas url to connect python to mongodb using pymongo
CONNECTION_STRING = \
    "mongodb+srv://dbBot:j5x-Pkq-Q8u-mW2@data.frvp6.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
# Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
CLIENT = MongoClient(CONNECTION_STRING)

DB_PROFILE = CLIENT[profile_settings["db_profile"]]
PROFILE_COLLECTION = DB_PROFILE[profile_settings["collection_profile"]]

DB_MEMES = CLIENT['bot_memes']
ACCEPTED_MEMES_COLLECTION = DB_MEMES["accepted_memes"]

DB_BILLS = CLIENT['bills']
NOT_APPROVED_BILLS_COLLECTION = DB_BILLS["not_approved_bills"]

PUBLIC_KEY = "48e7qUxn9T7RyYE1MVZswX1FRSbE6iyCj2gCRwwF3Dnh5XrasNTx3BGPiMsyXQFNKQhvukniQG8RTVhYm3iP5Np5KGAvSb9FvcCbcB" \
             "7mBUK6yJeLXtjhPA9B2jy2HPLsHXa9XoHmLK84brbRPtSBoBkuX6ek1UbUu63L36fif9RFaQ4kmm5Wchu2KePNv"
SECRET_KEY = "eyJ2ZXJzaW9uIjoiUDJQIiwiZGF0YSI6eyJwYXlpbl9tZXJjaGFudF9zaXRlX3VpZCI6IjZlOWljbC0wMCIsInVzZXJfaWQiOiI3OT" \
             "E1ODE1NzcwOSIsInNlY3JldCI6ImQ0NGM0MmY1MDQzMDQ1YjJmZjJjNGI0ZmI0YmEyZDdhOGZmNzRlM2NmY2IxNGIwNjRmZTcwNjQw" \
             "NDUyOGY2NjAifX0="
BILL = None


def Create_user_profile(author_id):
    result = ACCEPTED_MEMES_COLLECTION.find({"author": author_id})

    meme_count = 0
    likes = 0

    for meme in result:
        meme_count += 1
        likes += meme["likes"]

    PROFILE_COLLECTION.insert_one({
        "user_id": author_id,
        "level": 0,
        "exp": 0,
        "memes_count": meme_count,
        "memes_likes": likes,
        "premium_status": False,
        "meme_color": [66, 170, 255],
        "show_nickname": False,
        "show_tag": False,
        "show_url": False,
        "custom_url": ""
    })


class Payment(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener("on_ready")
    async def on_ready(self):
        pass
        self.premiumUsersChecker.start()
        self.billsChecker.start()

    @app_commands.guilds(892493256129118260)
    @app_commands.command()
    async def update_user(self, interaction):
        result = PROFILE_COLLECTION.find_one({"user_id": 702129698519384065})
        PROFILE_COLLECTION.update_one(result, {"$set": {
        "meme_color": [66, 170, 255],
        "show_nickname": False,
        "show_tag": False,
        "show_url": False,
        "custom_url": ""
        }})

    @tasks.loop(seconds=10)
    async def billsChecker(self):
        bills = NOT_APPROVED_BILLS_COLLECTION.find()
        for bill_result in bills:
            async with QiwiP2PClient(secret_p2p=SECRET_KEY) as p2p:
                bill = await p2p.get_bill_by_id(bill_id=bill_result["bill_id"])
                if bill.status.value == "REJECTED" or bill.status.value == "EXPIRED":
                    NOT_APPROVED_BILLS_COLLECTION.delete_one(bill_result)
                elif bill.status.value == "PAID":
                    user = PROFILE_COLLECTION.find_one({"user_id": bill_result["user_id"]})
                    if user is None:
                        Create_user_profile(bill_result["user_id"])
                        user = PROFILE_COLLECTION.find_one({"user_id": bill_result["user_id"]})
                    if not user["premium_status"]:
                        PROFILE_COLLECTION.update_one(user, {"$set": {"premium_status": True,
                                                                      "premium_status_end": datetime.datetime.now() + datetime.timedelta(days=30 * bill_result["months"])}})
                    else:
                        try:
                            PROFILE_COLLECTION.update_one(user, {"$set": {"premium_status_end": user["premium_status_end"] + datetime.timedelta(days=30 * bill_result["months"])}})
                        except KeyError:
                            pass
                    NOT_APPROVED_BILLS_COLLECTION.delete_one(bill_result)
                    user = PROFILE_COLLECTION.find_one({"user_id": bill_result["user_id"]})
                    await self.bot.get_user(bill_result["user_id"]).send(embed=discord.Embed(title="🚀 Оплата прошла успешно!",
                                                                                             description=f"**Благодарим за поддержку нашего бота. Мы очень рады, что вы выбрали именно нас!**"
                                                                                                         f"\n"
                                                                                                         f"\n**Подробнее про ваш meme+**"
                                                                                                         f"\nСрок поддержки: `{30 * bill_result['months']} дней`"
                                                                                                         f"\nДата окончания meme+: `{user['premium_status_end'].strftime('%d.%m.%Y')}`"
                                                                                                         f"\n"
                                                                                                         f"\n**Преимущества meme+**"
                                                                                                         f"\n🔹 Роль спонсора на официальном сервере бота"
                                                                                                         f"\n└ Специальный чат для спонсоров"
                                                                                                         f"\n└ Приоритетная поддержка"
                                                                                                         f"\n"
                                                                                                         f"\n🔸 **2x** опыт"
                                                                                                         f"\n🔸 Сменяемость цвета у ваших мемов"
                                                                                                         f"\n🔸 Возможность показать свой никнейм в меме"
                                                                                                         f"\n🔸 Возможность добавить к никнейму тег (люди смогут добавить вас в друзья)"
                                                                                                         f"\n🔸 Встраивание URL ссылок в мемы",
                                                                                             colour=discord.Colour.gold()
                                                                                             ))

    @app_commands.command()
    async def meme_plus(self, interaction: discord.Interaction):
        await interaction.response.send_message(embed=discord.Embed(
                                                        title="Спасибо за вашу заинтересованность!",
                                                        description="\nСообщение о поддержке вы получили в лс)",
                                                        colour=discord.Colour.gold()))
        await interaction.user.send(embed=discord.Embed(title="Хотите поддержать бота?",
                                                        description="\nПодробности про meme+ `/premium_info`"
                                                                    "\n"
                                                                    "\nВыберите способ оплаты в окне выбора ниже 😀",
                                                        colour=discord.Colour.gold()),
                                    view=PaymentSelect())

    @tasks.loop(seconds=10)
    async def premiumUsersChecker(self):
        premium_users = PROFILE_COLLECTION.find({"premium_status": True})
        for premium_user in premium_users:
            try:
                if premium_user["premium_status_end"] < datetime.datetime.now():
                    print(premium_user)
                    PROFILE_COLLECTION.update_one(premium_user, {"$set": {"premium_status": False, "premium_status_end": None}})
                    await self.bot.get_user(premium_user["user_id"]).send(embed=discord.Embed(
                        title="Ваш meme+ закончился",
                        description="\n:(",
                        colour=discord.Colour.red()))
            except KeyError:
                pass

    @app_commands.guilds(892493256129118260)
    @app_commands.command()
    async def premium_info(self, interaction: discord.Interaction):
        embed = discord.Embed(title="⭐ Преимущества meme+ ⭐",
                              description=f"🔹 **Роль спонсора на официальном сервере бота**"
                                          f"\n└ **Специальный чат для спонсоров**"
                                          f"\n└ **Приоритетная поддержка**"
                                          f"\n"
                                          f"\n🔸 **2x** опыт"
                                          f"\n🔸 **Сменяемость цвета у ваших мемов**"
                                          f"\n🔸 **Возможность показать свой никнейм в меме**"
                                          f"\n🔸 **Возможность добавить к никнейму тег (люди смогут добавить вас в друзья)**"
                                          f"\n🔸 **Встраивание URL ссылок в мемы**"
                                          f"\n"
                                          f"\n*А ещё...*"
                                          f"\n**Вы поддержите создателя бота, и он будет чаще пилить обновы для бота ^-^**"
                                          f"\n"
                                          f"\n💰 **Захотелось опробовать?** 💰"
                                          f"\n**Команда** 👉 `/meme_plus`",
                              colour=discord.Colour.gold())
        embed.set_author(name=f"▹ То что нужно 👍",
                         icon_url=interaction.user.avatar)
        embed.set_footer(text=f'🚀 Вжуууууух!')
        embed.set_thumbnail(url=interaction.guild.icon)
        await interaction.response.send_message(embed=embed)


class PaymentSelect(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.select(placeholder="Выберите способ оплаты", options=[discord.SelectOption(label="QIWI 1 месяц - 30 руб.",
                                                                                           value="1:1",
                                                                                           emoji=discord.PartialEmoji.from_str("<:qiwi:987444061969469440>")),
                                                                      discord.SelectOption(label="QIWI 3 месяца - 70 руб.",
                                                                                           value="3:1",
                                                                                           emoji=discord.PartialEmoji.from_str("<:qiwi:987444061969469440>"))])
    async def selectPayment(self, interaction: discord.Interaction, selector: discord.ui.Select):
        value = selector.values[0].split(":")
        months = int(value[0])
        rubles = int(value[1])
        async with QiwiP2PClient(secret_p2p=SECRET_KEY) as p2p:
            bill = await p2p.create_p2p_bill(amount=rubles,
                                             expire_at=datetime.datetime.now() + datetime.timedelta(hours=1),
                                             comment=f"discord user id: {interaction.user.id}",
                                             pay_source_filter=["qw", "card", "mobile"])
            NOT_APPROVED_BILLS_COLLECTION.insert_one({"bill_id": bill.id, "months": months, "user_id": interaction.user.id})
            await interaction.response.send_message(embed=discord.Embed(title="🧾 Ваш счёт создан",
                                                                        description=f"Обратите внимание, счёт действителен **1** час"
                                                                                    f"\n"
                                                                                    f"\n{bill.pay_url}",
                                                                        colour=discord.Colour.gold()))


async def setup(bot):
    print("Setup Payment")
    await bot.add_cog(Payment(bot))