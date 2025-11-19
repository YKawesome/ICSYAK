import os

from discord import app_commands
from discord.ext import commands, tasks
from dotenv import load_dotenv
from gradescope import Gradescope, StudentAssignment, Role  # type: ignore
from datetime import datetime, time
from dateutil.parser import parse
from zoneinfo import ZoneInfo

load_dotenv()
GS_USERNAME = os.getenv("GS_USERNAME")
GS_PASSWORD = os.getenv("GS_PASSWORD")

COURSE_MAPPINGS = {
    "cs141": {
        "course_id": 1092565,
        "channel_id": 1440164100385804358,
        "role_id": 1440164599750987866,
    },
    "cs166": {
        "course_id": 1148556,
        "channel_id": 1440169765137027233,
        "role_id": 1440169840601075732,
    }
}

REMINDER_TIME = time(
    hour=21, minute=0, second=0, tzinfo=ZoneInfo("America/Los_Angeles")
)


class REMINDERS(commands.Cog, description="Reminders for Gradescope Assignments"):
    def __init__(self, bot):
        self.bot = bot
        self.gs = Gradescope(GS_USERNAME, GS_PASSWORD)
        self.send_reminders.start()

    @tasks.loop(time=[REMINDER_TIME])
    async def send_reminders(self):
        print("Sending assignment reminders...")
        courses = self.gs.get_courses(role=Role.STUDENT, as_dict=True)
        for course_name, info in COURSE_MAPPINGS.items():
            course = courses.get(info["course_id"])
            if not course:
                continue

            assignments = self.gs.get_assignments_as_student(course)
            due_tonight = self.assns_due_tonight(assignments)

            print(due_tonight)

            if not due_tonight:
                continue

            msg = f"# <@&{info.get("role_id")}> ASSIGNMENTS DUE TONIGHT\n"
            for assn in due_tonight:
                dt = datetime.strptime(assn.due_date, "%Y-%m-%d %H:%M:%S %z")
                formatted_time = dt.strftime("%-I:%M%p")
                msg += f"- **{assn.title}** due at {formatted_time}\n"

            channel = self.bot.get_channel(info["channel_id"])
            if channel:
                await channel.send(msg)

    @app_commands.default_permissions(administrator=True)
    @app_commands.command(
        name="send_reminder", description="Test sending assignment reminders"
    )
    async def send_reminder(self, interaction):
        await self.send_reminders()

    @staticmethod
    def assns_due_tonight(assns: list[StudentAssignment]) -> list[StudentAssignment]:
        due_tonight = []
        now = datetime.now()

        for assn in assns:
            try:
                due_date = parse(assn.due_date)
                if due_date.date() == now.date() and due_date.time() <= time(
                    23, 59, 59
                ):
                    due_tonight.append(assn)
            except Exception:
                continue
        return due_tonight



async def setup(bot):
    await bot.add_cog(REMINDERS(bot))
