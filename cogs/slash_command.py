import discord
from discord import app_commands
from discord.ext import commands

class SlashCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="ping", description="Check bot latency")
    async def ping(self, interaction: discord.Interaction):
        """Slash ping command"""
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(f'🏓 Pong! {latency}ms')
    
    @app_commands.command(name="digambar", description="Show bot information")
    async def digambar_info(self, interaction: discord.Interaction):
        """Slash info command"""
        embed = discord.Embed(
            title="🤖 Digambar GPT",
            description="Uncensored AI Assistant",
            color=discord.Color.purple()
        )
        
        embed.add_field(name="Features", value="✅ Message history\n✅ Auto updates\n✅ Multi-API", inline=False)
        embed.add_field(name="Commands", value="/ping, /digambar", inline=True)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(SlashCommands(bot))
