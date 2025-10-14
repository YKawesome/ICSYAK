import discord
from discord import app_commands
from discord.ext import commands


class GROUPS(commands.Cog, description="Group Finding"):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="find_group", description="Find a study group")
    async def find_group(self, interaction: discord.Interaction):
        if not interaction.guild:
            await interaction.response.send_message(
                "This command can only be used in a server.",
                ephemeral=True,
                delete_after=5,
            )
            return

        open_group_role = discord.utils.get(interaction.guild.roles, name="Open Group")
        no_group_role = discord.utils.get(interaction.guild.roles, name="No Group")
        if not open_group_role or not no_group_role:
            await interaction.response.send_message(
                "Role(s) not found. Is this the right server?",
                ephemeral=True,
                delete_after=5,
            )
            return

        # Get all users with the open group role
        members_with_open_role = [
            member
            for member in interaction.guild.members
            if open_group_role in member.roles
        ]

        # Get all users with the no group role
        members_with_no_group_role = [
            member
            for member in interaction.guild.members
            if no_group_role in member.roles
        ]

        embed = discord.Embed(
            title="Groups", colour=0x00B0F4
        )

        embed.add_field(
            name="Open Group",
            value="\n".join(member.mention for member in members_with_open_role)[:1000]
            or "No users found.",
            inline=False,
        )

        embed.add_field(
            name="No Group",
            value="\n".join(member.mention for member in members_with_no_group_role)[:1000]
            or "No users found.",
            inline=False,
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(GROUPS(bot))
