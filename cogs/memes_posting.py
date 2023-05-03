import discord
from discord import app_commands, ui
from discord.ext import commands

from classes.Logger import log_to_console
from cogs.meme_moderation import process_and_send_meme_to_moderation_channel


class MemesPosting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="upload_meme", description="Выложить свой мем")
    @app_commands.describe(attachment="Медиафайл (поддерживаемые форматы: .jpeg .jepg .jpg .png .gif)")
    async def upload_meme(self, interaction: discord.Interaction, attachment: discord.Attachment):

        if attachment.filename.endswith((".jpeg", ".jepg", ".jpg", ".png", ".gif")):
                                     # 30MB
                if attachment.size < 31_457_280:
                    await interaction.response.send_modal(SendingMemeContextMenu(self.bot, attachment))
                else:
                    await interaction.response.send_message(ephemeral=True,
                                                            content="Максимальный размер файла: **30МБ**")
        else:
            await interaction.response.send_message(ephemeral=True,
                                                    content="Поддерживаемые форматы файла: .jepg .jpg .png .gif")


class SendingMemeContextMenu(ui.Modal, title="Выложить мем"):
    def __init__(self, bot, attachment: discord.Attachment):
        self.attachment = attachment
        self.bot = bot
        super().__init__()

    description = ui.TextInput(label="Описание", placeholder="Я люблю Meme Land!", style=discord.TextStyle.short,
                               required=False)
    tags = ui.TextInput(label="Теги (до 5 тегов)", style=discord.TextStyle.paragraph,
                                   placeholder='Каждый тег отделяется Запятой (пример: "привет, мир" - #привет #мир)',
                                   required=False)
    users_agreement = ui.TextInput(label="Соглашение перед отправкой", style=discord.TextStyle.paragraph,
                                   placeholder='Нажимая на кнопку "отправить", вы соглашаетесь '
                                               'с правилами модерации мемов. Мы за позитив в боте =)',
                                   max_length=1,
                                   required=False)

    async def on_submit(self, interaction: discord.Interaction):
        tags = self.tags.value.replace(" ", "")
        if len(tags) > 0:
            tags = tags.split(",")
            tags = tags[:min(len(tags), 5)]
        else:
            tags = []
        embed = discord.Embed(description=f"📔 **Описание:** {self.description}" if len(self.description.value.strip()) > 0 else None,
                              colour=discord.Colour.blue())
        embed.add_field(name="Теги", value=f"{'`#' + '` `#'.join(tags) + '`' if len(tags) > 0 else '`Отсутствуют`'}")
        embed.set_author(icon_url=interaction.user.avatar, name=f'{interaction.user.name} отправляет мем на модерацию!')
        embed.set_image(url=self.attachment.url)
        embed.set_footer(text="Обычно мемы проверяются меньше 24 часов 😋")
        await interaction.response.send_message(embed=embed)

        await process_and_send_meme_to_moderation_channel(self.bot, embed, interaction, tags)


async def setup(bot):
    log_to_console(f"Loaded {__file__}")
    await bot.add_cog(MemesPosting(bot))
