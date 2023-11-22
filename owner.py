import discord
from discord import app_commands
from discord.ext import commands


class OWNER(commands.Cog, description='Administrative Commands'):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='sync', description='Syncs the Command Tree')
    async def sync(self, interaction: discord.Interaction):
        await self.bot.tree.sync()
        await interaction.response.send_message('Command tree synced.')

    @app_commands.command(name='syncowner', description='Syncs the Owner Command Tree')
    async def syncowner(self, interaction: discord.Interaction):
        await self.bot.tree.sync(guild=discord.Object(id=930252479264882708))
        await interaction.response.send_message('Owner Command tree synced.')

    @commands.command(name='syn', description='Syncs the Command Tree')
    async def syn(self, ctx):
        print('syncing')
        await self.bot.tree.sync()
        await ctx.send('Command tree synced.')


async def setup(bot: commands.Bot):
    await bot.add_cog(OWNER(bot), guild=discord.Object(id=930252479264882708))
