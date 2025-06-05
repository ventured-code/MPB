import discord
from discord.ext import commands
from discord import app_commands

class Credit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="credit", description="Bot developer credits")
    async def credit(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Developers",
            description="Ventured - *Lead* \nAze - *Debugger* \nLola - *QoL* \nTea - *Programmer*",
            color=discord.Color.brand_green()
        )
        embed.set_footer(text="🪲 Thank you!")
        embed.set_thumbnail(url="https://cdn3.emoji.gg/emojis/7011-active-developer-badge.png")
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Credit(bot))
