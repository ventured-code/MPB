import discord
from discord.ext import commands
from discord import app_commands
from utils.file_utils import load_log_config, save_log_config

log_channels = load_log_config()

class LogChannel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="set_log_channel", description="Set the log channel.")
    @app_commands.describe(channel="Channel to log moderation actions")
    async def set_log_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You need to be an administrator to use this.", ephemeral=True)
            return

        log_channels[str(interaction.guild.id)] = channel.id
        save_log_config(log_channels)
        await interaction.response.send_message(f"✅ Log channel set to {channel.mention}.")

async def setup(bot):
    await bot.add_cog(LogChannel(bot))
