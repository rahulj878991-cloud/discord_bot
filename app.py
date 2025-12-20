import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from flask import Flask
from threading import Thread
import asyncio
import sys

# Load environment
load_dotenv()

# Flask keep-alive
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Digambar GPT Online"

@app.route('/health')
def health():
    return {"status": "online", "bot": "Digambar GPT"}, 200

def run_flask():
    port = int(os.getenv('PORT', 8000))
    from waitress import serve
    serve(app, host="0.0.0.0", port=port)

# Discord bot - CORRECT INTENTS
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print('=' * 60)
    print(f'🔥 DIGAMBAR GPT: {bot.user}')
    print(f'📊 SERVERS: {len(bot.guilds)}')
    
    for guild in bot.guilds:
        print(f'   📍 {guild.name} (ID: {guild.id})')
    
    print('=' * 30)
    
    # Load cogs WITH ERROR HANDLING
    try:
        await bot.load_extension('cogs.ai_cog')
        print('✅ AI Cog loaded')
    except Exception as e:
        print(f'❌ AI Cog error: {e}')
    
    try:
        await bot.load_extension('cogs.slash_commands')
        print('✅ Slash Commands loaded')
    except Exception as e:
        print(f'❌ Slash Commands error: {e}')
    
    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        print(f'✅ {len(synced)} slash commands synced')
        for cmd in synced:
            print(f'   ➤ /{cmd.name}')
    except Exception as e:
        print(f'⚠️ Slash command sync error: {e}')
    
    print('=' * 30)
    print('🎯 BOT IS FULLY OPERATIONAL!')
    print('💡 Commands: /ping, /digambar, !ping, !digambar')
    print('💡 Fixed Channel: #bot-commands')
    print('💡 Status Updates: Every 2 minutes')
    print('=' * 60)
    
    # Set status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.playing,
            name="/ask | Digambar GPT"
        )
    )

@bot.event
async def on_message(message):
    # Process commands
    await bot.process_commands(message)

async def main():
    # Start Flask
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    print(f'🌐 Flask server started on port {os.getenv("PORT", 8000)}')
    
    # Run bot
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("❌ ERROR: DISCORD_TOKEN not found")
        return
    
    print('🚀 Starting Discord bot...')
    await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
