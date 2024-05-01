import discord
from discord.ext import commands
import ed
import piazza


class EVENTHANDLERS(commands.Cog, description='Event Handlers'):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        await self.get_replies_from_thread(payload)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild = member.guild
        if guild.id == 1055582457509986315 and member.id in {582730177763737640, 295697456019144704}:
            role = discord.utils.get(guild.roles, id=1221188916569313441)
            await member.add_roles(role)
            print('added prev owner role')

    async def get_replies_from_thread(self, payload: discord.RawReactionActionEvent):
        bot_id = 1172417098065125436
        if payload.member.id == bot_id:
            return

        channel = discord.utils.get(self.bot.get_all_channels(), id=payload.channel_id)
        if channel is None:
            return

        message = await self.fetch_message(channel, payload.message_id)
        if message is None or message.author.id != bot_id or not (channel.name.startswith('ed') or channel.name.startswith('piazza')):
            return

        if not await self.remove_reaction_if_applicable(message, payload):
            return

        thread, error_msg = await self.process_message_thread(message)
        if error_msg and thread:
            await self.send_error_message(thread, error_msg)
        elif error_msg:
            print(error_msg)
        else:
            emb = message.embeds[0]
            thread_id = int(emb.footer.text.split('| ')[-1])
            if thread_id > 1000:
                await self.send_ed_replies(thread, message)
            else:
                await self.send_piazza_replies(thread, message)

    async def fetch_message(self, channel, message_id):
        try:
            return await channel.fetch_message(message_id)
        except Exception:
            return None

    async def remove_reaction_if_applicable(self, message, payload):
        try:
            await message.remove_reaction(payload.emoji, payload.member)
            return True
        except Exception:
            return False

    async def process_message_thread(self, message):
        emb = message.embeds[0]
        thread_id = emb.footer.text.split('| ')[-1]
        if int(thread_id) < 1000:
            return None, None
        try:
            ed_thread = ed.get_thread(int(thread_id))
            replies = ed_thread['comments'] + ed_thread['answers']
            if not replies:
                return None, 'No replies yet. Try reacting to the original message again later.'
        except Exception:
            return None, 'This thread has been deleted.'

        thread = await self.get_or_create_thread(message, emb)
        return thread, None if replies else 'No replies yet. Try reacting to the original message again later.'

    async def get_or_create_thread(self, message, emb):
        try:
            thread = await message.create_thread(name=emb.title)
            last_msg = [msg async for msg in message.channel.history(limit=1)][0]
            await last_msg.delete()
        except Exception:
            thread = message.channel.get_thread(message.id)
            await self.clear_thread_messages(thread)
        return thread

    async def clear_thread_messages(self, thread):
        msgs = [msg async for msg in thread.history(limit=100)]
        for msg in msgs[:-1]:
            await msg.delete()

    async def send_error_message(self, thread, errormsg):
        await thread.send(errormsg)

    async def send_ed_replies(self, thread, message):
        emb = message.embeds[0]
        thread_id = emb.footer.text.split('| ')[-1]
        ed_thread = ed.get_thread(int(thread_id))
        replies = ed_thread['comments'] + ed_thread['answers']
        for reply in replies:
            embed = self.create_reply_embed(reply)
            await thread.send(embed=embed)

    async def send_piazza_replies(self, thread, message: discord.Message):
        assert thread is None
        emb = message.embeds[0]
        thread_id = emb.footer.text.split('| ')[-1]
        class_id = emb.footer.text.split('| ')[-2].strip()
        post = piazza.get_post(class_id, int(thread_id))
        await message.edit(embed=post.embed)

    def create_reply_embed(self, reply):
        document = reply['document']
        embed = discord.Embed(description=document, color=0xf47fff)
        url = ed.get_reply_link(reply)
        user = reply['user_id'] if reply['user_id'] != 0 else 'Anonymous'
        embed.set_author(name=user, url=url)
        embed.set_footer(text=f'{ed.get_date_string(reply)} | A bot by yousef :D | {ed.get_id(reply)}')
        return embed


async def setup(bot: commands.Bot):
    await bot.add_cog(EVENTHANDLERS(bot))