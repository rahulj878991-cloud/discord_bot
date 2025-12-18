# Digambar GPT - Discord Bot

An uncensored AI Discord bot using OpenRouter API with multiple API key failover support.

## Features
- 🤖 Digambar GPT personality
- 🔄 Multiple API key failover system
- ⚡ Slash commands support
- 🎯 Configurable response modes
- 🔥 Uncensored responses
- 📊 API usage statistics
- ⏰ Automatic updates every 5 minutes

## Setup

### 1. Clone and Install
```bash
git clone <repo-url>
cd discord_bot
pip install -r requirements.txt
```

2. Configure Environment

Edit .env file:

```env
DISCORD_TOKEN=your_discord_token
LLM_API_KEY_1=your_openrouter_key_1
LLM_API_KEY_2=your_openrouter_key_2
# ... add more keys
```

3. Run the Bot

```bash
python app.py
```

Bot Commands

Slash Commands

· /ping - Check bot latency
· /ask <question> - Ask Digambar GPT anything
· /stats - Show API key statistics
· /digambar - Show bot information
· /set_channel <mode> - Set response mode for current channel (Admin only)

Regular Commands

· !ping - Check latency
· !ask <question> - Ask question
· !api_stats - Show API stats
· !digambar - Bot info
· !setmode <mode> - Set response mode (Admin only)

Response Modes

Fixed Channel (configured in .env)

· FIXED_CHANNEL_RESPONSE_MODE=always - Respond to all messages
· FIXED_CHANNEL_RESPONSE_MODE=mention - Respond only when mentioned

Other Channels

· Use /set_channel command to configure per channel

Multi-API System

Bot automatically rotates between multiple API keys:

· Rate limit handling
· Automatic failover
· Key cooldown (60 seconds)
· Usage statistics

Deployment on Render

1. Create new Web Service
2. Build Command: pip install -r requirements.txt
3. Start Command: python app.py
4. Add all environment variables
5. Set PORT: 8000

API Key Setup

1. Sign up on OpenRouter
2. Get API keys
3. Add to .env as LLM_API_KEY_1, LLM_API_KEY_2, etc.
4. More keys = better failover!
