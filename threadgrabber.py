import discord
from discord import app_commands
from discord.ext import commands, tasks
import ed
import piazza


class THREADGRABBER(commands.Cog, description="Grabs Threads from Ed Discussion"):
    def __init__(self, bot):
        self.bot = bot
        self.get_6b_pinned.start()
        # self.get_161_pinned.start()
        self.get_141_pinned.start()
        self.get_121_pinned.start()

    @tasks.loop(minutes=30)
    async def get_6b_pinned(self):
        await THREADGRABBER.do_ed_message(
            self,
            course_id=87345,
            channel_id=1354098640951578667,
            color=0x50288C,
            role_id=1197816299536003072,
            category="Pinned",
        )

    @tasks.loop(minutes=30)
    async def get_161_pinned(self):
        await THREADGRABBER.do_ed_message(
            self,
            course_id=77809,
            channel_id=1352531038957469756,
            color=0x50288C,
            role_id=1352565499036307466,
            category="Pinned",
        )

    @tasks.loop(minutes=30)
    async def get_121_pinned(self):
        await THREADGRABBER.do_ed_message(
            self,
            course_id=87804,
            channel_id=1418365288964952176,
            color=0x50288C,
            role_id=1418731515696644178,
            category="Pinned",
        )

    @tasks.loop(minutes=30)
    async def get_141_pinned(self):
        await THREADGRABBER.do_ed_message(
            self,
            course_id=87890,
            channel_id=1418200189763719278,
            color=0x50288C,
            role_id=1418197278367420479,
            category="Pinned",
        )

    async def do_ed_message(
        self, course_id: int, channel_id: int, color, role_id: int, category: str | None = None
    ):
        if category is None or category == "Pinned":
            limit = 6
        else:
            limit = 50
        channel = await self.bot.fetch_channel(channel_id)
        print(channel)
        msgs = [message async for message in channel.history(limit=100)]
        retlist = set()
        for msg in msgs:
            try:
                t_id = int(msg.embeds[0].footer.text.split("|")[-1].strip())

                retlist.add(t_id)
            except Exception:
                continue

        threads = ed.get_threads(limit, course_id)
        if category is not None and category != "Pinned":
            threads = ed.filter_threads(threads, category, False)
        threads = sorted(threads, key=ed.get_date)

        for thread in threads:
            test = int(ed.get_id(thread)) in retlist
            if category == "Pinned" and not ed.get_is_pinned(thread):
                continue

            if not test:
                embed = ed.make_embed(thread, color)
                try:
                    msg = await channel.send(embed=embed)
                except discord.errors.HTTPException:
                    continue
                await msg.add_reaction("❤️")
                await channel.send(f"<@&{role_id}>")

    async def do_piazza_message(self, class_id: str, channel_id: int, role_id: int):
        posts = piazza.get_posts(class_id, limit=6)
        channel = await self.bot.fetch_channel(channel_id)
        msgs = [message async for message in channel.history(limit=100)]
        retlist = set()
        for msg in msgs:
            try:
                t_id = int(msg.embeds[0].footer.text.split("|")[-1].strip())
                retlist.add(t_id)
            except Exception:
                continue

        for post in posts:
            if post.post_id in retlist:
                continue
            embed = post.embed
            msg = await channel.send(embed=embed)
            await msg.add_reaction("❤️")
            await channel.send(f"<@&{role_id}>")

    @app_commands.command(
        name="link_ed_thread", description="Links a thread from Ed Discussion"
    )
    @app_commands.describe(course_id="courses to choose from")
    @app_commands.choices(
        course_id=[
            app_commands.Choice(name="CS 161", value=77809),
            app_commands.Choice(name="CS 162", value=77807),
            app_commands.Choice(name="CS 178", value=77597),
            app_commands.Choice(name="CS 6B", value=77331),
        ]
    )
    async def link_ed_thread(
        self,
        interaction: discord.Interaction,
        thread_number: int,
        course_id: app_commands.Choice[int],
    ):
        try:
            thread = ed.get_course_thread(course_id.value, thread_number)
        except Exception:
            await interaction.response.send_message(
                f"Thread {thread_number} has been deleted or was private."
            )
            return
        embed = ed.make_embed(thread, 0xF47FFF)
        await interaction.response.send_message(embed=embed)

        if not interaction.channel:
            return
        if interaction.channel.type == discord.ChannelType.forum:
            await interaction.followup.send(
                "We are in a forum channel, so I am not listing the replies here."
            )
            return

        channel: discord.TextChannel = interaction.channel  # type: ignore

        new_message = channel.last_message
        if new_message is None:
            return
        if len(new_message.embeds) == 0:
            return
        try:
            d_thread = await new_message.create_thread(name=new_message.embeds[0].title or "Thread")
        except Exception:
            await channel.send(
                "We are in a thread already, so I am not listing the replies here."
            )
            return

        comments = thread["comments"]
        answers = thread["answers"]
        replies = comments + answers
        for reply in replies:
            document = reply["document"]
            embed = discord.Embed(description=document, color=0xF47FFF)
            url = ed.get_reply_link(reply)
            embed.set_author(name=reply["user_id"], url=url)
            embed.set_footer(
                text=f"{ed.get_date_string(reply)} | A bot by yousef :D | {ed.get_id(reply)}"
            )
            await d_thread.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(THREADGRABBER(bot))
