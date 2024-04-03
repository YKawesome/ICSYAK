import discord
from discord import app_commands
from discord.ext import commands, tasks
import ed


class THREADGRABBER(commands.Cog, description='Grabs Threads from Ed Discussion'):
    def __init__(self, bot):
        self.bot = bot
        self.get_6b_pinned.start()
        self.get_45c_pinned.start()
        self.get_51_pinned.start()

    @tasks.loop(minutes=30)
    async def get_6b_pinned(self):
        await THREADGRABBER.do_message(
            self,
            course_id=57816,
            channel_id=1224153183891492894,
            color=0x50288c,
            role_id=1197816299536003072,
            category='Pinned'
            )

    @tasks.loop(minutes=30)
    async def get_45c_pinned(self):
        await THREADGRABBER.do_message(
            self,
            course_id=57763,
            channel_id=1224858801346449519,
            color=0x50288c,
            role_id=1224858955281465364,
            category='Pinned'
            )
    
    @tasks.loop(minutes=30)
    async def get_51_pinned(self):
        await THREADGRABBER.do_message(
            self,
            course_id=57105,
            channel_id=1225142977996001381,
            color=0x50288c,
            role_id=1225143041019482323
            )

    async def do_message(self, course_id: int, channel_id: int, color, role_id: int, category: str = None):
        if category is None or category == 'Pinned':
            limit = 6
        else:
            limit = 50
        channel = await self.bot.fetch_channel(channel_id)
        print(channel)
        msgs = [message async for message in channel.history(limit=100)]
        retlist = set()
        for msg in msgs:
            try:
                t_id = int(msg.embeds[0].footer.text.split('|')[-1].strip())
                retlist.add(t_id)
            except Exception:
                continue

        threads = ed.get_threads(limit, course_id)
        if category is not None and category != 'Pinned':
            threads = ed.filter_threads(threads, category, False)
        threads = sorted(threads, key=ed.get_date)

        for thread in threads:
            print(ed.get_title(thread))
            test = int(ed.get_id(thread)) in retlist
            if category == 'Pinned' and not ed.get_is_pinned(thread):
                continue

            if not test:
                embed = ed.make_embed(thread, color)
                try:
                    msg = await channel.send(embed=embed)
                except discord.errors.HTTPException:
                    continue
                await msg.add_reaction('❤️')
                await channel.send(f'<@&{role_id}>')

    @app_commands.command(name='link_thread', description='Links a thread from Ed Discussion')
    async def link_thread(self, interaction: discord.Interaction, thread_number: int):
        try:
            thread = ed.get_course_thread(50505, thread_number)
        except Exception:
            await interaction.response.send_message(f'Thread {thread_number} has been deleted or was private.')
            return
        embed = ed.make_embed(thread, 0xf47fff)
        await interaction.response.send_message(embed=embed)

        new_message = interaction.channel.last_message
        if len(new_message.embeds) == 0:
            return
        try:
            d_thread = await new_message.create_thread(name=new_message.embeds[0].title)
        except Exception:
            await interaction.channel.send('We are in a thread already, so I am not listing the replies here.')
            return

        comments = thread['comments']
        answers = thread['answers']
        replies = comments + answers
        for reply in replies:
            document = reply['document']
            embed = discord.Embed(description=document, color=0xf47fff)
            url = ed.get_reply_link(reply)
            embed.set_author(name=reply['user_id'], url=url)
            embed.set_footer(text=f'{ed.get_date_string(reply)} | A bot by yousef :D | {ed.get_id(reply)}')
            await d_thread.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(THREADGRABBER(bot))
