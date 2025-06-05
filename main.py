import discord, json, os, asyncio, atexit
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv


# Load and save configurations
LOG_CONFIG_FILE = "log_config.json"

def load_log_config():
    try:
        with open(LOG_CONFIG_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_log_config(config):
    with open(LOG_CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

log_channels = load_log_config()

DATA_FILE = 'reaction_roles.json'

def load_reaction_roles():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_reaction_roles(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TOKEN")

# Bot intents and setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True
intents.guilds = True

bot = commands.Bot(command_prefix=".", intents=intents)
reaction_roles = load_reaction_roles()

@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.listening, name="bot-cmds"),
        status=discord.Status.idle  # Can be: online, idle, dnd, invisible
    )
    print(f"{bot.user} has launched successfully!")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"Failed to sync: {e}")


# Command list below

# Temp Role
@bot.tree.command(name="temp_role", description="Temporarily assign a role to a user")
@app_commands.describe(member="The user to give the role to", role="Role to assign", duration="Duration in seconds")
async def temp_role(interaction: discord.Interaction, member: discord.Member, role: discord.Role, duration: int):
    try:
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message("You don’t have permission to manage roles.", ephemeral=True)
            return

        await member.add_roles(role)
        await log_action(interaction.guild, f"🛡️ `{interaction.user}` assigned temporary role `{role.name}` to {member.mention} for {duration} seconds.")

        await interaction.response.send_message(f"✅ Gave {role.mention} to {member.mention} for {duration} seconds.", ephemeral=False)
        sent_msg = await interaction.original_response()

        await asyncio.sleep(duration)

        refreshed_member = await interaction.guild.fetch_member(member.id)
        if role in refreshed_member.roles:
            await refreshed_member.remove_roles(role)
            await log_action(interaction.guild, f"🛡️ `{interaction.user}` removed temporary role `{role.name}` from {member.mention} after {duration} seconds.")

            await sent_msg.edit(content=f"✅ Gave {role.mention} to {member.mention} for {duration} seconds.\n❌ Role `{role.name}` has now been removed.")
    except Exception as e:
        print(f"Error in temp_role: {e}")
        await interaction.followup.send("⚠️ Something went wrong with the temp role command.", ephemeral=True)


# Reaction Role
@bot.tree.command(name="reaction_role", description="Set up a reaction role on a message")
@app_commands.describe(message_id="The ID of the message", emoji="Emoji to react with", role="Role to assign")
async def reaction_role(interaction: discord.Interaction, message_id: str, emoji: str, role: discord.Role):
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("You don’t have permission to manage roles.", ephemeral=True)
        return

    try:
        msg = await interaction.channel.fetch_message(int(message_id))
        await msg.add_reaction(emoji)
    except Exception as e:
        await interaction.response.send_message(f"Failed to find or react to the message: {e}", ephemeral=True)
        return

    reaction_roles.setdefault(str(msg.id), {})[emoji] = role.id
    save_reaction_roles(reaction_roles)

    await interaction.response.send_message(f"✅ Reaction role set!", ephemeral=True)

# Reaction role events!
@bot.event
async def on_raw_reaction_add(payload):
    if str(payload.message_id) not in reaction_roles:
        return

    emoji = str(payload.emoji)
    role_id = reaction_roles[str(payload.message_id)].get(emoji)
    if role_id is None:
        return

    guild = bot.get_guild(payload.guild_id)
    if guild is None:
        return

    role = guild.get_role(role_id)
    if role is None:
        return

    member = guild.get_member(payload.user_id)
    if member is None or member.bot:
        return

    await member.add_roles(role)


@bot.event
async def on_raw_reaction_remove(payload):
    if str(payload.message_id) not in reaction_roles:
        return

    emoji = str(payload.emoji)
    role_id = reaction_roles[str(payload.message_id)].get(emoji)
    if role_id is None:
        return

    guild = bot.get_guild(payload.guild_id)
    if guild is None:
        return

    role = guild.get_role(role_id)
    if role is None:
        return

    member = guild.get_member(payload.user_id)
    if member is None:
        return

    await member.remove_roles(role)



# +Log bot actions+
async def log_action(guild: discord.Guild, content: str):
    channel_id = log_channels.get(str(guild.id))
    if not channel_id:
        return  # No log channel set
    channel = guild.get_channel(channel_id)
    if channel:
        await channel.send(content)


# +Set Log Channel+
@bot.tree.command(name="set_log_channel", description="Set the moderation log channel for this server.")
@app_commands.describe(channel="The channel where moderation actions will be logged.")
async def set_log_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You must be an administrator to set the log channel.", ephemeral=True)
        return

    log_channels[str(interaction.guild.id)] = channel.id
    save_log_config(log_channels)
    await interaction.response.send_message(f"✅ Log channel set to {channel.mention}.")

# +Slash command embed credit+
@bot.tree.command(name="credit", description="The Devs!")
async def credit(interaction: discord.Interaction):
    embed = discord.Embed(title="Developers", description="Ventured - *Lead* \n"
    "Aze - *Debugger* \n"
    "Lola - *QoL* \n"
    "Tea - *Programmer*", color=discord.Color.brand_green())
    embed.set_footer(text="🪲 Thank you!")
    embed.set_thumbnail(url="https://cdn3.emoji.gg/emojis/7011-active-developer-badge.png")
    await interaction.response.send_message(embed=embed, ephemeral=True)


# Run the bot
bot.run(TOKEN)
