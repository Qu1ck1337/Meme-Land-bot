import discord
from discord import app_commands, ui
from discord.ext import commands
from discord.ext.commands import Cog

from classes import StaticParameters
from classes.DataBase import add_meme_in_moderation_collection
from classes.configs import memes_posting_config


class MemeModeration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener("on_ready")
    async def on_ready(self):
        StaticParameters.moderation_channel = self.bot.get_channel(memes_posting_config.meme_moderation_channel_id)


async def process_and_send_meme_to_moderation_channel(embed: discord.Embed, interaction: discord.Interaction):
    embed.add_field(name="Сервер", value=interaction.guild)
    embed.add_field(name="Пользователь", value=interaction.user)
    embed.set_footer(text="Соответствует ли этот мем правилам бота?\n"
                          '"Одобрить" - да | "Отклонить" - нет')
    message = await StaticParameters.moderation_channel.send(embed=embed, view=ModerationButtons())

    await add_meme_in_moderation_collection(url=embed.image.url,
                                            description=embed.description,
                                            message_id=message.id,
                                            interaction=interaction)


class ModerationButtons(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Одобрить", custom_id="persistent_view:accept", style=discord.ButtonStyle.green)
    async def accept_button(self, interaction_button: discord.Interaction, button: discord.ui.Button):
        await interaction_button.response.send_message("Одобрить")

    @discord.ui.button(label="Отклонить", custom_id="persistent_view:reject", style=discord.ButtonStyle.red)
    async def reject_button(self, interaction_button: discord.Interaction, button: discord.ui.Button):
        await interaction_button.response.send_message("Отклонить")


async def setup(bot):
    print("Setup MemeModeration")
    await bot.add_cog(MemeModeration(bot))