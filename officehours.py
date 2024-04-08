import discord
from discord import app_commands
from discord.ext import commands, tasks
from datetime import datetime
import pytz


def make_date_string() -> str:
    dt = datetime.now(pytz.timezone('US/Pacific'))
    day = dt.date().strftime("%A")
    hour = dt.time().strftime("%I_%p")
    string = f"{hour}_{day}"
    return string


class OFFICEHOURS(commands.Cog, description='Pings for LA Office Hours'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


async def setup(bot: commands.Bot):
    await bot.add_cog(OFFICEHOURS(bot))


print(make_date_string())