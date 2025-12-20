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
        await interaction.response.send_message(f'🏓 Pong! Latency: {latency}ms')
    
    @app_commands.command(name="digambar", description="Show Digambar GPT information")
    async def digambar_info(self, interaction: discord.Interaction):
        """Slash info command"""
        embed = discord.Embed(
            title="🤖 Digambar GPT",
            description="Uncensored AI Assistant",
            color=discord.Color.purple()
        )
        
        embed.add_field(name="Status", value="✅ Online and Working", inline=True)
        embed.add_field(name="Features", value="Message History\nAuto Updates\nMulti-API", inline=True)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="ask", description="Ask Digambar GPT anything")
    @app_commands.describe(question="Your question")
    async def ask_slash(self, interaction: discord.Interaction, question: str):
        """Slash ask command"""
        await interaction.response.defer(thinking=True)
        
        # Get AI cog to handle the request
        ai_cog = self.bot.get_cog('AICog')
        if ai_cog:
            messages = [
                {"role": "system", "content": ai_cog.system_prompt},
                {"role": "user", "content": question}
            ]
            
            response = await ai_cog.get_ai_response(messages)
            await interaction.followup.send(response)
        else:
            await interaction.followup.send("AI cog not loaded. Try again.")

async def setup(bot):
    await bot.add_cog(SlashCommands(bot))
