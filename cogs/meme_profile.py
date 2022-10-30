import datetime

import discord
from discord import app_commands, ui
from discord.ext import commands

from classes.DataBase import get_meme_ids_from_user, get_top_users
from classes.MemeObjects import Profile, Meme


class MemeProfile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.guilds(766386682047365190)
    @app_commands.command(name="profile", description="Увидеть себя в зеркале")
    async def profile(self, interaction: discord.Interaction):
        await interaction.response.send_message(embed=await Profile(interaction.user).get_user_profile(),
                                                view=MemeLibraryCheckButton(interaction.user.id))

    @app_commands.guilds(766386682047365190)
    @app_commands.command(description="Таблица лидеров")
    async def leaderboard(self, interaction: discord.Interaction):
        result = get_top_users()
        embed = discord.Embed(title="Топ-10 лучших мемеров бота Meme Land",
                              colour=discord.Colour.blue(),
                              timestamp=datetime.datetime.now())
        for num, rez in enumerate(result):
            embed.add_field(
                name=f"**{'🥇 ' if num == 0 else '🥈 ' if num == 1 else '🥉 ' if num == 2 else ''}{num + 1}. {self.bot.get_user(rez['user_id']).name if self.bot.get_user(rez['user_id']) else 'user id: ' + str(rez['user_id'])}**",
                value=f"`{rez['level']} уровень` | `{rez['memes_count']} 🗂️` | `{rez['memes_likes']} 👍`", inline=False)
        embed.set_thumbnail(url=interaction.guild.icon)
        embed.set_footer(text=f"Подробнее о себе /profile",
                         icon_url=interaction.user.avatar)

        await interaction.response.send_message(embed=embed)


class MemeLibraryCheckButton(ui.View):
    def __init__(self, author_id: int):
        super().__init__(timeout=None)
        self.author_id = author_id

    @discord.ui.button(label="Заглянуть в архив", emoji="🗂️", style=discord.ButtonStyle.green)
    async def accept_button(self, interaction_button: discord.Interaction, button: discord.ui.Button):
        ids = await get_meme_ids_from_user(self.author_id)
        profile_embed = interaction_button.message.embeds
        profile_embed.append(Meme(ids[0]).get_embed(f"Мем 1 / {len(ids)}"))
        await interaction_button.response.edit_message(embeds=profile_embed,
                                                       view=MemeLibraryScroller(interaction_button, ids) if len(ids) > 1 else None)


class MemeLibraryScroller(ui.View):
    def __init__(self, interaction: discord.Interaction, author_meme_ids: list):
        super().__init__(timeout=None)
        self.interaction = interaction
        self.author_meme_ids = author_meme_ids
        self.current_meme_id_index = 0

    # async def on_timeout(self):
    #     for child in self.children:
    #         child.disabled = True
    #         print(child)
    #     await self.interaction.edit_original_response(view=self)

    @discord.ui.button(label="Назад", emoji="◀", style=discord.ButtonStyle.green)
    async def previous_button(self, interaction_button: discord.Interaction, button: discord.ui.Button):
        self.current_meme_id_index -= 1
        self.index_corrector()
        await interaction_button.response.edit_message(embeds=self.replace_embed(interaction_button), view=self)

    @discord.ui.button(label="Далее", emoji="▶", style=discord.ButtonStyle.green)
    async def next_button(self, interaction_button: discord.Interaction, button: discord.ui.Button):
        self.current_meme_id_index += 1
        self.index_corrector()
        await interaction_button.response.edit_message(embeds=self.replace_embed(interaction_button), view=self)

    @discord.ui.button(label="Последний мем", emoji="↩", style=discord.ButtonStyle.blurple)
    async def newest_button(self, interaction_button: discord.Interaction, button: discord.ui.Button):
        self.current_meme_id_index = len(self.author_meme_ids) - 1
        await interaction_button.response.edit_message(embeds=self.replace_embed(interaction_button), view=self)

    def index_corrector(self):
        if self.current_meme_id_index < 0:
            self.current_meme_id_index = len(self.author_meme_ids) - 1
        elif self.current_meme_id_index > len(self.author_meme_ids) - 1:
            self.current_meme_id_index = 0

    def replace_embed(self, interaction_button):
        profile_embed = interaction_button.message.embeds
        profile_embed[1] = Meme(self.author_meme_ids[self.current_meme_id_index]).get_embed(
            f"Мем {self.current_meme_id_index + 1} / {len(self.author_meme_ids)}")
        return profile_embed


async def setup(bot):
    print(f"Setup MemeProfile")
    await bot.add_cog(MemeProfile(bot))