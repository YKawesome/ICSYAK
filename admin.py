import discord
from discord import app_commands
from discord.ext import commands


class ADMIN(commands.Cog, description='Administrative Commands'):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='testapp', description='Tests slash commands')
    async def testapp(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message('test')

    @app_commands.default_permissions(administrator=True)
    @app_commands.command(name='schizo', description='Gives someone the schizo role')
    async def schizo(self, interaction: discord.Interaction, member: discord.Member):
        # print(member)
        guild: discord.Guild = interaction.guild
        role = guild.get_role(1174252377591795772)
        # print(role)
        await member.add_roles(role)
        await interaction.response.send_message(f'<@{member.id}> has been schizo\'d.', ephemeral=True, delete_after=10)

    @app_commands.default_permissions(administrator=True)
    @app_commands.command(name='unschizo', description='Removes the schizo role from someone')
    async def unschizo(self, interaction: discord.Interaction, member: discord.Member):
        # print(member)
        guild: discord.Guild = interaction.guild
        role = guild.get_role(1174252377591795772)
        # print(role)
        await member.remove_roles(role)
        await interaction.response.send_message(f'<@{member.id}> has been unschizo\'d.', ephemeral=True, delete_after=10)


async def setup(bot: commands.Bot):
    await bot.add_cog(ADMIN(bot))