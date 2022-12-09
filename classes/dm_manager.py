import discord


async def send_user_reject_meme_dm_message(bot: discord.Client, user_id: int, moderator: discord.User, reason: str,
                                           image_url: str, meme_description: str):
    try:
        embed = discord.Embed(title="Уведомление от модерации",
                              description="Нам пришлось отклонить ваш мем, причина отклонения написана ниже.",
                              colour=discord.Colour.red())
        embed.add_field(name="👮 Модератор", value=f"```{moderator}```")
        embed.add_field(name="📋 Причина", value=f"```{reason if reason != '' else 'Причина не указана'}```")

        meme_embed = discord.Embed(description=meme_description, colour=discord.Colour.red())
        meme_embed.set_image(url=image_url)
        meme_embed.set_footer(text="🔨 Остались вопросы? Обратитесь в нашу поддержку /support")

        await bot.get_user(user_id).send(embeds=[embed, meme_embed])
    except Exception:
        pass


async def send_user_accept_meme_dm_message(bot: discord.Client, user_id: int, moderator: discord.User, meme_id: int,
                                           image_url: str, meme_description: str):
    try:
        embed = discord.Embed(title="Уведомление от модерации",
                              description=f"Поздравляем, ваш мем одобрен! "
                                          f"\nТеперь можно жёстко пофлексить от радости) 😏"
                                          f"\n"
                                          f"\n⚠ Внимание, из-за политики безопасности дискорда мы не можем держать ваши мемы больше 2х недель. "
                                          f"\n\n***Официальный ответ от EBOLA (создателя бота)***: «Сейчас стараемся всеми усилиями увеличить срок хранения мемов для наших пользователей бота»",
                              colour=discord.Colour.green())
        embed.add_field(name="👮 Модератор", value=f"```{moderator}```")
        embed.add_field(name="🏷️ ID мема", value=f"```{meme_id}```")

        meme_embed = discord.Embed(description=meme_description, colour=discord.Colour.green())
        meme_embed.set_image(url=image_url)
        meme_embed.set_footer(text="🔨 Остались вопросы? Обратитесь в нашу поддержку /support")

        await bot.get_user(user_id).send(embeds=[embed, meme_embed])
    except Exception:
        pass