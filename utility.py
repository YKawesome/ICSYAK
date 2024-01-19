import discord
from discord import app_commands
from discord.ext import commands


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


async def setup(bot: commands.Bot):
    await bot.add_cog(UTILITY(bot))
