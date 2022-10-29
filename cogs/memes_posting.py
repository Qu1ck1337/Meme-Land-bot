import discord
from discord import app_commands, ui
from discord.ext import commands

from cogs.meme_moderation import process_and_send_meme_to_moderation_channel


class MemesPosting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.guilds(766386682047365190)
    @app_commands.command(name="send_meme", description="Запостить мемчик")
    @app_commands.describe(attachment="Мем")
    async def send_meme(self, interaction: discord.Interaction, attachment: discord.Attachment):
        await interaction.response.send_modal(SendingMemeContextMenu(attachment))


class SendingMemeContextMenu(ui.Modal, title="Выложить мем"):
    def __init__(self, attachment: discord.Attachment):
        self.attachment = attachment
        super().__init__()

    description = ui.TextInput(label="Описание", placeholder="Я люблю Meme Land!", style=discord.TextStyle.short,
                               required=False)
    users_agreement = ui.TextInput(label="Соглашение перед отправкой", style=discord.TextStyle.paragraph,
                                   placeholder='Нажимая на кнопку "отправить", вы соглашаетесь '
                                               'с правилами модерации мемов. Мы за позитив в боте =)',
                                   max_length=1,
                                   required=False)

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(description=f"📔 **Описание:** {self.description}",
                              colour=discord.Colour.blue())
        embed.set_author(icon_url=interaction.user.avatar, name=f'{interaction.user.name} отправляет мем на модерацию!')
        embed.set_image(url=self.attachment.url)

        await process_and_send_meme_to_moderation_channel(embed, interaction)

        embed.set_footer(text="Обычно мемы проверяются меньше 24 часов ^-^")
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    print("Setup MemesPosting")
    await bot.add_cog(MemesPosting(bot))
