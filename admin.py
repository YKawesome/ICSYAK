import discord
from discord import app_commands
from discord.ext import commands
from color_palette import grab_palette


COLOR_SEPERATOR = '———MANAGED———'


class ADMIN(commands.Cog, description='Administrative Commands'):
    def __init__(self, bot: commands.Bot):
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
    @app_commands.command(name='create_problem_threads', description='Creates problem threads for a test. Seperate outcomes by spaces.')
    async def create_problem_threads(self, interaction: discord.Interaction, forum: discord.ForumChannel, assn_name: str, problems_string: str):
        problems = problems_string.split(' ')
        try:
            tag = discord.utils.get(forum.available_tags, name=assn_name.split(' ')[0])
            if tag is None:
                raise Exception
        except Exception:
            await interaction.response.send_message(f'No tag found for {assn_name}', ephemeral=True, delete_after=5)
            return
        for problem in problems:
            await forum.create_thread(name=f'{assn_name} Problem {problem}', auto_archive_duration=1440, content='Post solutions here!', applied_tags=[tag])
        await interaction.response.send_message(f'Created problem threads for {",".join(problems)} for {assn_name}', ephemeral=True, delete_after=5)

    @app_commands.command(name='solved', description='Marks a forum post as solved')
    async def solved(self, interaction: discord.Interaction):
        if interaction.channel.type != discord.ChannelType.public_thread:
            await interaction.response.send_message('This command can only be used in a thread', ephemeral=True, delete_after=5)
            return
        thread = interaction.channel
        forum: discord.ForumChannel = thread.parent
        try:
            tag = discord.utils.get(forum.available_tags, name='Solved')
            if tag is None:
                raise Exception
        except Exception:
            tag = await forum.create_tag(name='Solved', emoji='✅', moderated=False)
        await thread.add_tags(tag)
        await interaction.response.send_message(f'Marked thread {thread} as solved :white_check_mark:')

    @app_commands.command(name='unsolved', description='Marks a forum post as unsolved')
    async def unsolved(self, interaction: discord.Interaction):
        if interaction.channel.type != discord.ChannelType.public_thread:
            await interaction.response.send_message('This command can only be used in a thread', ephemeral=True, delete_after=5)
            return
        thread = interaction.channel
        forum: discord.ForumChannel = thread.parent
        tag = discord.utils.get(forum.available_tags, name='Solved')
        if tag is None:
            await interaction.response.send_message('This thread is not currently marked as solved.', ephemeral=True, delete_after=5)
            return
        await thread.remove_tags(tag)
        await interaction.response.send_message(f'Marked thread {thread} as unsolved :red_square:')

    @app_commands.command(name='img_verify', description='Verifies a user to post images')
    async def img_verify(self, interaction: discord.Interaction):
        # role = discord.utils.get(interaction.guild.roles, name='Image Verified')
        # if role is None:
        #     role = await interaction.guild.create_role(name='Image Verified', permissions=discord.Permissions(49152))
        # user = interaction.user
        # await user.add_roles(role)
        # await interaction.response.send_message('You have been granted image permissions. Use them wisely.', ephemeral=True, delete_after=5)
        await interaction.response.send_message('Image verification is currently disabled.', ephemeral=True, delete_after=5)

    @app_commands.default_permissions(administrator=True)
    @app_commands.command(name='push', description='Pushes a message to all channels with the name specified')
    async def push(self, interaction: discord.Interaction, channel_name: str, message: str):
        if interaction.user.id != 582730177763737640:
            await interaction.response.send_message('You do not have permission to use this command.', ephemeral=True, delete_after=5)
            return
        message = message.replace('\\n', '\n')
        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                if channel.name == channel_name:
                    await channel.send(message)
        await interaction.response.send_message(f'Pushed message to all channels named {channel_name}', ephemeral=True, delete_after=5)

    @app_commands.default_permissions(manage_roles=True)
    @app_commands.command(name='add_color_roles', description='Adds color roles to the server')
    @app_commands.describe(palette_choice='color palette to use')
    @app_commands.choices(palette_choice=[
        app_commands.Choice(name='Chromatic', value='Chromatic'),
        app_commands.Choice(name='Wonderland', value='Wonderland'),
        app_commands.Choice(name='Paintbox', value='Paintbox'),
        app_commands.Choice(name='Discord', value='Discord')
    ])
    async def add_color_roles(self, interaction: discord.Interaction, palette_choice: app_commands.Choice[str]):
        await interaction.response.defer(ephemeral=True, thinking=True)
        palette = grab_palette(palette_choice.value)

        seen_start = False
        seen_end = False
        for role in interaction.guild.roles:
            if seen_start and role.name == COLOR_SEPERATOR:
                seen_end = True
            elif role.name == COLOR_SEPERATOR:
                seen_start = True

            if seen_end:
                if role:
                    await role.delete()
                break
            elif seen_start:
                if role:
                    await role.delete()

        await interaction.guild.create_role(name=COLOR_SEPERATOR)
        for color in palette.__dict__:
            await interaction.guild.create_role(name=color.replace('_', ' ').capitalize(), color=discord.Colour(int(palette[color][1:], base=16)))
        await interaction.guild.create_role(name=COLOR_SEPERATOR)
        await interaction.followup.send('Done.', ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(ADMIN(bot))