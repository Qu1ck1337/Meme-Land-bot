import discord
from discord import ui
from discord.ext import commands
from discord.ext.commands import Cog

from classes import StaticParameters
from classes.DataBase import add_meme_in_moderation_collection, remove_meme_from_moderation_collection, \
    transform_meme_from_moderation_to_accepted
from classes.configs import memes_posting_config
from classes.dm_manager import send_user_reject_meme_dm_message, send_user_accept_meme_dm_message


class MemeModeration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener("on_ready")
    async def on_ready(self):
        StaticParameters.moderation_channel = self.bot.get_channel(memes_posting_config.meme_moderation_channel_id)


async def process_and_send_meme_to_moderation_channel(bot, embed: discord.Embed, interaction: discord.Interaction):
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
                                      interaction=interaction)


class ModerationButtons(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Одобрить", custom_id="persistent_view:accept", style=discord.ButtonStyle.green)
    async def accept_button(self, interaction_button: discord.Interaction, button: discord.ui.Button):
        meme_id = transform_meme_from_moderation_to_accepted(interaction_button.message.id)
        await send_user_accept_meme_dm_message(self.bot,
                                               user_id=int(interaction_button.message.embeds[0].fields[2].value.split("\n")[1][3:]),
                                               moderator=interaction_button.user,
                                               meme_id=meme_id,
                                               image_url=interaction_button.message.embeds[0].image.url,
                                               meme_description=interaction_button.message.embeds[0].description)
        await interaction_button.message.delete()
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
        await send_user_reject_meme_dm_message(self.bot,
                                               user_id=int(self.meme_in_moderation.embeds[0].fields[2].value.split("\n")[1][3:]),
                                               moderator=interaction.user,
                                               reason=self.reason.value,
                                               image_url=self.meme_in_moderation.embeds[0].image.url,
                                               meme_description=self.meme_in_moderation.embeds[0].description)
        remove_meme_from_moderation_collection(self.meme_in_moderation.id)
        await self.meme_in_moderation.delete()
        await interaction.response.send_message("Мем отклонён", ephemeral=True)


async def setup(bot):
    print("Setup MemeModeration")
    await bot.add_cog(MemeModeration(bot))