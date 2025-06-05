import discord, os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True
intents.guilds = True

bot = commands.Bot(command_prefix=".", intents=intents)

@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.listening, name="bot-cmds"),
        status=discord.Status.idle
    )
    print(f"{bot.user} has launched successfully!")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"Failed to sync: {e}")

# Load cogs
initial_extensions = [
    "cogs.temp_role",
    "cogs.reaction_role",
    "cogs.log_channel",
    "cogs.credit"
]

for ext in initial_extensions:
    bot.load_extension(ext)

bot.run(TOKEN)
