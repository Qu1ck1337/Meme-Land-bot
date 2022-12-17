import discord
from discord import app_commands, ui
from discord.ext import commands

from classes.DataBase import get_user, get_user_level, update_user_color

colors = {
    "0x3498db": ["🔵", "Голубой", 0],
    "0xFEE75C": ["🟡", "Жёлтый", 2],
    "0xe67e22": ["🟠", "Оранжевый", 4],
    "0xe74c3c": ["🔴", "Красный", 6],
    "0x1f8b4c": ["🟢", "Зелёный", 8],
    "0x7289da": ["🟣", "Фиолетовый", 10],
    "0x000000": ["⚫", "Чёрный", 12],
    "0xFFFFFF": ["⚪", "Белый", 14],
}
options = []

for key in colors:
    options.append(discord.SelectOption(label=f'[{colors[key][2]} уровень] {colors[key][1]}', emoji=colors[key][0], value=key))


class MemeColors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.guilds(766386682047365190)
    @app_commands.command(description="Поставить крутой цвет для твоих мемов!")
    async def set_color(self, interaction: discord.Interaction):
        try:
            user_level = get_user_level(interaction.user.id)
            color = get_user(interaction.user.id)["memes_color"]
            if color is None:
                update_user_color(interaction.user.id, "0x3498db")
                color = get_user(interaction.user.id)["memes_color"]
            color_list = colors[color]
            embed = discord.Embed(title="Установить цвет мемов",
                                  description=f"Текущий цвет:"
                                              f"\n```{' '.join(color_list[0:2])}```",
                                  colour=discord.Colour.from_str(color))
            await interaction.response.send_message(embed=embed, view=ChangeColor(user_level),
                                                    ephemeral=True)
        except Exception as ex:
            print(ex)


class ChangeColor(ui.View):
    def __init__(self, user_level: int):
        super().__init__(timeout=None)
        self.user_level = user_level

    @ui.select(placeholder="Сменить цвет", options=options)
    async def change_color(self, selector_interaction: discord.Interaction, selector: ui.Select):
        if self.user_level >= colors[selector.values[0]][2]:
            original_embed = selector_interaction.message.embeds[0]
            description = f"Текущий цвет: \n```{' '.join(colors[selector.values[0]][0:2])}```"
            update_user_color(selector_interaction.user.id, selector.values[0])
            await selector_interaction.response.edit_message(embed=discord.Embed(title=original_embed.title,
                                                                                 description=description,
                                                                                 colour=discord.Colour.from_str(selector.values[0])),
                                                             view=ChangeColor(self.user_level))
        else:
            await selector_interaction.response.send_message(f"Нужно достигнуть уровня **{colors[selector.values[0]][2]}**,"
                                                             f" чтобы разблокировать этот цвет.",
                                                             ephemeral=True)

    # @ui.button(label="Случайный цвет")
    # async def random_color(self, selector_interaction: discord.Interaction, button: ui.button):
    #     original_embed = selector_interaction.message.embeds[0]
    #     description = f"Текущий цвет: \n```Кастомный - ```"
    #     await selector_interaction.response.edit_message(embed=discord.Embed(title=original_embed.title,
    #                                                                          description=description,
    #                                                                          colour=discord.Colour.random()),
    #                                                      view=ChangeColor())


async def setup(bot):
    print("Setup MemeColors")
    await bot.add_cog(MemeColors(bot))