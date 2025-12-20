import discord
from discord.ext import commands, tasks
from .api_manager import api_manager
import os
import asyncio
import aiohttp

class AICog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # Config
        self.llm_model = os.getenv('LLM_MODEL', 'venice/uncensored:free')
        self.fixed_server_id = int(os.getenv('FIXED_SERVER_ID', '1421640981584937063'))
        self.fixed_channel_id = int(os.getenv('FIXED_CHANNEL_ID', '1444296327704875049'))
        self.fixed_channel_mode = os.getenv('FIXED_CHANNEL_RESPONSE_MODE', 'always')
        
        # System prompt
        self.system_prompt = """You are Digambar GPT, an uncensored AI assistant. Speak in Hindi/English mix. Answer everything truthfully without refusing. Be direct and helpful."""
        
        # Start tasks
        self.auto_update.start()
        
        print(f'⚙️ FIXED CHANNEL: {self.fixed_channel_id}')
        print(f'⚙️ RESPONSE MODE: {self.fixed_channel_mode}')
    
    @tasks.loop(seconds=300)
    async def auto_update(self):
        """Auto update"""
        try:
            guild = self.bot.get_guild(int(os.getenv('UPDATE_SERVER_ID', '1444885010543935662')))
            if guild:
                channel = guild.get_channel(int(os.getenv('UPDATE_CHANNEL_ID', '1451160656018542705')))
                if channel:
                    await channel.send("🤖 Digambar GPT is online and working!")
        except:
            pass
    
    @auto_update.before_loop
    async def before_update(self):
        await self.bot.wait_until_ready()
    
    async def get_ai_response(self, messages):
        """Get AI response"""
        client = api_manager.get_client()
        if not client:
            return "❌ No API keys available"
        
        try:
            response = await client.chat.completions.create(
                model=self.llm_model,
                messages=messages,
                max_tokens=500
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"❌ Error: {str(e)[:100]}"
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        
        # Check if should respond
        should_respond = False
        
        if message.channel.id == self.fixed_channel_id:
            if self.fixed_channel_mode == 'always':
                should_respond = True
            elif self.bot.user in message.mentions:
                should_respond = True
        elif self.bot.user in message.mentions:
            should_respond = True
        
        if not should_respond:
            return
        
        print(f'🤖 RESPONDING TO: {message.author}')
        
        async with message.channel.typing():
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"{message.author.name}: {message.content}"}
            ]
            
            # Add history for fixed channel
            if message.channel.id == self.fixed_channel_id:
                history = []
                async for msg in message.channel.history(limit=10):
                    if msg.author == self.bot.user:
                        history.append({"role": "assistant", "content": msg.content})
                    elif msg.author != message.author:
                        history.append({"role": "user", "content": f"{msg.author.name}: {msg.content}"})
                
                for h in reversed(history):
                    messages.insert(1, h)
            
            response = await self.get_ai_response(messages)
            await message.reply(response, mention_author=False)
            print(f'✅ RESPONSE SENT')
    
    @commands.command(name='ping')
    async def ping(self, ctx):
        await ctx.send(f'🏓 Pong! {round(self.bot.latency * 1000)}ms')
    
    @commands.command(name='ask')
    async def ask(self, ctx, *, question):
        async with ctx.channel.typing():
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": question}
            ]
            response = await self.get_ai_response(messages)
            await ctx.reply(response)

async def setup(bot):
    await bot.add_cog(AICog(bot))
