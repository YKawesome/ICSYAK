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
    @app_commands.command(name='send', description='Sends a message in a particular channel')
    async def send(self, interaction: discord.Interaction, channel: discord.TextChannel, message: str):
        message = message.replace('\\n', '\n')
        await channel.send(message)
        await interaction.response.send_message(f'Sent message to {channel}', ephemeral=True, delete_after=5)

    @app_commands.default_permissions(administrator=True)
    @app_commands.command(name='reply', description='Replies to a specified message')
    async def reply(self, interaction: discord.Interaction, message_id: str, reply: str):
        message_id = int(message_id)
        message = await interaction.channel.fetch_message(message_id)
        await message.reply(reply)
        await interaction.response.send_message(f'Replied to message {message_id}', ephemeral=True, delete_after=5)

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

    @app_commands.default_permissions(administrator=True)
    @app_commands.command(name='create_problem_threads', description='Creates problem threads for a test. Seperate outcomes by spaces.')
    async def create_problem_threads(self, interaction: discord.Interaction, assn_name: str, problems_string: str):
        forum: discord.ForumChannel = interaction.guild.get_channel(1195541144210247800)
        problems = problems_string.split(' ')
        try:
            tag = discord.utils.get(forum.available_tags, name=assn_name)
        except discord.errors.HTTPException:
            await interaction.response.send_message(f'No tag found for {assn_name}', ephemeral=True, delete_after=5)
            return
        for problem in problems:
            await forum.create_thread(name=f'{assn_name} Problem {problem}', auto_archive_duration=1440, content='Post solutions here!', applied_tags=[tag])
        await interaction.response.send_message(f'Created problem threads for {",".join(problems)} for {assn_name}', ephemeral=True, delete_after=5)


async def setup(bot: commands.Bot):
    await bot.add_cog(ADMIN(bot))