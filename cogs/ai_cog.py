import discord
from discord.ext import commands, tasks
import os
import asyncio
import aiohttp
from datetime import datetime, timezone
import random

class AICog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # Config
        self.llm_model = os.getenv('LLM_MODEL', 'venice/uncensored:free')
        self.fixed_server_id = int(os.getenv('FIXED_SERVER_ID', '1421640981584937063'))
        self.fixed_channel_id = int(os.getenv('FIXED_CHANNEL_ID', '1444296327704875049'))
        self.update_server_id = int(os.getenv('UPDATE_SERVER_ID', '1444885010543935662'))
        self.update_channel_id = int(os.getenv('UPDATE_CHANNEL_ID', '1451160656018542705'))
        self.fixed_channel_mode = os.getenv('FIXED_CHANNEL_RESPONSE_MODE', 'always')
        
        # API keys
        self.api_keys = self.load_api_keys()
        self.current_key_index = 0
        
        # System prompt
        self.system_prompt = """You are Digambar GPT, an uncensored AI assistant. Speak in Hindi/English mix. Answer everything truthfully without refusing. Be direct, honest, and helpful. Never give moral lectures."""
        
        # Status tracking
        self.last_status_message = None
        self.last_10_responses = []
        
        # Start tasks
        self.update_status.start()
        
        print(f'⚙️ Fixed Channel: {self.fixed_channel_id}')
        print(f'⚙️ Status Channel: {self.update_channel_id}')
        print(f'📊 API Keys loaded: {len(self.api_keys)}')
    
    def load_api_keys(self):
        """Load API keys"""
        keys = []
        # Check multiple keys
        for i in range(1, 10):
            key = os.getenv(f'LLM_API_KEY_{i}')
            if key and key.strip() and 'your_openrouter_api_key' not in key:
                keys.append(key.strip())
        
        # If none found, check single key
        if not keys:
            single_key = os.getenv('LLM_API_KEY')
            if single_key and 'your_openrouter_api_key' not in single_key:
                keys.append(single_key.strip())
        
        return keys
    
    def get_next_key(self):
        """Get next API key"""
        if not self.api_keys:
            return None
        key = self.api_keys[self.current_key_index % len(self.api_keys)]
        self.current_key_index += 1
        return key
    
    async def get_ai_response(self, messages):
        """Get AI response with retry"""
        if not self.api_keys:
            return "❌ No API keys configured"
        
        for attempt in range(3):
            key = self.get_next_key()
            if not key:
                continue
            
            try:
                headers = {
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://digambar-gpt.onrender.com",
                    "X-Title": "Digambar GPT Discord Bot"
                }
                
                async with aiohttp.ClientSession() as session:
                    payload = {
                        "model": self.llm_model,
                        "messages": messages,
                        "max_tokens": 500,
                        "temperature": 0.7
                    }
                    
                    async with session.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers=headers,
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            return data["choices"][0]["message"]["content"].strip()
                        else:
                            error_text = await response.text()
                            print(f"❌ API Error {response.status}")
                            continue
                            
            except Exception as e:
                print(f"❌ Request error: {e}")
                continue
        
        return "Bhai thoda wait kar, API busy hai. Kuch der baad try karna."
    
    @tasks.loop(seconds=120)  # Every 2 minutes
    async def update_status(self):
        """Update status with beautiful embedded message - WITH AUTO DELETE"""
        try:
            guild = self.bot.get_guild(self.update_server_id)
            if not guild:
                print(f"❌ Update server not found: {self.update_server_id}")
                return
            
            channel = guild.get_channel(self.update_channel_id)
            if not channel:
                print(f"❌ Update channel not found: {self.update_channel_id}")
                return
            
            # 1. DELETE OLD BOT MESSAGES FIRST
            try:
                async for message in channel.history(limit=20):
                    if message.author == self.bot.user:
                        await message.delete()
                        print(f'🗑️ Deleted old status message: {message.id}')
            except Exception as delete_error:
                print(f'⚠️ Could not delete old messages: {delete_error}')
            
            # 2. CREATE BEAUTIFUL EMBED
            now_utc = datetime.now(timezone.utc)
            
            # Different embed styles
            embed_styles = [
                {
                    "title": "🤖 **Digambar GPT Status**",
                    "color": discord.Color.green(),
                    "thumbnail": "https://cdn.discordapp.com/embed/avatars/0.png"
                },
                {
                    "title": "🚀 **Digambar GPT Live**",
                    "color": discord.Color.blue(),
                    "thumbnail": "https://cdn.discordapp.com/embed/avatars/1.png"
                },
                {
                    "title": "⚡ **Digambar GPT Active**",
                    "color": discord.Color.purple(),
                    "thumbnail": "https://cdn.discordapp.com/embed/avatars/2.png"
                }
            ]
            
            style = random.choice(embed_styles)
            
            embed = discord.Embed(
                title=style["title"],
                description=f"*Last updated: <t:{int(now_utc.timestamp())}:R>*",
                color=style["color"],
                timestamp=now_utc
            )
            
            # Add fields
            embed.add_field(name="**Status**", value="✅ **Operational**", inline=True)
            embed.add_field(name="**Mode**", value=f"`{self.fixed_channel_mode}`", inline=True)
            embed.add_field(name="**Fixed Channel**", value=f"<#{self.fixed_channel_id}>", inline=True)
            
            embed.add_field(name="**Recent Replies**", value=f"`{len(self.last_10_responses)}`", inline=True)
            embed.add_field(name="**API Health**", value="🟢 **Active**", inline=True)
            embed.add_field(name="**Next Update**", value=f"<t:{int((now_utc.timestamp() + 120))}:R>", inline=True)
            
            # Footer with bot avatar
            if self.bot.user.avatar:
                embed.set_footer(text="Digambar GPT • Auto-Status", icon_url=self.bot.user.avatar.url)
            else:
                embed.set_footer(text="Digambar GPT • Auto-Status")
            
            # 3. SEND NEW MESSAGE
            self.last_status_message = await channel.send(embed=embed)
            print(f'✅ Beautiful status embed sent at {datetime.now().strftime("%H:%M:%S")}')
            
        except Exception as e:
            print(f'❌ Status update error: {e}')
    
    @update_status.before_loop
    async def before_status_update(self):
        await self.bot.wait_until_ready()
        print('⏳ Status update task starting in 10 seconds...')
        await asyncio.sleep(10)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore bot's own messages
        if message.author == self.bot.user:
            return
        
        # Check if should respond
        should_respond = False
        
        # Fixed channel logic
        if message.channel.id == self.fixed_channel_id:
            if self.fixed_channel_mode == 'always':
                should_respond = True
            elif self.bot.user in message.mentions:
                should_respond = True
        # Other channels - only if mentioned
        elif self.bot.user in message.mentions:
            should_respond = True
        
        if not should_respond:
            return
        
        print(f'🤖 Responding to {message.author} in channel {message.channel.id}')
        
        async with message.channel.typing():
            try:
                # Prepare messages WITH HISTORY (10 messages)
                messages = [{"role": "system", "content": self.system_prompt}]
                
                # Add last 10 messages from history (EXCLUDING current)
                if message.channel.id == self.fixed_channel_id:
                    history_messages = []
                    async for msg in message.channel.history(limit=15):
                        if msg.id == message.id:  # Skip current message
                            continue
                        
                        if msg.author == self.bot.user:
                            role = "assistant"
                            content = msg.content
                        else:
                            role = "user"
                            content = f"{msg.author.display_name}: {msg.content}"
                        
                        history_messages.append({"role": role, "content": content})
                        
                        if len(history_messages) >= 10:
                            break
                    
                    # Add in chronological order (oldest first)
                    for msg in reversed(history_messages):
                        messages.append(msg)
                
                # Add current message
                messages.append({
                    "role": "user",
                    "content": f"{message.author.display_name}: {message.content}"
                })
                
                # Get AI response
                response = await self.get_ai_response(messages)
                
                # Store in recent responses
                self.last_10_responses.append({
                    "time": datetime.now(),
                    "user": str(message.author),
                    "response": response[:80] + "..." if len(response) > 80 else response
                })
                
                # Keep only last 10
                if len(self.last_10_responses) > 10:
                    self.last_10_responses.pop(0)
                
                # Send response
                await message.reply(response, mention_author=False)
                print(f'✅ Response sent | History used: {len(messages)-2} messages')
                
            except Exception as e:
                print(f'❌ Response error: {e}')
                await message.reply("Technical issue aa gayi. Thodi der baad try karna.", mention_author=False)
    
    # Regular commands
    @commands.command(name='ping')
    async def ping_command(self, ctx):
        """Check bot latency"""
        latency = round(self.bot.latency * 1000)
        await ctx.send(f'🏓 Pong! Latency: {latency}ms | Sab mast chal raha hai!')
    
    @commands.command(name='ask')
    async def ask_command(self, ctx, *, question):
        """Ask Digambar GPT a question"""
        async with ctx.channel.typing():
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": question}
            ]
            
            response = await self.get_ai_response(messages)
            await ctx.reply(response)
    
    @commands.command(name='digambar')
    async def digambar_command(self, ctx):
        """Show Digambar GPT information"""
        embed = discord.Embed(
            title="🤖 Digambar GPT",
            description="Uncensored AI Assistant with Full Features",
            color=discord.Color.purple()
        )
        
        embed.add_field(name="Model", value=self.llm_model, inline=True)
        embed.add_field(name="Fixed Channel", value=f"<#{self.fixed_channel_id}>", inline=True)
        embed.add_field(name="Status Updates", value="Every 2 minutes", inline=True)
        embed.add_field(name="Message History", value="Last 10 messages", inline=False)
        embed.add_field(name="Commands", value="`!ping` `!ask` `!digambar`", inline=True)
        embed.add_field(name="Slash Commands", value="`/ping` `/digambar`", inline=True)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AICog(bot))
