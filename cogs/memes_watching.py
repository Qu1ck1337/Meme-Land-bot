import random

import discord
from discord import app_commands
from discord.ext import commands

from classes.DataBase import like_meme
from classes.Exp import add_user_exp
from classes.Logger import log_to_console
from classes.MemeObjects import RandomedMeme, SearchedMeme, NewMeme, PopularMeme, TaggedMeme


class MemesWatching(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.moderation_channel = None
        self.post_meme = False

    @app_commands.command(name="meme", description="Посмотреть мем")
    @app_commands.describe(meme_id="ID мема")
    @app_commands.describe(tag="Тег мемов")
    async def meme(self, interaction: discord.Interaction, meme_id: int=None, tag: str=None):
        await interaction.response.defer()
        is_searched_or_randomed_meme = False
        if meme_id is not None or tag is not None:
            if tag is not None:
                meme = TaggedMeme(self.bot, tag=tag)
            else:
                meme = SearchedMeme(self.bot, meme_id=meme_id)
                is_searched_or_randomed_meme = True
        else:
            meme = RandomedMeme(self.bot)
            is_searched_or_randomed_meme = True

        if is_searched_or_randomed_meme:
            embed = meme.get_embed("Мемчик")
            await interaction.edit_original_response(embed=embed,
                                                    view=RandomMeme(meme.get_meme_id(), self.bot, interaction)
                                                    if meme_id is None or (meme_id is not None and meme.is_meme_exist()) else _()
                                                    )
        else:
            embed = meme.get_embed(f"Мем под тегом «{tag}»")
            await interaction.edit_original_response(embed=embed,
                                                    view=NextTaggedMeme(meme, meme.get_meme_id(), self.bot, interaction)
                                                    if meme.is_meme_object_exist() else _()
                                                    )

        add_user_exp(interaction.user.id, random.randint(1, 5))

    @app_commands.command(name="last_meme", description="Посмотреть свеженький мемчик")
    async def last_meme(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await interaction.edit_original_response(embed=NewMeme(self.bot).get_embed("Мем прямо из печи!"))
        add_user_exp(interaction.user.id, random.randint(1, 5))

    @app_commands.command(name="top_meme", description="Увидеть самый лучший мем в боте")
    async def top_meme(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await interaction.edit_original_response(embed=PopularMeme(self.bot).get_embed("Самый популярный мем"))
        add_user_exp(interaction.user.id, random.randint(1, 5))


class _(discord.ui.View):
    pass


class LikeMeme(discord.ui.View):
    def __init__(self, meme_id: int, bot: discord.Client, command_author: discord.Interaction=discord.Interaction):
        super().__init__()
        self.meme_id = meme_id
        self.bot = bot
        self.command_author = command_author

    @discord.ui.button(label="Лайкнуть", emoji="♥", style=discord.ButtonStyle.blurple)
    async def like_button(self, interaction_button: discord.Interaction, button: discord.ui.Button):
        await like_meme(self.meme_id)

        embed = interaction_button.message.embeds[0]
        likes_field = embed.fields[1]
        likes_counter = likes_field.value.strip("```").split()
        likes_counter[0] = str(int(likes_counter[0]) + 1)
        embed.set_field_at(index=1,
                           name=likes_field.name,
                           value=f'```{" ".join(likes_counter)}```',
                           inline=likes_field.inline)
        add_user_exp(interaction_button.user.id, 5)
        button.label = "Лайкнуто"
        button.emoji = "👍"
        button.disabled = True
        await interaction_button.response.edit_message(embed=embed, view=self)


class RandomMeme(LikeMeme, discord.ui.View):
    @discord.ui.button(label="Случайный мем", emoji="🔀", style=discord.ButtonStyle.green)
    async def randomise_meme(self, interaction_button: discord.Interaction, button: discord.ui.Button):
        if interaction_button.user.id == self.command_author.user.id:
            meme = RandomedMeme(self.bot)
            embed = meme.get_embed("Рандомный мемчик")
            self.meme_id = meme.get_meme_id()
            await interaction_button.response.edit_message(embed=embed,
                                                           view=RandomMeme(self.meme_id, self.bot, interaction_button))
            add_user_exp(interaction_button.user.id, random.randint(1, 3))


class NextTaggedMeme(LikeMeme, discord.ui.View):
    def __init__(self, tagged_meme_obj: TaggedMeme, meme_id: int, bot: discord.Client, command_author: discord.Interaction=discord.Interaction):
        super().__init__(meme_id, bot, command_author)
        self.tagged_meme_obj = tagged_meme_obj
        self.prev_meme.disabled = False if self.tagged_meme_obj.is_prev_exists() else True
        self.next_meme.disabled = False if self.tagged_meme_obj.is_next_exists() else True

    @discord.ui.button(label="", emoji="⏮️", style=discord.ButtonStyle.green)
    async def prev_meme(self, interaction_button: discord.Interaction, button: discord.ui.Button):
        if interaction_button.user.id == self.command_author.user.id:
            self.tagged_meme_obj.prev()
            embed = self.tagged_meme_obj.get_embed(f"Мем под тегом «{self.tagged_meme_obj.tag}»")
            self.meme_id = self.tagged_meme_obj.get_meme_id()
            await interaction_button.response.edit_message(embed=embed,
                                                           view=NextTaggedMeme(self.tagged_meme_obj, self.meme_id, self.bot, interaction_button))
            add_user_exp(interaction_button.user.id, random.randint(1, 3))

    @discord.ui.button(label="", emoji="⏭️", style=discord.ButtonStyle.green)
    async def next_meme(self, interaction_button: discord.Interaction, button: discord.ui.Button):
        if interaction_button.user.id == self.command_author.user.id:
            self.tagged_meme_obj.next()
            embed = self.tagged_meme_obj.get_embed(f"Мем под тегом «{self.tagged_meme_obj.tag}»")
            self.meme_id = self.tagged_meme_obj.get_meme_id()
            await interaction_button.response.edit_message(embed=embed,
                                                           view=NextTaggedMeme(self.tagged_meme_obj, self.meme_id, self.bot, interaction_button))
            add_user_exp(interaction_button.user.id, random.randint(1, 3))


async def setup(bot):
    log_to_console(f"Loaded {__file__}")
    await bot.add_cog(MemesWatching(bot))