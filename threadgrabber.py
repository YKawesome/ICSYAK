import discord
from discord import app_commands
from discord.ext import commands, tasks
import ed


class THREADGRABBER(commands.Cog, description='Grabs Threads from Ed Discussion'):
    def __init__(self, bot):
        self.bot = bot
        self.get_pinned.start()
        self.get_general.start()
        self.get_the.start()
        self.get_ther.start()
        self.get_midterms.start()
        self.get_other.start()

    @tasks.loop(minutes=30)
    async def get_pinned(self):
        await THREADGRABBER.do_message(
            self,
            channel_id=1172439850218180618,
            color=0x50288c,
            role_id=1172439119218098176
            )

    @tasks.loop(minutes=15)
    async def get_general(self):
        await THREADGRABBER.do_message(
            self,
            category='General',
            channel_id=1172703040659263548,
            color=0x0565a8,
            role_id=1172697491964170324
            )

    @tasks.loop(minutes=30)
    async def get_other(self):
        await THREADGRABBER.do_message(
            self,
            category='Other',
            channel_id=1174506533552390184,
            color=0x339d5d,
            role_id=1172697491964170324
            )

    @tasks.loop(minutes=16)
    async def get_the(self):
        await THREADGRABBER.do_message(
            self,
            category='Take-home exam questions',
            channel_id=1172704581059366973,
            color=0xc84300,
            role_id=1172697491964170324
            )

    @tasks.loop(minutes=17)
    async def get_ther(self):
        await THREADGRABBER.do_message(
            self,
            category='THE redo questions',
            channel_id=1172704616845148180,
            color=0xad32d9,
            role_id=1172697491964170324
            )

    @tasks.loop(minutes=18)
    async def get_midterms(self):
        await THREADGRABBER.do_message(
            self,
            category='Midterms',
            channel_id=1173040165606924371,
            color=0x4e7d00,
            role_id=1172697491964170324
        )

    async def do_message(self, channel_id: int, color, role_id: int, category: str = None):
        if category is None:
            print('yessir')
            limit = 3
        else:
            limit = 50
        channel = await self.bot.fetch_channel(channel_id)
        print(channel)
        msgs = [message async for message in channel.history(limit=100)]
        retlist = []
        for msg in msgs:
            try:
                embed = msg.embeds[0].title
                retlist.append(embed)
            except Exception:
                continue

        threads = ed.get_threads(limit)
        if category is not None:
            threads = ed.filter_threads(threads, category, False)
        threads = sorted(threads, key=ed.get_date)

        for thread in threads:
            author = 'Anonymous' if ed.get_author(thread) is None else ed.get_author(thread)
            test = f'{ed.get_title(thread)}: {author}, in {ed.get_category(thread)}' in retlist

            if not test:
                embed = ed.make_embed(thread, color)
                msg = await channel.send(embed=embed)
                await msg.add_reaction('❤️')
                await channel.send(f'<@&{role_id}>')

    @app_commands.command(name='link_thread', description='Links a thread from Ed Discussion')
    async def link_thread(self, interaction: discord.Interaction, thread_number: int):
        try:
            thread = ed.get_course_thread(48103, thread_number)
        except Exception:
            await interaction.response.send_message(f'Thread {thread_number} has been deleted or was private.')
            return
        embed = ed.make_embed_no_user(thread, 0xf47fff)
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(THREADGRABBER(bot))
