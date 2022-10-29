import discord
from discord import app_commands, ui
from discord.ext import commands

from classes.MemeObjects import Profile, Meme


class MemeProfile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.guilds(766386682047365190)
    @app_commands.command(name="profile", description="Увидеть себя в зеркале")
    async def profile(self, interaction: discord.Interaction):
        await interaction.response.send_message(embed=await Profile(interaction.user).get_user_profile(),
                                                view=MemeLibraryCheckButton())


class MemeLibraryCheckButton(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Заглянуть в архив", style=discord.ButtonStyle.green)
    async def accept_button(self, interaction_button: discord.Interaction, button: discord.ui.Button):
        profile_embed = interaction_button.message.embeds
        profile_embed.append(Meme(1).get_embed())
        await interaction_button.response.edit_message(embeds=profile_embed, view=MemeLibraryScroller())


class MemeLibraryScroller(ui.View):
    def __init__(self):
        super().__init__(timeout=5)

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        await self.

    @discord.ui.button(label="Далее", style=discord.ButtonStyle.green)
    async def next_button(self, interaction_button: discord.Interaction, button: discord.ui.Button):
        pass

    @discord.ui.button(label="Назад", style=discord.ButtonStyle.green)
    async def previous_button(self, interaction_button: discord.Interaction, button: discord.ui.Button):
        pass

    @discord.ui.button(label="Последний мем", style=discord.ButtonStyle.blurple)
    async def newest_button(self, interaction_button: discord.Interaction, button: discord.ui.Button):
        pass


async def setup(bot):
    print(f"Setup MemeProfile")
    await bot.add_cog(MemeProfile(bot))