import discord
from discord import app_commands
from discord.ext import commands, tasks
import ed
from datetime import datetime


class THREADGRABBER(commands.Cog, description='Grabs Threads from Ed Discussion'):

  def __init__(self, bot):
    self.bot = bot
    self.get_pinned.start()
    self.get_general.start()
    self.get_the.start()
    self.get_ther.start()
    self.get_midterms.start()
    self.get_other.start()

  @app_commands.command()
  async def testapp(self, interaction: discord.Interaction) -> None:
    await interaction.response.send_message(datetime.now())

  @tasks.loop(minutes=30)
  async def get_pinned(self):
    print('ran!')
    channel = await self.bot.fetch_channel(1172439850218180618)
    msgs = [message async for message in channel.history(limit=10)]
    retlist = []
    for msg in msgs:
      try:
        embed = msg.embeds[0].title
        retlist.append(embed)
      except:
        pass

    for thread in ed.get_threads(3):
      test = f'{ed.get_title(thread)}: {ed.get_author(thread)}, in {ed.get_category(thread)}' in retlist

      if not test:
        embed = ed.make_embed(thread, 0x50288c)
        msg = await channel.send(embed=embed)
        await msg.add_reaction('❤️')
        await channel.send('<@&1172439119218098176>')
      else:
        pass

  @tasks.loop(minutes=15)
  async def get_general(self):
    await THREADGRABBER.do_message(self, 'General', 1172703040659263548, 0x0565a8,
                             1172697491964170324)

  @tasks.loop(minutes=30)
  async def get_other(self):
    await THREADGRABBER.do_message(self, 'Other', 1174506533552390184, 0x339d5d,
                             1172697491964170324)

  @tasks.loop(minutes=16)
  async def get_the(self):
    await THREADGRABBER.do_message(self, 'Take-home exam questions',
                             1172704581059366973, 0xc84300,
                             1172697491964170324)

  @tasks.loop(minutes=17)
  async def get_ther(self):
    await THREADGRABBER.do_message(self, 'THE redo questions', 1172704616845148180,
                             0xad32d9, 1172697491964170324)

  @tasks.loop(minutes=18)
  async def get_midterms(self):
    await THREADGRABBER.do_message(self, 'Midterms', 1173040165606924371, 0x4e7d00,
                             1172697491964170324)

  @commands.command(name='sync', description='Owner only')
  async def sync(self, ctx):
    if ctx.author.id == 582730177763737640:
      await ctx.send('syncing command tree')
      await self.bot.tree.sync()
      await ctx.send('Command tree synced.')
    else:
      await ctx.send('You must be the owner to use this command!')

  @app_commands.command()
  async def edtest(self, interaction: discord.Interaction) -> None:
    pass

  async def do_message(self, category: str, channel_id: int, color,
                       role_id: int):
    channel = await self.bot.fetch_channel(channel_id)
    print(channel)
    msgs = [message async for message in channel.history(limit=100)]
    retlist = []
    for msg in msgs:
      try:
        embed = msg.embeds[0].title
        retlist.append(embed)
      except:
        pass

    threads = ed.filter_threads(ed.get_threads(50), category)

    threads = sorted(threads, key=ed.get_date)

    for thread in threads:
      author = 'Anonymous' if ed.get_author(thread) is None else ed.get_author(
          thread)
      test = f'{ed.get_title(thread)}: {author}, in {ed.get_category(thread)}' in retlist

      if not test:
        embed = ed.make_embed(thread, color)
        msg = await channel.send(embed=embed)
        await msg.add_reaction('❤️')
        await channel.send(f'<@&{role_id}>')
      else:
        pass

  

  @commands.command(name='testing')
  async def testing(self, ctx):
    msg = await ctx.channel.fetch_message(1174141999318847578)
    thread = await msg.create_thread(name='testing')
    await thread.send('wahoo')

  @app_commands.default_permissions(administrator=True)
  @app_commands.command()
  async def schizo(self, interaction: discord.Interaction, member: discord.Member):
    # print(member)
    guild: discord.Guild = interaction.guild
    role = guild.get_role(1174252377591795772)
    # print(role)
    await member.add_roles(role)
    await interaction.response.send_message(f'<@{member.id}> has been schizo\'d.', ephemeral=True, delete_after=10)

  @app_commands.default_permissions(administrator=True)
  @app_commands.command()
  async def unschizo(self, interaction: discord.Interaction, member: discord.Member):
    # print(member)
    guild: discord.Guild = interaction.guild
    role = guild.get_role(1174252377591795772)
    # print(role)
    await member.remove_roles(role)
    await interaction.response.send_message(f'<@{member.id}> has been unschizo\'d.', ephemeral=True, delete_after=10)


async def setup(bot: commands.Bot):
  await bot.add_cog(THREADGRABBER(bot))
