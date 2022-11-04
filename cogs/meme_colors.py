import discord
from discord import app_commands, ui
from discord.ext import commands

from classes.DataBase import get_user, save_user_memes_color

colors = {
    "0xe74c3c": ["🔴", "Красный"],
    "0xe67e22": ["🟠", "Оранжевый"],
    "0xFEE75C": ["🟡", "Жёлтый"],
    "0x1f8b4c": ["🟢", "Зелёный"],
    "0x3498db": ["🔵", "Голубой"],
    "0x7289da": ["🟣", "Фиолетовый"],
    "rgb(0, 0, 0)": ["⚫", "Чёрный"],
    "rgb(255, 255, 255)": ["⚪", "Белый"]
}
options = []
for key in colors:
    options.append(discord.SelectOption(label=colors[key][1], emoji=colors[key][0], value=key))


class MemeColors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.guilds(766386682047365190)
    @app_commands.command(description="Поставить крутой цвет для твоих мемов!")
    async def color_memes(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Установить цвет мемов",
                              description="Текущий цвет:"
                                          "\n```🔵 Голубой```",
                              colour=discord.Colour.blue())
        await interaction.response.send_message(embed=embed, view=ChangeColor(embed.color))


class ChangeColor(ui.View):
    def __init__(self, color_before):
        super().__init__(timeout=180)
        self.current_color = color_before
        print(self.current_color)

    @ui.select(placeholder="Стандартные цвета", options=options)
    async def change_color(self, selector_interaction: discord.Interaction, selector: ui.Select):
        original_embed = selector_interaction.message.embeds[0]
        description = f"Текущий цвет: \n```{' '.join(colors[selector.values[0]])}```"
        self.current_color = discord.Colour.from_str(selector.values[0])
        await selector_interaction.response.edit_message(embed=discord.Embed(title=original_embed.title,
                                                                             description=description,
                                                                             colour=self.current_color),
                                                         view=self)

    @ui.button(label="Случайный цвет", style=discord.ButtonStyle.blurple)
    async def random_color(self, button_interaction: discord.Interaction, button: ui.button):
        original_embed = button_interaction.message.embeds[0]
        self.current_color = discord.Colour.random()
        description = f"Текущий цвет: \n```{self.current_color}```"
        await button_interaction.response.edit_message(embed=discord.Embed(title=original_embed.title,
                                                                           description=description,
                                                                           colour=self.current_color),
                                                       view=self)

    @ui.button(label="Применить", style=discord.ButtonStyle.green)
    async def accept_button(self, button_interaction: discord.Interaction, button: ui.button):
        original_embed = button_interaction.message.embeds[0]
        save_user_memes_color(button_interaction.user.id, str(self.current_color))
        await button_interaction.response.edit_message(content="Успех!", embed=original_embed, view=self)


async def setup(bot):
    print("Setup MemeColors")
    await bot.add_cog(MemeColors(bot))