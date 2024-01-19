import discord
from discord import app_commands
from discord.ext import commands
import helphelpers


class UTILITY(commands.Cog, description='Utility Commands'):
    def __init__(self, bot):
        self.bot = bot
        self._reminder_list = []

    @app_commands.command(name='remindme', description='Reminds you of the next event in-class event')
    async def remindme(self, interaction: discord.Interaction):
        if interaction.user.mention not in self._reminder_list:
            self._reminder_list.append(interaction.user.mention)
            await interaction.response.send_message('I will remind you of the next in-class event.')
        else:
            await interaction.response.send_message('You are already on the list.')

    @app_commands.default_permissions(administrator=True)
    @app_commands.command(name='trigger_reminder', description='Triggers the reminder')
    async def trigger_reminder(self, interaction: discord.Interaction, msg: str):
        if len(self._reminder_list) == 0:
            await interaction.response.send_message('No one is on the list.')
            return
        await interaction.response.send_message(' '.join(self._reminder_list) + ', ' + msg)
        self._reminder_list = []

    @app_commands.command(name='join_helper_list', description='Adds you to the helper list')
    async def join_helper_list(self, interaction: discord.Interaction):
        helpers = helphelpers.get_helpers_json()
        helpees = helphelpers.get_helpees_json()
        if str(interaction.user.id) in helpers:
            await interaction.response.send_message('You are already on the list.', ephemeral=True, delete_after=5)
        elif str(interaction.user.id) in helpees:
            await interaction.response.send_message('You cannot be on both lists.', ephemeral=True, delete_after=5)
        else:
            helphelpers.add_helper(interaction.user.name, interaction.user.id)
            await interaction.response.send_message('You have been added to the list.', ephemeral=True, delete_after=5)

    @app_commands.command(name='leave_helper_list', description='Removes you from the helper list')
    async def leave_helper_list(self, interaction: discord.Interaction):
        helpers = helphelpers.get_helpers_json()
        if str(interaction.user.id) in helpers:
            helphelpers.remove_helper(str(interaction.user.id))
            await interaction.response.send_message('You have been removed from the list.', ephemeral=True, delete_after=5)
        else:
            await interaction.response.send_message('You were already not on the list.', ephemeral=True, delete_after=5)

    @app_commands.command(name='join_needs_help_list', description='Adds you to the needs help list')
    async def join_helpee_list(self, interaction: discord.Interaction):
        helpees = helphelpers.get_helpees_json()
        helpers = helphelpers.get_helpers_json()
        if str(interaction.user.id) in helpees:
            await interaction.response.send_message('You are already on the list.', ephemeral=True, delete_after=5)
        elif str(interaction.user.id) in helpers:
            await interaction.response.send_message('You cannot be on both lists.', ephemeral=True, delete_after=5)
        else:
            helphelpers.add_helpee(interaction.user.name, interaction.user.id)
            await interaction.response.send_message('You have been added to the list.', ephemeral=True, delete_after=5)

    @app_commands.command(name='leave_needs_help_list', description='Removes you from the needs help list')
    async def leave_helpee_list(self, interaction: discord.Interaction):
        helpees = helphelpers.get_helpees_json()
        if str(interaction.user.id) in helpees:
            helphelpers.remove_helpee(str(interaction.user.id))
            await interaction.response.send_message('You have been removed from the list.', ephemeral=True, delete_after=5)
        else:
            await interaction.response.send_message('You were already not on the list.', ephemeral=True, delete_after=5)

    @app_commands.command(name='show_help_list', description='Lists the helpers and people who need help')
    async def show_help_list(self, interaction: discord.Interaction):
        await interaction.response.send_message(embed=helphelpers.make_help_list_embed())

    @app_commands.default_permissions(administrator=True)
    @app_commands.command(name='clear_helper_list', description='Clears the helpers list')
    async def clear_helper_list(self, interaction: discord.Interaction):
        helphelpers.clear_helper_list()
        await interaction.response.send_message('The helpers list has been cleared.', ephemeral=True, delete_after=5)

    @app_commands.default_permissions(administrator=True)
    @app_commands.command(name='clear_helpee_list', description='Clears the helpees list')
    async def clear_helpee_list(self, interaction: discord.Interaction):
        helphelpers.clear_helpee_list()
        await interaction.response.send_message('The helpees list has been cleared.', ephemeral=True, delete_after=5)

    @app_commands.command(name='help_user', description='Helps a user')
    async def help_user(self, interaction: discord.Interaction, user: discord.User):
        helpers = helphelpers.get_helpers_json()
        helpees = helphelpers.get_helpees_json()
        if str(interaction.user.id) not in helpers:
            await interaction.response.send_message('You are not a registered helper. Please use the /join_helper_list command.', ephemeral=True, delete_after=5)
            return

        if str(user.id) in helpers:
            await interaction.response.send_message(f'{user.mention} is a helper and thus cannot be helped', ephemeral=True, delete_after=5)
        elif str(user.id) in helpees:
            helphelpers.remove_helpee(str(user.id))
            helphelpers.remove_helper(str(interaction.user.id))
            await interaction.response.send_message(f'{user.mention}, {interaction.user.mention} will help you. Please start a dm!')
        else:
            await interaction.response.send_message(f'{user.mention} is not registered to be helped.', ephemeral=True, delete_after=5)

    @app_commands.command(name='get_help_from', description='Gets help from a helper')
    async def get_help_from(self, interaction: discord.Interaction, user: discord.User):
        helpers = helphelpers.get_helpers_json()
        helpees = helphelpers.get_helpees_json()
        if str(interaction.user.id) not in helpees:
            await interaction.response.send_message('You are not registered to be helped. Please use the /join_needs_help_list command.', ephemeral=True, delete_after=5)
            return

        if str(user.id) in helpers:
            helphelpers.remove_helpee(str(interaction.user.id))
            helphelpers.remove_helper(str(user.id))
            await interaction.response.send_message(f'{interaction.user.mention}, {user.mention} will help you. Please start a dm!')
        elif str(user.id) in helpees:
            await interaction.response.send_message(f'{user.mention} needs help and thus cannot help you', ephemeral=True, delete_after=5)
        else:
            await interaction.response.send_message(f'{user.mention} is not registered to help.', ephemeral=True, delete_after=5)


async def setup(bot: commands.Bot):
    await bot.add_cog(UTILITY(bot))
