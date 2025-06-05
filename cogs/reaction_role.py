import discord
from discord.ext import commands
from discord import app_commands
from utils.file_utils import load_reaction_roles, save_reaction_roles

reaction_roles = load_reaction_roles()

class ReactionRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.add_listener(self.on_raw_reaction_add)
        self.bot.add_listener(self.on_raw_reaction_remove)

    @app_commands.command(name="reaction_role", description="Set up a reaction role")
    @app_commands.describe(message_id="Message ID", emoji="Emoji", role="Role to assign")
    async def reaction_role(self, interaction: discord.Interaction, message_id: str, emoji: str, role: discord.Role):
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message("Permission denied.", ephemeral=True)
            return
        try:
            msg = await interaction.channel.fetch_message(int(message_id))
            await msg.add_reaction(emoji)
        except Exception as e:
            await interaction.response.send_message(f"Error: {e}", ephemeral=True)
            return

        reaction_roles.setdefault(str(msg.id), {})[emoji] = role.id
        save_reaction_roles(reaction_roles)
        await interaction.response.send_message("✅ Reaction role set!", ephemeral=True)

    async def on_raw_reaction_add(self, payload):
        if str(payload.message_id) not in reaction_roles:
            return
        emoji = str(payload.emoji)
        role_id = reaction_roles[str(payload.message_id)].get(emoji)
        if not role_id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        role = guild.get_role(role_id)

        if member and not member.bot and role:
            await member.add_roles(role)

    async def on_raw_reaction_remove(self, payload):
        if str(payload.message_id) not in reaction_roles:
            return
        emoji = str(payload.emoji)
        role_id = reaction_roles[str(payload.message_id)].get(emoji)
        if not role_id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        role = guild.get_role(role_id)

        if member and role:
            await member.remove_roles(role)

async def setup(bot):
    await bot.add_cog(ReactionRole(bot))
