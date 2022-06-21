import datetime

import discord
from discord.ext import commands, tasks
from discord import app_commands
from discord.ext.commands import Cog
from glQiwiApi import QiwiP2PClient
from pymongo import MongoClient
from config import profile_settings,settings

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


def Check_if_it_is_me(interaction: discord.Interaction) -> bool:
    return interaction.user.id == 443337837455212545


class Payment(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.official_guild = discord.Guild
        self.premium_role = discord.Role

    @Cog.listener("on_ready")
    async def on_ready(self):
        self.official_guild = self.bot.get_guild(settings["guild"])
        self.premium_role = self.official_guild.get_role(987616951415210005)
        self.premiumUsersChecker.start()
        self.billsChecker.start()

    @app_commands.guilds(892493256129118260)
    @app_commands.check(Check_if_it_is_me)
    @app_commands.command()
    async def update_all_users(self, interaction):
        result_all = PROFILE_COLLECTION.find()
        for result in result_all:
            PROFILE_COLLECTION.update_one(result, {"$set": {
            "meme_color": [66, 170, 255],
            "show_nickname": False,
            "show_tag": False,
            "show_url": False,
            "custom_url": ""
            }})
        print("done!")

    @tasks.loop(minutes=1)
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
                                                                                                         f"\nДата окончания **meme+**: `{user['premium_status_end'].strftime('%d.%m.%Y')}`"
                                                                                                         f"\n"
                                                                                                         f"\n**Преимущества meme+**"
                                                                                                         f"\n🔹 Роль спонсора на официальном сервере бота (ссылка в профиле бота)"
                                                                                                         f"\n└ Специальный чат для спонсоров"
                                                                                                         f"\n└ Приоритетная поддержка"
                                                                                                         f"\n"
                                                                                                         f"\n🔸 **2x** опыт"
                                                                                                         f"\n🔸 Сменяемость цвета у ваших мемов"
                                                                                                         f"\n🔸 Возможность показать свой никнейм в меме"
                                                                                                         f"\n🔸 Возможность добавить к никнейму тег (люди смогут добавить вас в друзья)"
                                                                                                         f"\n🔸 Встраивание URL ссылок в мемы"
                                                                                                         f"\n🔸 Подсказки ниже картинки мема убираются"
                                                                                                         f"\n"
                                                                                                         f"\n⭐ Посмотреть ваши премиум настроки: `/plus_settings`",
                                                                                             colour=discord.Colour.gold()
                                                                                             ))

    @app_commands.command(description="Поддержать бота")
    async def meme_plus(self, interaction: discord.Interaction):
        await interaction.user.send(embed=discord.Embed(title="Хотите поддержать бота?",
                                                        description="\nПодробности про meme+: `/premium_info`"
                                                                    "\n"
                                                                    "\nВыберите способ оплаты в окне выбора ниже 😀",
                                                        colour=discord.Colour.gold()),
                                    view=PaymentSelect())
        await interaction.response.send_message(embed=discord.Embed(
                                                        title="Спасибо за вашу заинтересованность!",
                                                        description="\nСпособы поддержки вы получили в лс)",
                                                        colour=discord.Colour.gold()))

    @tasks.loop(hours=1)
    async def premiumUsersChecker(self):
        premium_users = PROFILE_COLLECTION.find({"premium_status": True})
        for premium_user in premium_users:
            try:
                member = self.bot.get_guild(settings["guild"]).get_member(premium_user["user_id"])
                if member is not None and member.get_role(self.premium_role.id) is None:
                    await member.add_roles(self.premium_role)

                if premium_user["premium_status_end"] < datetime.datetime.now():
                    member = self.bot.get_guild(settings["guild"]).get_member(premium_user["user_id"])
                    if member is not None and member.get_role(self.premium_role.id):
                        await member.remove_roles(self.premium_role)

                    PROFILE_COLLECTION.update_one(premium_user, {"$set": {"premium_status": False, "premium_status_end": None}})
                    await self.bot.get_user(premium_user["user_id"]).send(embed=discord.Embed(
                        title="Ваш meme+ закончился",
                        description="\nВаш meme+ закончился, чтобы продолжить meme+, используйте: `/meme_plus`"
                                    "\nБлагодарим за вашу поддержку нашего бота)",
                        colour=discord.Colour.red()))
            except KeyError:
                pass

    @app_commands.command(description="Узнать преимущества поддержки бота")
    async def plus_info(self, interaction: discord.Interaction):
        embed = discord.Embed(title="⭐ Преимущества meme+ ⭐",
                              description=f"🔹 **Роль спонсора на официальном сервере бота** (ссылка в профиле бота)"
                                          f"\n└ **Специальный чат для спонсоров**"
                                          f"\n└ **Приоритетная поддержка**"
                                          f"\n"
                                          f"\n🔸 **2x** опыт"
                                          f"\n🔸 **Сменяемость цвета у ваших мемов**"
                                          f"\n🔸 **Возможность показать свой никнейм в меме**"
                                          f"\n🔸 **Возможность добавить к никнейму тег (люди смогут добавить вас в друзья)**"
                                          f"\n🔸 **Встраивание URL ссылок в мемы**"
                                          f"\n🔸 **Подсказки ниже картинки мема убираются**"
                                          f"\n"
                                          f"\n[скоро] **Интервал времени между авто-мемами**"
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

    @app_commands.command()
    @app_commands.check(Check_if_it_is_me)
    @app_commands.guilds(892493256129118260)
    async def add_plus(self, interaction: discord.Interaction, user_id: str, time_in_days: int, is_permanent: bool=False):
        user_id = int(user_id)
        user = self.bot.get_user(int(user_id))
        if user is not None:
            result = PROFILE_COLLECTION.find_one({"user_id": user_id})
            if result is None:
                Create_user_profile(user_id)
                result = PROFILE_COLLECTION.find_one({"user_id": user_id})
            if is_permanent is False:
                if result["premium_status"]:
                    end_time = user['premium_status_end'] + datetime.timedelta(days=time_in_days)
                    PROFILE_COLLECTION.update_one(result, {"$set": {"premium_status": True, "premium_status_end": end_time}})
                else:
                    end_time = datetime.datetime.now() + datetime.timedelta(days=time_in_days)
                    PROFILE_COLLECTION.update_one(result, {"$set": {"premium_status": True, "premium_status_end": end_time}})
                await interaction.response.send_message(embed=discord.Embed(title="Пользователю был добавлен meme+",
                                                                            description=f"Пользователь **{user.name}** получил meme+"
                                                                                        f"\nДата окончания поддержки: `{end_time.strftime('%d.%m.%Y')}`",
                                                                            colour=discord.Colour.green()))
                await user.send(embed=discord.Embed(title="Поздравляем! Вы получили meme+!",
                                                    description=f"\nВы получили **{time_in_days}** дня(-ей) meme+"
                                                                f"\nДата окончания поддержки: `{end_time.strftime('%d.%m.%Y')}`"
                                                                f"\nОзнакомиться со всеми плюшками meme+: `/plus_info`",
                                                    colour=discord.Colour.gold()))
            else:
                try:
                    PROFILE_COLLECTION.update_one(result,
                                                  {"$set": {"premium_status": True}, "$unset": {"premium_status_end": result["premium_status_end"]}})
                except KeyError:
                    PROFILE_COLLECTION.update_one(result,
                                                  {"$set": {"premium_status": True}})
                await interaction.response.send_message(embed=discord.Embed(title="Пользователю был добавлен meme+",
                                                                            description=f"Пользователь **{user.name}** получил meme+"
                                                                                        f"\nДата окончания поддержки: `навсегда`",
                                                                            colour=discord.Colour.green()))
                await user.send(embed=discord.Embed(title="Поздравляем! Вы получили meme+!",
                                                    description=f"\nВы получили **навсегда** meme+"
                                                                f"\nОзнакомиться со всеми плюшками meme+: `/plus_info`",
                                                    colour=discord.Colour.gold()))
        else:
            await interaction.response.send_message(embed=discord.Embed(title="Пользователь не найден",
                                                                        description=f"Пользователь под id **{user_id}** не найден",
                                                                        colour=discord.Colour.red()))

    @app_commands.command()
    @app_commands.check(Check_if_it_is_me)
    @app_commands.guilds(892493256129118260)
    async def remove_plus(self, interaction: discord.Interaction, user_id: str, time_in_days: int=0, is_permanent: bool=False):
        user_id = int(user_id)
        user = self.bot.get_user(int(user_id))
        if user is not None:
            result = PROFILE_COLLECTION.find_one({"user_id": user_id})
            if result is None:
                await interaction.response.send_message(embed=discord.Embed(title="Пользователь не зарегистрирован в системе",
                                                                            description=f"Пользователь под id **{user_id}** не зарегистрирован в системе",
                                                                            colour=discord.Colour.red()))
                return
            elif result["premium_status"] and is_permanent:
                try:
                    PROFILE_COLLECTION.update_one(result,
                                                  {"$set": {"premium_status": False}, "$unset": {"premium_status_end": result["premium_status_end"]}})
                    await interaction.response.send_message(embed=discord.Embed(title="У пользователя был снят meme+",
                                                                                description=f"У пользователя **{user.name}** был снят meme+",
                                                                                colour=discord.Colour.orange()))
                    await user.send(embed=discord.Embed(title="Плохие новости. У вас был снят meme+",
                                                        description=f"\nАдминистрация решила у вас полностью снять meme+",
                                                        colour=discord.Colour.red()))
                except KeyError:
                    PROFILE_COLLECTION.update_one(result,
                                                  {"$set": {"premium_status": False}})
                    await interaction.response.send_message(embed=discord.Embed(title="У пользователя был снят meme+",
                                                                                description=f"У пользователя **{user.name}** был снят meme+",
                                                                                colour=discord.Colour.orange()))
                    await user.send(embed=discord.Embed(title="Плохие новости. У вас был снят meme+",
                                                        description=f"\nАдминистрация решила у вас полностью снять meme+",
                                                        colour=discord.Colour.red()))
            elif result["premium_status"]:
                end_time = result["premium_status_end"] - datetime.timedelta(days=time_in_days)
                PROFILE_COLLECTION.update_one(result, {"$set": {"premium_status_end": end_time}})
                await interaction.response.send_message(embed=discord.Embed(title="У пользователя была уменьшена поддержка meme+",
                                                                            description=f"У пользователя **{user.name}** был уменьшен срок meme+ на **{time_in_days}** дней",
                                                                            colour=discord.Colour.orange()))
                await user.send(embed=discord.Embed(title="Плохие новости. У вас было сокращено время meme+",
                                                    description=f"\nАдминистрация решила у вас уменьшить время meme+ на **{time_in_days}** дней"
                                                                f"\nСрок действия поддержки: `{end_time.strftime('%d.%m.%Y')}`",
                                                    colour=discord.Colour.red()))
            else:
                await interaction.response.send_message(embed=discord.Embed(title="Пользователь не имеет meme+",
                                                                            description=f"Пользователь под id **{user_id}** не имеет meme+",
                                                                            colour=discord.Colour.red()))
                return
            member = self.bot.get_guild(settings["guild"]).get_member(user_id)
            if member is not None and member.get_role(self.premium_role.id):
                await member.remove_roles(self.premium_role)
        else:
            await interaction.response.send_message(embed=discord.Embed(title="Пользователь не найден",
                                                                        description=f"Пользователь под id **{user_id}** не найден",
                                                                        colour=discord.Colour.red()))

    @app_commands.command(description="[Только для поддержавших] Ваши meme+ настройки профиля")
    async def plus_settings(self, interaction: discord.Interaction):
        user = PROFILE_COLLECTION.find_one({"user_id": interaction.user.id})
        if user is not None and user["premium_status"]:
            r = user['meme_color'][0]
            g = user['meme_color'][1]
            b = user['meme_color'][2]
            try:
                embed = discord.Embed(title="⭐ Настройки вашего meme+ профиля ⭐",
                                      description=f"\n🚀 Ваша поддержка активна до: `{user['premium_status_end'].strftime('%d.%m.%Y')}`"
                                                  f"\n"
                                                  f"\n🔸 [/meme_color] **Цвет у мемов:** `{r} {g} {b}` (RGB)"
                                                  f"\n"
                                                  f"\n🔸 [/set_publicity] **Показывать никнейм:** `{user['show_nickname']}`"
                                                  f"\n🔸 [/set_publicity] **Показывать тег рядом с ником:** `{user['show_tag']}`"
                                                  f"\n"
                                                  f"\n🔸 [/set_url] **Ссылки в мемах:** `{user['show_url']}`"
                                                  f"\n🔸 [/set_url] **Текущая ссылка:** ```{user['custom_url']}```"
                                                  f"\n"
                                                  f"\n[скоро] **Интервал времени между авто-мемами**",
                                      colour=discord.Colour.from_rgb(r=r, g=g, b=b))
            except KeyError:
                embed = discord.Embed(title="⭐ Настройки вашего meme+ профиля ⭐",
                                      description=f"\n🚀 Ваша поддержка активна: `навсегда`"
                                                  f"\n"
                                                  f"\n🔸 [/meme_color] **Цвет у мемов:** `{r} {g} {b}` (RGB)"
                                                  f"\n"
                                                  f"\n🔸 [/set_publicity] **Показывать никнейм:** `{user['show_nickname']}`"
                                                  f"\n🔸 [/set_publicity] **Показывать тег рядом с ником:** `{user['show_tag']}`"
                                                  f"\n"
                                                  f"\n🔸 [/set_url] **Ссылки в мемах:** `{user['show_url']}`"
                                                  f"\n🔸 [/set_url] **Текущая ссылка:** ```{user['custom_url']}```"
                                                  f"\n"
                                                  f"\n[скоро] **Интервал времени между авто-мемами**",
                                      colour=discord.Colour.from_rgb(r=r, g=g, b=b))
            embed.set_author(name=f"[meme+] {interaction.user.display_name}",
                             icon_url=interaction.user.avatar)
            embed.set_footer(text=f'🚀 Команда только для поддержавших бота')
            await interaction.response.send_message(embed=embed)
            return
        await interaction.response.send_message(embed=discord.Embed(title="Ошибка",
                                                                    description=f"Только пользователи с meme+ могут смотреть премиум настройки",
                                                                    color=0xff0000))


class PaymentSelect(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.select(placeholder="Выберите способ оплаты", options=[discord.SelectOption(label="QIWI 30 дней - 30 руб.",
                                                                                           value="1:30",
                                                                                           emoji=discord.PartialEmoji.from_str("<:qiwi:987444061969469440>")),
                                                                      discord.SelectOption(label="QIWI 90 дней - 70 руб.",
                                                                                           value="3:70",
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
                                                                                    f"\nСсылка на оплату:"
                                                                                    f"\n{bill.pay_url}",
                                                                        colour=discord.Colour.gold()))


async def setup(bot):
    print("Setup Payment")
    await bot.add_cog(Payment(bot))