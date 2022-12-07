import random

import discord
from discord import app_commands
from discord.ext import commands

from classes.DataBase import like_meme
from classes.Exp import add_user_exp
from classes.MemeObjects import Meme


class MemesWatching(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.moderation_channel = None
        self.post_meme = False

    @app_commands.guilds(766386682047365190)
    @app_commands.command(name="meme", description="Посмотреть мем")
    @app_commands.describe(meme_id="ID мема")
    async def meme(self, interaction: discord.Interaction, meme_id: int = None):
        meme = Meme(self.bot, None if meme_id is None else meme_id)
        await interaction.response.send_message(embed=meme.get_embed(),
                                                view=RandomMeme(meme.get_meme_id(), self.bot, interaction)
                                                if meme.is_meme_exists else None)
        add_user_exp(interaction.user.id, random.randint(1, 5))

    @app_commands.guilds(766386682047365190)
    @app_commands.command(name="last_meme", description="Посмотреть свеженький мемчик")
    async def last_meme(self, interaction: discord.Interaction):
        await interaction.response.send_message(embed=Meme(self.bot, None).get_reversed_meme_embed())
        add_user_exp(interaction.user.id, random.randint(1, 5))

    @app_commands.guilds(766386682047365190)
    @app_commands.command(name="top_meme", description="Увидеть самый лучший мем в боте")
    async def top_meme(self, interaction: discord.Interaction):
        await interaction.response.send_message(embed=Meme(self.bot, None).get_top_meme_embed())
        add_user_exp(interaction.user.id, random.randint(1, 5))


class LikeMeme(discord.ui.View):
    def __init__(self, meme_id: int, bot: discord.Client, command_author: discord.Interaction=discord.Interaction):
        super().__init__()
        self.command_author = command_author
        self.meme_id = meme_id
        self.bot = bot

    @discord.ui.button(label="Лайкнуть", style=discord.ButtonStyle.blurple)
    async def like_button(self, interaction_button: discord.Interaction, button: discord.ui.Button):
        await like_meme(self.meme_id)
        button.disabled = True

        embed = interaction_button.message.embeds[0]
        likes_field = embed.fields[1]
        likes_counter = likes_field.value.split()
        likes_counter[0] = str(int(likes_counter[0]) + 1)
        embed.set_field_at(index=1,
                           name=likes_field.name,
                           value=" ".join(likes_counter),
                           inline=likes_field.inline)

        await interaction_button.response.edit_message(embed=embed, view=self)
        add_user_exp(interaction_button.user.id, 5)


class RandomMeme(LikeMeme, discord.ui.View):
    @discord.ui.button(label="Смотреть дальше", style=discord.ButtonStyle.green)
    async def randomise_meme(self, interaction_button: discord.Interaction, button: discord.ui.Button):
        if interaction_button.user.id == self.command_author.user.id:
            meme = Meme(self.bot)
            embed = meme.get_embed()
            self.meme_id = meme.get_meme_id()
            await interaction_button.response.edit_message(embed=embed,
                                                           view=self)
            add_user_exp(interaction_button.user.id, random.randint(1, 3))


async def setup(bot):
    print("Setup Meme_Rus")
    await bot.add_cog(MemesWatching(bot))