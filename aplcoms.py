import discord
from discord import app_commands
from discord.ext import commands, tasks
import ed
from datetime import datetime


class APLCOMS(commands.Cog, description='Application Commands'):

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
    await APLCOMS.do_message(self, 'General', 1172703040659263548, 0x0565a8,
                             1172697491964170324)

  @tasks.loop(minutes=30)
  async def get_other(self):
    await APLCOMS.do_message(self, 'Other', 1174506533552390184, 0x339d5d,
                             1172697491964170324)

  @tasks.loop(minutes=16)
  async def get_the(self):
    await APLCOMS.do_message(self, 'Take-home exam questions',
                             1172704581059366973, 0xc84300,
                             1172697491964170324)

  @tasks.loop(minutes=17)
  async def get_ther(self):
    await APLCOMS.do_message(self, 'THE redo questions', 1172704616845148180,
                             0xad32d9, 1172697491964170324)

  @tasks.loop(minutes=18)
  async def get_midterms(self):
    await APLCOMS.do_message(self, 'Midterms', 1173040165606924371, 0x4e7d00,
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

  @commands.Cog.listener()
  async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
    if payload.member.id == 1172417098065125436:
      return None
    channel = discord.utils.get(self.bot.get_all_channels(),
                                id=payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    member = message.author
    await message.remove_reaction(payload.emoji, payload.member)
    if member.id == 1172417098065125436:
      try:
        emb = message.embeds[0]
        id = emb.footer.text.split('| ')[-1]
      except:
        return None
    try:
      ed_thread = ed.get_thread(int(id))
    except UnboundLocalError:
      return None
    comments = ed_thread['comments']
    answers = ed_thread['answers']
    replies = comments + answers

    try:
      thread = await message.create_thread(name=emb.title)
      lmsg = [msg async for msg in channel.history(limit=1)][0]
      await lmsg.delete()
    except:
      thread = channel.get_thread(message.id)
      msgs = [message async for message in thread.history(limit=100)]
      del msgs[-1]
      for msg in msgs:
        await msg.delete()

    if len(replies) == 0:
      await thread.send(
          'No replies yet. Try reacting to the originalmessage again later.')
      return None

    for reply in replies:
      document = reply['document']
      embed = discord.Embed(description=document, color=0xf47fff)
      url = ed.get_reply_link(reply)
      embed.set_author(name=reply['user_id'], url=url)
      embed.set_footer(
          text=
          f'{ed.get_date_string(reply)} | A bot by yousef :D | {ed.get_id(reply)}'
      )
      await thread.send(embed=embed)

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
  await bot.add_cog(APLCOMS(bot))
