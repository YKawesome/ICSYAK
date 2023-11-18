import discord
from discord.ext import commands
import ed

class EVENTHANDLERS(commands.Cog, description='Event Handlers'):
  
  def __init__(self, bot):
    self.bot = bot

  @commands.Cog.listener()
  async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
    if payload.member.id == 1172417098065125436:
      return None
    channel = discord.utils.get(self.bot.get_all_channels(),
                                id=payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    member = message.author
    if member.id == 1172417098065125436:
      try:
        await message.remove_reaction(payload.emoji, payload.member)
        emb = message.embeds[0]
        id = emb.footer.text.split('| ')[-1]
      except:
        return None
    ed_thread = None
    errormsg = None
    try:
      ed_thread = ed.get_thread(int(id))
    except UnboundLocalError:
      return None
    except:
      errormsg = 'This thread has been deleted.'

    replies = None
    if ed_thread is not None:
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

    if replies is not None and len(replies) == 0:
      errormsg = 'No replies yet. Try reacting to the original message again later.'
    if errormsg is not None:
      await thread.send(errormsg)
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
  
async def setup(bot: commands.Bot):
  await bot.add_cog(EVENTHANDLERS(bot))