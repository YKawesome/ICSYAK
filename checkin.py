from discord import app_commands
from discord.ext import commands, tasks
from view import init_db, get_today_info, delete_last_bot_message
from view import (
    START,
    REMINDER_TIME,
    CHECKIN_DAYS,
    REMINDER_DAYS,
    CHECKIN_CHANNEL_ID,
    CHECKIN_MSG,
    REMINDER_MSG,
    DB_PATH,
    REMINDER_CHANNEL_IDS,
    SERVER_TO_GS,
)
from view import MyView
import sqlite3
import discord
from gradescope_helper import GradescopeHelper


class CHECKIN(commands.Cog, description="Checkin system"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # init_db()
        # self.checkin.start()
        # self.reminder.start()

    @tasks.loop(time=[START])
    async def checkin(self):
        _, today = await get_today_info()
        if today not in CHECKIN_DAYS:
            return

        channel = self.bot.get_channel(CHECKIN_CHANNEL_ID)
        await delete_last_bot_message(channel, CHECKIN_MSG)
        view = MyView()
        await channel.send(CHECKIN_MSG, view=view)

    @checkin.before_loop
    async def before_checkin(self):
        await self.bot.wait_until_ready()  # Wait until the bot is ready

    # @app_commands.default_permissions(administrator=True)
    # @app_commands.command(
    #     name="send_checkin",
    #     description="Manually send today's checkin message",
    # )
    # async def send_checkin(self, interaction: discord.Interaction):
    #     channel = self.bot.get_channel(CHECKIN_CHANNEL_ID)
    #     await delete_last_bot_message(channel, CHECKIN_MSG)
    #     view = MyView()
    #     await channel.send(CHECKIN_MSG, view=view)
    #     await interaction.response.send_message(
    #         "Check-in message sent!", ephemeral=True, delete_after=5
    #     )

    # @app_commands.default_permissions(administrator=True)
    # @app_commands.command(
    #     name="send_checkin_in",
    #     description="Manually send today's checkin message in a specific channel",
    # )
    # async def send_checkin_in(
    #     self, interaction: discord.Interaction, channel: discord.TextChannel
    # ):
    #     await delete_last_bot_message(channel, CHECKIN_MSG)
    #     view = MyView()
    #     await channel.send(CHECKIN_MSG, view=view)
    #     await interaction.response.send_message(
    #         f"Check-in message sent in {channel.mention}!",
    #         ephemeral=True,
    #         delete_after=5,
    #     )

    # @app_commands.command(name="leaderboard", description="Get the checkin leaderboard")
    # async def leaderboard(self, interaction: discord.Interaction, ephemeral: bool = False):
    #     await interaction.response.defer(ephemeral=ephemeral)
    #     conn = sqlite3.connect(DB_PATH)
    #     c = conn.cursor()
    #     c.execute("SELECT user_id, COUNT(*) FROM checkins GROUP BY user_id")
    #     checkins = c.fetchall()
    #     conn.close()

    #     embed = discord.Embed(
    #         title="🏆 All-Time Check-in Leaderboard", color=discord.Color.gold()
    #     )

    #     if not checkins:
    #         embed.description = "No check-ins yet!"
    #     else:
    #         sorted_checkins = sorted(checkins, key=lambda x: x[1], reverse=True)
    #         for i, (user_id, count) in enumerate(sorted_checkins[:10], start=1):
    #             embed.add_field(
    #                 name=f"{i}.",
    #                 value=f"{(await interaction.guild.fetch_member(int(user_id))).mention} — **{count}** check-ins",
    #                 inline=False,
    #             )
    #     # await interaction.response.send_message(embed=embed, ephemeral=ephemeral)
    #     await interaction.followup.send(embed=embed, ephemeral=ephemeral)

    async def _send_reminder_message(
        self, channel: discord.TextChannel, guild: discord.Guild
    ):
        await delete_last_bot_message(channel)

        gs = GradescopeHelper()
        course = gs.get_course_by_id(SERVER_TO_GS[guild.id])
        open_assns = gs.get_assignments(course, only_open=True)

        if not open_assns:
            return None

        open_assn = open_assns[0]
        try:
            file = discord.File(
                gs.get_template_file(open_assn), filename=open_assn.title + ".pdf"
            )
        except Exception:
            file = None

        role_id = discord.utils.get(guild.roles, name="REMINDER PINGS").id
        await channel.send(REMINDER_MSG.format(role_id, open_assn.title, course.get_url()), file=file)
        return open_assn

    @tasks.loop(time=[REMINDER_TIME])
    async def reminder(self):
        _, today = await get_today_info()
        if today not in REMINDER_DAYS:
            return

        for c_id in REMINDER_CHANNEL_IDS:
            channel = self.bot.get_channel(c_id)
            await self._send_reminder_message(channel, channel.guild)

    @reminder.before_loop
    async def before_reminder(self):
        await self.bot.wait_until_ready()  # Wait until the bot is ready

    # @app_commands.command(
    #     name="send_reminder",
    #     description="Manually send today's reminder message",
    # )
    # async def send_reminder(self, interaction: discord.Interaction):
    #     result = await self._send_reminder_message(
    #         interaction.channel, interaction.guild
    #     )
    #     if result:
    #         await interaction.response.send_message(
    #             "Reminder message sent!", ephemeral=True, delete_after=5
    #         )
    #     else:
    #         await interaction.response.send_message(
    #             "No open assignments found!", ephemeral=True, delete_after=5
    #         )

    # @app_commands.command(
    #     name="send_reminder_in",
    #     description="Manually send today's reminder message in a specific channel",
    # )
    # async def send_reminder_in(
    #     self, interaction: discord.Interaction, channel: discord.TextChannel
    # ):
    #     result = await self._send_reminder_message(channel, interaction.guild)
    #     if result:
    #         await interaction.response.send_message(
    #             f"Reminder message sent in {channel.mention}!",
    #             ephemeral=True,
    #             delete_after=5,
    #         )
    #     else:
    #         await interaction.response.send_message(
    #             "No open assignments found!", ephemeral=True, delete_after=5
    #         )

    # @app_commands.command(name="my_checkins", description="Show how many check-ins you've done")
    # async def checkin_me(self, interaction: discord.Interaction, ephemeral: bool = False):
    #     await self._show_checkin_stats(interaction, interaction.user, ephemeral)

    # @app_commands.command(name="user_checkins", description="Show how many check-ins another user has done")
    # async def checkin_user(self, interaction: discord.Interaction, member: discord.Member, ephemeral: bool = False):
    #     await self._show_checkin_stats(interaction, member, ephemeral)

    async def _show_checkin_stats(self, interaction: discord.Interaction, user: discord.abc.User, ephemeral: bool):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "SELECT COUNT(*) FROM checkins WHERE user_id = ?",
            (str(user.id),),
        )
        (user_count,) = c.fetchone()

        if user_count == 0:
            embed = discord.Embed(
                title="Check-in Stats",
                description=f"{user.display_name} has never checked in.",
                color=discord.Color.red(),
            )
            embed.set_author(
                name=user.display_name,
                icon_url=user.display_avatar.url,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            conn.close()
            return

        c.execute("SELECT COUNT(DISTINCT date) FROM checkins")
        (total_days,) = c.fetchone()
        c.execute("SELECT DISTINCT date FROM checkins WHERE user_id = ? ORDER BY date", (str(user.id),))
        user_dates = [row[0] for row in c.fetchall()]
        c.execute("SELECT user_id, COUNT(*) FROM checkins GROUP BY user_id")
        checkins = c.fetchall()
        conn.close()

        sorted_checkins = sorted(checkins, key=lambda x: x[1], reverse=True)
        rank = next(i + 1 for i, (uid, _) in enumerate(sorted_checkins) if str(uid) == str(user.id))
        total_users = len(sorted_checkins)
        percentile = 100 * (total_users - rank) / (total_users - 1) if total_users > 1 else 100

        embed = discord.Embed(
            title="Check-in Stats",
            description=(
                f"{user.display_name} has checked in **{user_count}** times!\n"
                f"That's **{user_count} / {total_days}** check-in days.\n\n"
                f"**Rank:** #{rank} out of {total_users} ({percentile:.1f} percentile)\n\n"
                "**Days checked in:**\n" +
                "\n".join(f"- {date}" for date in user_dates)
            ),
            color=discord.Color.blue(),
        )
        embed.set_author(
            name=user.display_name,
            icon_url=user.display_avatar.url,
        )

        await interaction.response.send_message(embed=embed, ephemeral=ephemeral)


async def setup(bot: commands.Bot):
    await bot.add_cog(CHECKIN(bot))
