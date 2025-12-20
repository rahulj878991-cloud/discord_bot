import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from flask import Flask
from threading import Thread
import asyncio

load_dotenv()

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

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print('=' * 60)
    print(f'🔥 DIGAMBAR GPT: {bot.user}')
    print(f'📊 SERVERS: {len(bot.guilds)}')
    
    for guild in bot.guilds:
        print(f'   📍 {guild.name} ({guild.id})')
    
    # Load cogs
    await bot.load_extension('cogs.ai_cog')
    await bot.load_extension('cogs.slash_commands')
    print('✅ All cogs loaded')
    
    # Sync commands
    try:
        synced = await bot.tree.sync()
        print(f'✅ {len(synced)} slash commands synced')
    except Exception as e:
        print(f'⚠️ Sync error: {e}')
    
    print('=' * 60)
    print('🎯 BOT READY! Features:')
    print('   ✅ Message history (10 messages)')
    print('   ✅ Auto status updates every 2 min')
    print('   ✅ Beautiful embedded status')
    print('   ✅ Multi-API failover')
    print('=' * 60)
    
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.playing,
            name="/ask | Digambar GPT"
        )
    )

async def main():
    # Start Flask
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    print(f'🌐 Flask server started')
    
    # Run bot
    token = os.getenv('DISCORD_TOKEN')
    await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
