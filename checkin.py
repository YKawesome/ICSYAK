import discord
from discord import app_commands
from discord.ext import commands, tasks
import os
import datetime
import sqlite3
from zoneinfo import ZoneInfo

SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, "checkin.db")


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


START = datetime.time(
    hour=7, minute=50, second=0, tzinfo=ZoneInfo("America/Los_Angeles")
)
CUTOFF = datetime.time(
    hour=8, minute=15, second=0, tzinfo=ZoneInfo("America/Los_Angeles")
)

CHECKIN_MSG = "# Good Morning <@&1356726753485127913>!\n It's time to check in :D"


class MyView(discord.ui.View):
    def __init__(self):
        super().__init__()
        button = discord.ui.Button(label="Check In", style=discord.ButtonStyle.primary)
        button.callback = self.check_in_callback
        self.add_item(button)

    async def check_in_callback(self, interaction: discord.Interaction):
        curr_day = datetime.datetime.now().strftime("%m/%d")

        now = datetime.datetime.now(tz=ZoneInfo("America/Los_Angeles"))
        today = now.strftime("%A")
        if today not in {"Tuesday", "Thursday"} or now.time() > CUTOFF.replace(
            tzinfo=None
        ):
            await interaction.response.send_message(
                "checkin ends at 8:15, ur too late :(", ephemeral=True, delete_after=5
            )
            return

        user_id = str(interaction.user.id)

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "SELECT 1 FROM checkins WHERE user_id = ? AND date = ?", (user_id, curr_day)
        )
        if c.fetchone():
            await interaction.response.send_message(
                "You have already checked in today!", ephemeral=True, delete_after=5
            )
        else:
            c.execute(
                "INSERT INTO checkins (user_id, date) VALUES (?, ?)",
                (user_id, curr_day),
            )
            conn.commit()
            await interaction.response.send_message(
                "You checked in!", ephemeral=True, delete_after=5
            )
        conn.close()


class CHECKIN(commands.Cog, description="Checkin system"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        init_db()
        self.checkin.start()

    @tasks.loop(time=[START])
    async def checkin(self):
        today = datetime.datetime.now(tz=ZoneInfo("America/Los_Angeles")).strftime("%A")
        if today not in {"Tuesday", "Thursday"}:
            return

        channel = self.bot.get_channel(1356725800849772775)

        old_msg = await anext(channel.history(limit=1))
        if old_msg and old_msg.author == self.bot.user:
            # Check if the last message was sent by the bot
            await old_msg.delete()

        view = MyView()
        await channel.send(CHECKIN_MSG, view=view)

    @checkin.before_loop
    async def before_checkin(self):
        await self.bot.wait_until_ready()  # Wait until the bot is ready

    @app_commands.command(
        name="send_checkin",
        description="Manually send today's checkin message",
    )
    async def send_checkin(self, interaction: discord.Interaction):
        channel = self.bot.get_channel(1356725800849772775)

        view = MyView()

        old_msg = await anext(channel.history(limit=1))
        if old_msg and old_msg.author == self.bot.user:
            # Check if the last message was sent by the bot
            await old_msg.delete()

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


async def setup(bot: commands.Bot):
    await bot.add_cog(CHECKIN(bot))
