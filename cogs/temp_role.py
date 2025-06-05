import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from utils.log_utils import log_action

class TempRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="temp_role", description="Temporarily assign a role to a user")
    @app_commands.describe(member="User to assign the role to", role="Role to assign", duration="Duration in seconds")
    async def temp_role(self, interaction: discord.Interaction, member: discord.Member, role: discord.Role, duration: int):
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message("You don’t have permission to manage roles.", ephemeral=True)
            return

        await member.add_roles(role)
        await log_action(interaction.guild, f"🛡️ `{interaction.user}` assigned temporary role `{role.name}` to {member.mention} for {duration} seconds.")
        await interaction.response.send_message(f"✅ Gave {role.mention} to {member.mention} for {duration} seconds.")

        await asyncio.sleep(duration)

        refreshed_member = await interaction.guild.fetch_member(member.id)
        if role in refreshed_member.roles:
            await refreshed_member.remove_roles(role)
            await log_action(interaction.guild, f"🛡️ `{interaction.user}` removed temporary role `{role.name}` from {member.mention} after {duration} seconds.")

async def setup(bot):
    await bot.add_cog(TempRole(bot))
