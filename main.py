import discord, os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

# Bot intents enable in Dev Portal.
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True
intents.guilds = True

# Prefix incase of non-slash commands.
bot = commands.Bot(command_prefix=".", intents=intents)

# Cog load list, add as necessary for commands.
initial_extensions = [
    "cogs.temp_role",
    "cogs.reaction_role",
    "cogs.log_channel",
    "cogs.credit"
]

async def load_extensions():
    for ext in initial_extensions:
        try:
            await bot.load_extension(ext)
            print(f"✅ Loaded extension: {ext}")
        except Exception as e:
            print(f"❌ Failed to load extension {ext}: {e}")

@bot.event
async def on_ready():
    await load_extensions()
    print(f"{bot.user} has launched successfully!")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"❌ Failed to sync: {e}")

# Bot run event, make it online.
bot.run(TOKEN)
