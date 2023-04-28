import datetime

import discord
from discord import ui, app_commands
from discord.ext import commands
from discord.ext.commands import Cog

from classes import StaticParameters
from classes.DataBase import add_meme_in_moderation_collection, remove_meme_from_moderation_collection, \
    transfer_meme_from_moderation_to_accepted, delete_meme_by_id_from_accepted_collection, get_meme
from classes.Exp import add_user_exp
from classes.Logger import log_message, log_to_console, error_to_console
from classes.MemeObjects import Meme, SearchedMeme
from classes.configs import memes_channels_config
from classes.DMManager import send_user_reject_meme_dm_message, send_user_accepted_meme_dm_message, \
    send_user_deleted_meme_dm_message


class MemeModeration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        StaticParameters.moderation_channel = self.bot.get_channel(memes_channels_config.meme_moderation_channel_id)

    @app_commands.guilds(892493256129118260)
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.command(name="delete_meme", description="Удалить мем под id")
    @app_commands.describe(meme_id="id мема для удаления")
    @app_commands.describe(reason="причина удаления")
    async def delete_meme(self, interaction: discord.Interaction, meme_id: int, reason: str="Причина не указана"):
        meme = SearchedMeme(self.bot, meme_id)
        meme_embed = meme.get_embed()
        await interaction.response.send_message(embed=discord.Embed(description="Удаляю мем..."))
        if delete_meme_by_id_from_accepted_collection(meme_id):
            meme_embed.colour = discord.Colour.red()
            await send_user_deleted_meme_dm_message(meme_author=self.bot.get_user(meme.get_author_id()),
                                                    moderator=interaction.user,
                                                    reason=reason,
                                                    meme_embed=meme_embed,
                                                    meme_id=meme_id)
            await interaction.edit_original_response(
                embed=discord.Embed(description=f"Мем под ID `{meme_id}` успешно удалён"
                                                f"\nПричина: ```{reason}```",
                                    colour=discord.Colour.yellow()))
            await log_message(
                f"Мем под ID `{meme_id}` был удалён. \n**Модератор:** {interaction.user.mention} \n**Причина:** {reason}.")
        else:
            await interaction.edit_original_response(
                embed=discord.Embed(description=f"Не удалось удалить мем по ID `{meme_id}`",
                                    colour=discord.Colour.red()))


async def process_and_send_meme_to_moderation_channel(bot, embed: discord.Embed, interaction: discord.Interaction, tags: list):
    embed.add_field(name="Сервер", value=f'```{interaction.guild}```')
    embed.add_field(name="Пользователь", value=f'```{interaction.user}```')
    embed.add_field(name="ID пользователя", value=f"```py\n"
                                                  f"id={interaction.user.id}\n"
                                                  f"```")
    embed.set_footer(text="Соответствует ли этот мем правилам бота?\n"
                          '"Одобрить" - да | "Отклонить" - нет')
    message = await StaticParameters.moderation_channel.send(embed=embed, view=ModerationButtons(bot))

    add_meme_in_moderation_collection(url=embed.image.url,
                                      description=embed.description,
                                      message_id=message.id,
                                      interaction=interaction,
                                      tags=tags)


class ModerationButtons(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Одобрить", custom_id="persistent_view:accept", style=discord.ButtonStyle.green)
    async def accept_button(self, interaction_button: discord.Interaction, button: discord.ui.Button):
        meme_id = transfer_meme_from_moderation_to_accepted(interaction_button.message.id)
        meme_author = self.bot.get_user(int(interaction_button.message.embeds[0].fields[-1].value.split("\n")[1][3:]))
        meme_description = interaction_button.message.embeds[0].description
        await send_user_accepted_meme_dm_message(meme_author=meme_author,
                                                 moderator=interaction_button.user,
                                                 meme_id=meme_id,
                                                 image_url=interaction_button.message.embeds[0].image.url,
                                                 meme_description=meme_description)

        new_meme_embed = discord.Embed(title="⭐ Новый мем! ⭐",
                                       description=meme_description,
                                       colour=discord.Colour.blue(),
                                       timestamp=datetime.datetime.now())
        new_meme_embed.set_image(url=interaction_button.message.embeds[0].image.url)
        new_meme_embed.add_field(name="🏷️ ID мема", value=f"```{meme_id} 🏷️```")
        new_meme_embed.set_footer(text=f'⚡ Выкладывайте свои мемы: /upload_meme')
        new_meme_embed.add_field(name="😎 Автор", value=f'```{meme_author}```')
        new_meme_embed.add_field(name="👮 Одобрил модератор", value=f"```{interaction_button.user}```")

        add_user_exp(user_id=meme_author.id, exp=25)
        message = await StaticParameters.new_memes_channel.send(embed=new_meme_embed)
        await interaction_button.message.delete()
        await log_message(
            f"Был принят мем модератором {interaction_button.user.mention} под ID: {meme_id}")
        try:
            await message.publish()
        except discord.Forbidden or discord.HTTPException:
            pass
        await interaction_button.response.send_message("Мем принят", ephemeral=True)

    @discord.ui.button(label="Отклонить", custom_id="persistent_view:reject", style=discord.ButtonStyle.red)
    async def reject_button(self, interaction_button: discord.Interaction, button: discord.ui.Button):
        await interaction_button.response.send_modal(RejectReason(self.bot, interaction_button.message))


class RejectReason(ui.Modal, title="Причина отклонения"):
    def __init__(self, bot, meme_in_moderation: discord.Message):
        self.meme_in_moderation = meme_in_moderation
        self.bot = bot
        super().__init__()

    reason = ui.TextInput(label="Причина", placeholder="Мем не понравился(", style=discord.TextStyle.long,
                          max_length=1000, required=False)

    async def on_submit(self, interaction: discord.Interaction):
        await send_user_reject_meme_dm_message(meme_author=self.bot.get_user(int(self.meme_in_moderation.embeds[0].fields[-1].value.split("\n")[1][3:])),
                                               moderator=interaction.user,
                                               reason=self.reason.value,
                                               image_url=self.meme_in_moderation.embeds[0].image.url,
                                               meme_description=self.meme_in_moderation.embeds[0].description)
        remove_meme_from_moderation_collection(self.meme_in_moderation.id)
        await self.meme_in_moderation.delete()
        await interaction.response.send_message("Мем отклонён", ephemeral=True)
        await log_message(
            f"Был отклонён мем модератором {interaction.user.mention}")


async def setup(bot):
    log_to_console(f"Loaded {__file__}")
    await bot.add_cog(MemeModeration(bot))