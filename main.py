import os
import discord
import keep_alive
from discord.ext import commands
from dotenv import load_dotenv
from checkin import MyView

load_dotenv()
keep_alive.keep_alive()

description = "A UCI Discord Bot"

TOKEN = os.getenv("DISCORD_TOKEN")

startup_extensions = [
    "threadgrabber",
    "eventhandlers",
    "admin",
    "owner",
    "checkin",
    "groups",
]
bot = commands.Bot(
    command_prefix="*", description=description, intents=discord.Intents.all()
)


@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening, name="your needs :)"
        )
    )
    bot.add_view(MyView())
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)
    print(f"{bot.user.name} has connected to Discord!")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send(
            "You do not have the correct role for this command, or you are in the wrong server."
        )


@bot.event
async def setup_hook():
    for extension in startup_extensions:
        try:
            await bot.load_extension(extension)
        except Exception as e:
            exc = "{}: {}".format(type(e).__name__, e)
            print("Failed to load extension {}\n{}".format(extension, exc))


if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
