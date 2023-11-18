import discord
from discord.ext import commands
import ed


class EVENTHANDLERS(commands.Cog, description='Event Handlers'):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        await self.get_replies_from_thread(payload)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        await self.embed_ed(message)

    async def get_replies_from_thread(self, payload: discord.RawReactionActionEvent):
        errormsg = None
        reactor = payload.member
        bot_id = 1172417098065125436
        bot_reaction = reactor.id == bot_id
        if bot_reaction:
            return None

        # If correct message type, remove reaction as confirmation
        channel = discord.utils.get(self.bot.get_all_channels(), id=payload.channel_id)
        try:
            message = await channel.fetch_message(payload.message_id)
        except Exception:
            return
        member = message.author
        if member.id == bot_id and channel.name.startswith('ed'):
            try:
                await message.remove_reaction(payload.emoji, payload.member)
                emb = message.embeds[0]
                thread_id = emb.footer.text.split('| ')[-1]
            except Exception:
                return
        else:
            return

        # Attempt to get thread replies
        try:
            ed_thread = ed.get_thread(int(thread_id))
            comments = ed_thread['comments']
            answers = ed_thread['answers']
            replies = comments + answers
            if len(replies) == 0:
                errormsg = 'No replies yet. Try reacting to the original message again later.'
        except Exception:
            errormsg = 'This thread has been deleted.'

        # Create thread, or if exists already, replace current replies
        try:
            thread = await message.create_thread(name=emb.title)
            lmsg = [msg async for msg in channel.history(limit=1)][0]
            await lmsg.delete()
        except Exception:
            thread = channel.get_thread(message.id)
            msgs = [message async for message in thread.history(limit=100)]
            del msgs[-1]
            for msg in msgs:
                await msg.delete()

        # Send error message if applicable
        if errormsg is not None:
            await thread.send(errormsg)
            return

        # Send replies
        for reply in replies:
            document = reply['document']
            embed = discord.Embed(description=document, color=0xf47fff)
            url = ed.get_reply_link(reply)
            embed.set_author(name=reply['user_id'], url=url)
            embed.set_footer(text=f'{ed.get_date_string(reply)} | A bot by yousef :D | {ed.get_id(reply)}')
            await thread.send(embed=embed)

    async def embed_ed(self, message: discord.Message):
        if not message.content.startswith('https://edstem.org/us/courses/48103/discussion/'):
            return
        ed_thread = ed.get_thread(int(message.content.split('/')[-1]))
        ed_title = ed.get_title(ed_thread)
        ed_category = ed.get_category(ed_thread)
        ed_document = ed.get_document(ed_thread)
        ed_link = ed.get_link(ed_thread)
        ed_date = ed.get_date_string(ed_thread)
        ed_id = ed.get_id(ed_thread)
        try:
            ed_author = ed.get_author(ed_thread)
        except Exception:
            ed_author = 'Anonymous'

        embed = discord.Embed(title=f'{ed_title}: {ed_author}, in {ed_category}', url=ed_link, description=ed_document, color=0xf47fff)
        embed.set_footer(text=f'{ed_date} | A bot by yousef :D | {ed_id}')

        new_message = await message.channel.send(f'> From {message.author.mention}:', embed=embed)
        try:
            thread = await new_message.create_thread(name=new_message.embeds[0].title)
        except Exception:
            await message.channel.send('We are in a thread already, so I am not listing the replies here.')
            return
        finally:
            await message.delete()

        comments = ed_thread['comments']
        answers = ed_thread['answers']
        replies = comments + answers
        for reply in replies:
            document = reply['document']
            embed = discord.Embed(description=document, color=0xf47fff)
            url = ed.get_reply_link(reply)
            embed.set_author(name=reply['user_id'], url=url)
            embed.set_footer(text=f'{ed.get_date_string(reply)} | A bot by yousef :D | {ed.get_id(reply)}')
            await thread.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(EVENTHANDLERS(bot))