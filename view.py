import discord
import os
import datetime
from zoneinfo import ZoneInfo
import sqlite3

SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, "checkin.db")

CHECKIN_DAYS = {"Tuesday", "Thursday"}
REMINDER_DAYS = {"Monday", "Wednesday"}
CHECKIN_CHANNEL_ID = 1356725800849772775
REMINDER_CHANNEL_IDS = [1356725800849772775, 1358014326031781939]
CHECKIN_MSG = "# Good Morning <@&1356726753485127913>!\n It's time to check in :D"
REMINDER_MSG = (
    "# Pre-Lecture Preparation <@&{}>\nDon't forget "
    "to finish **{}**! Details on GradeScope.\n"
)

SERVER_TO_GS = {
    1219779798310588599: 1011553,  # 161
    1352534413467979786: 1009804,  # 162
}

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


async def delete_last_bot_message(channel: discord.TextChannel, match_text=None):
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
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Check In", custom_id="check_in", style=discord.ButtonStyle.primary
    )
    async def handle_click(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        now, today = await get_today_info()
        curr_day = now.strftime("%m/%d")

        if (
            today not in CHECKIN_DAYS
            or now.time() > CUTOFF.replace(tzinfo=None)
            or now.time() < START.replace(tzinfo=None)
        ):
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


#
