import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from flask import Flask
from threading import Thread
import asyncio

# Load environment variables
load_dotenv()

# Flask app for keep-alive
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Digambar GPT - Uncensored AI Assistant! 🔥"

@app.route('/health')
def health():
    return {"status": "healthy", "bot": "Digambar GPT"}, 200

@app.route('/api-status')
def api_status():
    """Check API key status"""
    try:
        from cogs.api_manager import api_manager
        stats = api_manager.get_stats()
        return {
            "status": "healthy" if stats['available_keys'] > 0 else "warning",
            "bot": "Digambar GPT",
            "api_keys": {
                "total": stats['total_keys'],
                "available": stats['available_keys'],
                "failed": stats['failed_keys']
            },
            "message": "All good!" if stats['available_keys'] > 0 else "Some issue!"
        }
    except:
        return {"status": "error", "bot": "Digambar GPT", "message": "API manager not loaded"}, 500

def keep_alive():
    """Start Flask server in a separate thread"""
    port = int(os.getenv('PORT', 8000))
    thread = Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': port, 'debug': False})
    thread.daemon = True
    thread.start()
    print(f"✅ Flask keep-alive server started on port {port}")

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'✅ Digambar GPT logged in as {bot.user} (ID: {bot.user.id})')
    print('🔥 Digambar GPT ready to serve!')
    print('------')
    
    # Load all cogs
    cogs_to_load = ['cogs.ai_cog', 'cogs.slash_commands']
    
    for cog in cogs_to_load:
        try:
            await bot.load_extension(cog)
            print(f'✅ {cog} loaded successfully')
        except Exception as e:
            print(f'❌ Failed to load {cog}: {e}')
    
    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash command(s):")
        for cmd in synced:
            print(f"   - /{cmd.name}")
    except Exception as e:
        print(f"❌ Failed to sync slash commands: {e}")
    
    # Show config
    mode = os.getenv('FIXED_CHANNEL_RESPONSE_MODE', 'always')
    print(f"✅ Fixed channel response mode: {mode}")
    
    print('✅ Digambar GPT ready with all features!')
    
    # Set status
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.listening, 
        name="/ask | Digambar GPT"
    ))

@bot.event
async def on_message(message):
    # Don't process commands if message starts with /
    if message.content.startswith('/'):
        return
    
    # Process regular commands
    await bot.process_commands(message)

async def run_bot():
    """Run the Discord bot"""
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("❌ ERROR: DISCORD_TOKEN not found in .env file!")
        return
    
    print("🚀 Starting Digambar GPT...")
    print("🎯 Features: Uncensored | Multi-API | Slash Commands | Configurable")
    
    await bot.start(token)

def main():
    """Main function to start both Flask and Discord bot"""
    # Start Flask server first (for Render)
    print("🌐 Starting Flask keep-alive server...")
    keep_alive()
    
    # Run Discord bot
    print("🤖 Starting Digambar GPT...")
    
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        print("\n👋 Digambar GPT stopped by user")
    except Exception as e:
        print(f"❌ Error running bot: {e}")

if __name__ == "__main__":
    main()
