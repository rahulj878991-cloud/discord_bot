import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from flask import Flask
from threading import Thread
import asyncio

# Load environment
load_dotenv()

# Flask keep-alive
app = Flask(__name__)

@app.route('/')
def index():
    return "🤖 Digambar GPT Online"

@app.route('/health')
def health():
    return {"status": "online", "bot": "Digambar GPT"}, 200

def run_flask():
    port = int(os.getenv('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# Discord bot with ALL intents
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print('=' * 50)
    print(f'🔥 Digambar GPT Logged In: {bot.user}')
    print(f'📊 Connected to {len(bot.guilds)} servers:')
    
    for guild in bot.guilds:
        print(f'   - {guild.name} (ID: {guild.id})')
    
    print('=' * 50)
    
    # Load cogs
    cogs_loaded = 0
    try:
        await bot.load_extension('cogs.ai_cog')
        cogs_loaded += 1
        print('✅ AI Cog loaded')
    except Exception as e:
        print(f'❌ AI Cog error: {e}')
    
    try:
        await bot.load_extension('cogs.slash_commands')
        cogs_loaded += 1
        print('✅ Slash Commands Cog loaded')
    except Exception as e:
        print(f'❌ Slash Commands error: {e}')
    
    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        print(f'✅ {len(synced)} slash commands synced')
    except Exception as e:
        print(f'❌ Slash command sync error: {e}')
    
    print('=' * 50)
    print('🎯 Bot is READY!')
    print('💡 Test with: /ping or !ping')
    print('=' * 50)
    
    # Set bot status
    try:
        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.playing,
                name="/ask | Digambar GPT"
            )
        )
        print('✅ Status set successfully')
    except Exception as e:
        print(f'❌ Status error: {e}')

@bot.event
async def on_message(message):
    # Don't respond to self
    if message.author == bot.user:
        return
    
    # Process commands
    await bot.process_commands(message)

async def main():
    # Start Flask in background thread
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    print(f'🌐 Flask server started on port {os.getenv("PORT", 8000)}')
    
    # Get token and run bot
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("❌ ERROR: DISCORD_TOKEN missing in .env")
        return
    
    print('🚀 Starting Discord bot...')
    await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
