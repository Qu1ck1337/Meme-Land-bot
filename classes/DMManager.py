import discord


async def send_user_reject_meme_dm_message(meme_author: discord.User, moderator: discord.User, reason: str,
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

        await meme_author.send(embeds=[embed, meme_embed])
    except Exception:
        pass


async def send_user_accepted_meme_dm_message(meme_author: discord.User, moderator: discord.User, meme_id: int,
                                             image_url: str, meme_description: str):
    try:
        embed = discord.Embed(title="Уведомление от модерации",
                              description=f"Поздравляем, ваш мем одобрен! "
                                          f"\nТеперь можно жёстко пофлексить от радости) 😏",
                              colour=discord.Colour.green())
        embed.add_field(name="👮 Модератор", value=f"```{moderator}```")
        embed.add_field(name="🏷️ ID мема", value=f"```{meme_id}```")

        meme_embed = discord.Embed(description=meme_description, colour=discord.Colour.green())
        meme_embed.set_image(url=image_url)
        meme_embed.set_footer(text="🔨 Остались вопросы? Обратитесь в нашу поддержку /support")

        await meme_author.send(embeds=[embed, meme_embed])
    except Exception:
        pass


async def send_user_deleted_meme_dm_message(meme_author: discord.User, moderator, reason: str,
                                            meme_embed: discord.Embed, meme_id: int):
    try:
        embed = discord.Embed(title="Уведомление от модерации",
                              description=f"Нам пришлось удалить ваш мем под ID: **{meme_id}** по следующей причине.",
                              colour=discord.Colour.red())
        embed.add_field(name="👮 Модератор", value=f"```{moderator if moderator is not None else 'СИСТЕМА'}```")
        embed.add_field(name="📋 Причина", value=f"```{reason if reason != '' else 'Причина не указана'}```")

        meme_embed.set_footer(text="🔨 Остались вопросы? Обратитесь в нашу поддержку /support")

        await meme_author.send(embeds=[embed, meme_embed])
    except Exception:
        pass