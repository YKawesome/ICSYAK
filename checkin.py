import discord
from discord import app_commands
from discord.ext import commands, tasks
import os
import datetime
import sqlite3
from zoneinfo import ZoneInfo

SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, "checkin.db")

CHECKIN_DAYS = {"Tuesday", "Thursday"}
REMINDER_DAYS = {"Monday", "Wednesday"}
CHECKIN_CHANNEL_ID = 1356725800849772775
REMINDER_CHANNEL_IDS = [1356725800849772775, 1358014326031781939]
CHECKIN_MSG = "# Good Morning <@&1356726753485127913>!\n It's time to check in :D"
REMINDER_MSG = (
    "# Pre-Lecture Preparation <@&{}>\nDon't forget "
    "to finish the pre-lecture assignment! Details on GradeScope.\n-# If there isn't one, apologies! This is an automated message."
)

START = datetime.time(
    hour=7, minute=50, second=0, tzinfo=ZoneInfo("America/Los_Angeles")
)
CUTOFF = datetime.time(
    hour=8, minute=15, second=0, tzinfo=ZoneInfo("America/Los_Angeles")
)
REMINDER_TIME = datetime.time(
    hour=21, minute=0, second=0, tzinfo=ZoneInfo("America/Los_Angeles")
)


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS checkins (
            user_id TEXT NOT NULL,
            date TEXT NOT NULL,
            UNIQUE(user_id, date)
        )
    """
    )
    conn.commit()
    conn.close()


async def get_today_info():
    now = datetime.datetime.now(tz=ZoneInfo("America/Los_Angeles"))
    today = now.strftime("%A")
    return now, today


async def delete_last_bot_message(channel, match_text=None):
    old_msg = await anext(channel.history(limit=1))
    if old_msg and old_msg.author == channel.guild.me:
        if match_text is None or old_msg.content == match_text:
            await old_msg.delete()


async def has_checked_in_today(user_id, date):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT 1 FROM checkins WHERE user_id = ? AND date = ?", (user_id, date))
    result = c.fetchone() is not None
    conn.close()
    return result


async def add_checkin(user_id, date):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO checkins (user_id, date) VALUES (?, ?)", (user_id, date))
    conn.commit()
    conn.close()


class MyView(discord.ui.View):
    def __init__(self):
        super().__init__()
        button = discord.ui.Button(label="Check In", style=discord.ButtonStyle.primary)
        button.callback = self.check_in_callback
        self.add_item(button)

    async def check_in_callback(self, interaction: discord.Interaction):
        now, today = await get_today_info()
        curr_day = now.strftime("%m/%d")

        if today not in CHECKIN_DAYS or now.time() > CUTOFF.replace(tzinfo=None):
            await interaction.response.send_message(
                "checkin ends at 8:15, ur too late :(", ephemeral=True, delete_after=5
            )
            return

        user_id = str(interaction.user.id)

        if await has_checked_in_today(user_id, curr_day):
            await interaction.response.send_message(
                "You have already checked in today!", ephemeral=True, delete_after=5
            )
        else:
            await add_checkin(user_id, curr_day)
            await interaction.response.send_message(
                "You checked in!", ephemeral=True, delete_after=5
            )


class CHECKIN(commands.Cog, description="Checkin system"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        init_db()
        self.checkin.start()
        self.reminder.start()

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

    @app_commands.default_permissions(administrator=True)
    @app_commands.command(
        name="send_checkin",
        description="Manually send today's checkin message",
    )
    async def send_checkin(self, interaction: discord.Interaction):
        channel = self.bot.get_channel(CHECKIN_CHANNEL_ID)
        await delete_last_bot_message(channel, CHECKIN_MSG)
        view = MyView()
        await channel.send(CHECKIN_MSG, view=view)
        await interaction.response.send_message(
            "Check-in message sent!", ephemeral=True, delete_after=5
        )

    @app_commands.command(name="leaderboard", description="Get the checkin leaderboard")
    async def leaderboard(self, interaction: discord.Interaction):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT user_id, COUNT(*) FROM checkins GROUP BY user_id")
        checkins = c.fetchall()
        conn.close()

        embed = discord.Embed(
            title="🏆 All-Time Check-in Leaderboard", color=discord.Color.gold()
        )

        if not checkins:
            embed.description = "No check-ins yet!"
        else:
            sorted_checkins = sorted(checkins, key=lambda x: x[1], reverse=True)
            for i, (user_id, count) in enumerate(sorted_checkins[:10], start=1):
                embed.add_field(
                    name=f"{i}.",
                    value=f"<@{user_id}> — **{count}** check-ins",
                    inline=False,
                )

        await interaction.response.send_message(embed=embed)

    @tasks.loop(time=[REMINDER_TIME])
    async def reminder(self):
        _, today = await get_today_info()
        if today not in REMINDER_DAYS:
            return

        for c_id in REMINDER_CHANNEL_IDS:
            channel = self.bot.get_channel(c_id)
            await delete_last_bot_message(channel, REMINDER_MSG)
            await channel.send(
                REMINDER_MSG.format(
                    discord.utils.get(channel.guild.roles, name="REMINDER PINGS").id
                )
            )

    @reminder.before_loop
    async def before_reminder(self):
        await self.bot.wait_until_ready()  # Wait until the bot is ready

    @app_commands.default_permissions(administrator=True)
    @app_commands.command(
        name="send_reminder",
        description="Manually send today's reminder message",
    )
    async def send_reminder(self, interaction: discord.Interaction):
        channel = interaction.channel
        await delete_last_bot_message(channel)
        await channel.send(
            REMINDER_MSG.format(
                discord.utils.get(interaction.guild.roles, name="REMINDER PINGS").id
            )
        )

        await interaction.response.send_message(
            "Reminder message sent!", ephemeral=True, delete_after=5
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(CHECKIN(bot))
