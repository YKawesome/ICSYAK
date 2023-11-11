import discord
from discord import app_commands
from discord.ext import commands, tasks
import ed


class APLCOMS(commands.Cog, description='Application Commands'):

  def __init__(self, bot):
    self.bot = bot
    self.get_pinned.start()
    self.get_general.start()
    self.get_the.start()
    self.get_ther.start()

  @app_commands.command()
  async def testapp(self, interaction: discord.Interaction) -> None:
    await interaction.response.send_message("hello from the command!")

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
        await channel.send(embed=embed)
        await channel.send('<@&1172439119218098176>')
      else:
        pass

  @tasks.loop(minutes=15)
  async def get_general(self):
    await APLCOMS.do_message(self, 'General', 1172703040659263548, 0x0565a8, 1172697491964170324)

  @tasks.loop(minutes=15)
  async def get_the(self):
    await APLCOMS.do_message(self, 'Take-home exam questions', 1172704581059366973, 0xc84300, 1172697491964170324)

  @tasks.loop(minutes=15)
  async def get_ther(self):
    await APLCOMS.do_message(self, 'THE redo questions', 1172704616845148180, 0xad32d9, 1172697491964170324)
  
  
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


  async def do_message(self, category: str, channel_id: int, color, role_id: int):
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
      author = 'Anonymous' if ed.get_author(thread) is None else ed.get_author(thread)
      test = f'{ed.get_title(thread)}: {author}, in {ed.get_category(thread)}' in retlist
  
      if not test:
        embed = ed.make_embed(thread, color)
        await channel.send(embed=embed)
        await channel.send(f'<@&{role_id}>')
      else:
        pass


async def setup(bot: commands.Bot):
  await bot.add_cog(APLCOMS(bot))
