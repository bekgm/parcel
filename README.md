# Parcel Tracker Telegram Bot

A Telegram bot that tracks parcels in real-time by scraping tracking websites. No API keys needed for tracking services!

## Features

- **Real-time Tracking** - Get parcel status instantly
- **Multiple Carriers** - DHL, FedEx, UPS, China Post, and more
- **Web Scraping** - Uses 17track.net and parcelsapp.com APIs
- **Error Handling** - Graceful handling of missing or invalid packages
- **Async/Await** - Fully async with python-telegram-bot v20+
- **Environment Variables** - Secure token management
- **Render Ready** - Deploy in minutes using Procfile

## Installation

### Prerequisites
- Python 3.10+
- Telegram Bot Token (from BotFather)

### Local Setup

1. **Clone or download the project**
```bash
cd parcel
```

2. **Create a Python virtual environment**
```bash
python -m venv venv
```

3. **Activate the virtual environment**

Windows:
```bash
venv\Scripts\activate
```

macOS/Linux:
```bash
source venv/bin/activate
```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

5. **Create `.env` file** (copy from `.env.example`)
```bash
cp .env.example .env
```

6. **Add your bot token to `.env`**
```
TELEGRAM_BOT_TOKEN=your_token_from_botfather
```

## Getting Your Bot Token

1. Open Telegram and search for **@BotFather**
2. Send `/start` command
3. Send `/newbot` to create a new bot
4. Follow the prompts:
   - Choose a name (e.g., "My Parcel Tracker")
   - Choose a username (e.g., "my_parcel_tracker_bot")
5. BotFather will give you a token, copy it to `.env`

## Running the Bot

```bash
python bot.py
```

You should see output like:
```
INFO:__main__:Starting Parcel Tracker Bot...
```

## How to Use

### In Telegram

1. Search for your bot by username
2. Send `/start` to see welcome message
3. Send any tracking number (e.g., `RB123456789CN`)
4. Get instant tracking info with status, location, and dates

### Example Interaction

```
User: RB123456789CN

Bot: Tracking Number: RB123456789CN
Carrier: China Post
Status: In transit
Location: Shanghai
Date: 2024-05-01 14:30
Last Update: Arrived at sorting center
```

## Bot Commands

| Command | Description |
|---------|------------|
| `/start` | Show welcome message |
| `/help` | Display help and usage tips |
| Send tracking # | Track a parcel |

## Code Structure

### `bot.py`

**ParcelTracker Class:**
- `validate_tracking_number()` - Validates tracking number format
- `track_parcel()` - Primary scraping using 17track.net
- `track_parcel_parcelsapp()` - Fallback scraping using parcelsapp.com

**Bot Handlers:**
- `start()` - /start command handler
- `handle_tracking_number()` - Processes tracking requests
- `help_command()` - /help command handler
- `error_handler()` - Global error handler
- `main()` - Bot initialization and polling

## Scraping Details

The bot uses two approaches:

### 1. **17track.net API** (Primary)
- Uses undocumented JSON API endpoint
- Supports 1000+ carriers worldwide
- Provides detailed tracking information

### 2. **parcelsapp.com** (Fallback)
- HTML parsing with BeautifulSoup
- Works as backup if primary fails
- Handles edge cases

### Error Handling
- **Timeout errors** - Waits 10 seconds before giving up
- **Network errors** - Graceful fallback to alternative service
- **Parsing errors** - Returns user-friendly error message
- **Not found** - Special message suggesting verification

## Deployment on Render

### Step-by-Step Guide

1. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub or email

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository (or use public repo)

3. **Configure Service**
   - **Name**: `parcel-tracker-bot`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py`

4. **Add Environment Variables**
   - Click "Environment"
   - Add key: `TELEGRAM_BOT_TOKEN`
   - Paste your bot token as value

5. **Change Service Type (Important!)**
   - Click "Settings"
   - Scroll to "Service"
   - Change from "Web Service" to **"Background Worker"**
   - Save changes

6. **Deploy**
   - Click "Deploy"
   - Monitor logs for "Starting Parcel Tracker Bot..."

### Why Background Worker?

The bot uses `polling()` which keeps a persistent connection. Background Workers are ideal for this, while Web Services are for HTTP servers.

### Alternative: Using Webhooks

For production, consider using webhooks instead of polling:

```python
# Replace application.run_polling() with:
application.run_webhook(
    listen="0.0.0.0",
    port=PORT,
    url_path='/telegram',
    webhook_url=f"https://your-app.onrender.com/telegram"
)
```

## Troubleshooting

### Bot not responding
- Check if `TELEGRAM_BOT_TOKEN` is set correctly
- Verify token with BotFather
- Check internet connection
- Look for errors in console

### "Tracking number not found"
- Verify the tracking number is correct
- Some carriers take 24+ hours to show in system
- Try removing spaces or special characters

### Website scraping fails
- Websites may update their HTML structure
- Update selectors in `track_parcel_parcelsapp()` method
- Check website's robots.txt and terms of service

### Rate limiting on Render
- Free tier Render may have limitations
- Consider upgrading or adding delays between requests

## API Sources

- **17track.net**: Supports 1000+ carriers, free API
- **parcelsapp.com**: Multi-carrier with HTML parsing

## Security Notes

- **Never** hardcode your bot token
- Always use environment variables
- Keep `.env` file out of version control
- Don't share your bot token publicly

## Requirements

- `python-telegram-bot==20.6` - Official Telegram Bot API wrapper
- `requests==2.31.0` - HTTP library for web scraping
- `beautifulsoup4==4.12.2` - HTML/XML parsing
- `python-dotenv==1.0.0` - Environment variable management

## Contributing

Feel free to:
- Add more scraping methods
- Improve parsing logic
- Add new carriers
- Fix bugs

## License

MIT License - Feel free to use and modify!

## Support

For issues with:
- **Telegram Bot API**: See [python-telegram-bot docs](https://docs.python-telegram-bot.org/)
- **Render Deployment**: Check [Render docs](https://render.com/docs)
- **Web Scraping**: Review [BeautifulSoup docs](https://www.crummy.com/software/BeautifulSoup/)

## Legal Notice

- Respect website terms of service when scraping
- Use appropriate User-Agent headers
- Don't overload servers with requests
- Some websites may block bots - this is normal

---

**Happy tracking!**
