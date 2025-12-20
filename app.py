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
def index():
    return "🤖 Digambar GPT Online"

@app.route('/health')
def health():
    return {"status": "online", "bot": "Digambar GPT"}, 200

def run_flask():
    port = int(os.getenv('PORT', 8000))
    from waitress import serve
    serve(app, host="0.0.0.0", port=port)

# Discord bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print('=' * 60)
    print(f'🔥 DIGAMBAR GPT ONLINE: {bot.user}')
    print(f'📊 SERVERS: {len(bot.guilds)}')
    
    for guild in bot.guilds:
        print(f'   📍 {guild.name} (ID: {guild.id})')
        if guild.id == 1421640981584937063:
            print(f'      ⭐ FIXED SERVER DETECTED!')
            for channel in guild.text_channels:
                if channel.id == 1444296327704875049:
                    print(f'      🎯 FIXED CHANNEL FOUND: #{channel.name}')
    
    print('=' * 60)
    
    # Load cogs
    try:
        await bot.load_extension('cogs.ai_cog')
        print('✅ AI COG LOADED')
    except Exception as e:
        print(f'❌ AI COG ERROR: {e}')
    
    try:
        await bot.load_extension('cogs.slash_commands')
        print('✅ SLASH COMMANDS COG LOADED')
    except Exception as e:
        print(f'❌ SLASH COMMANDS ERROR: {e}')
    
    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        print(f'✅ {len(synced)} SLASH COMMANDS SYNCED:')
        for cmd in synced:
            print(f'   ➤ /{cmd.name}')
    except Exception as e:
        print(f'❌ SLASH COMMAND SYNC ERROR: {e}')
    
    print('=' * 60)
    print('🎯 BOT IS FULLY OPERATIONAL!')
    print('💡 Test commands:')
    print('   In #bot-commands: Type anything')
    print('   Elsewhere: @mention the bot')
    print('   Commands: !ping, /ping, !ask, /ask')
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
    # Log incoming messages
    if message.guild:
        print(f'📨 [{message.guild.name}] #{message.channel.name} {message.author}: {message.content[:50]}')
    
    # Process commands
    await bot.process_commands(message)

async def main():
    # Start Flask with waitress (production-ready)
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    print(f'🌐 FLASK SERVER STARTED ON PORT {os.getenv("PORT", 8000)}')
    
    # Get token
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("❌ ERROR: DISCORD_TOKEN NOT FOUND")
        return
    
    if token == "your_discord_bot_token_here":
        print("❌ ERROR: UPDATE .env WITH REAL TOKEN")
        return
    
    print('🚀 STARTING DISCORD BOT...')
    
    try:
        await bot.start(token)
    except discord.LoginFailure:
        print("❌ LOGIN FAILED: CHECK DISCORD_TOKEN")
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")

if __name__ == "__main__":
    # Set event loop policy for Render
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(main())
