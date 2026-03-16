#!/usr/bin/env python3
"""
Telegram Parcel Tracking Bot
Tracks parcels by scraping tracking websites
"""

import os
import sys
import asyncio
import logging
import re
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

# Third-party imports
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get bot token from environment variable
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError('TELEGRAM_BOT_TOKEN environment variable not set')


class ParcelTracker:
    """
    Handles web scraping for parcel tracking information.
    Supports multiple tracking websites.
    """

    # Headers to mimic a real browser request
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    @staticmethod
    def validate_tracking_number(tracking_number: str) -> bool:
        """
        Validate tracking number format.
        Most tracking numbers are 9-20 alphanumeric characters.
        """
        # Remove whitespace and convert to uppercase
        tracking_number = tracking_number.strip().upper()
        # Check if it matches typical tracking number format
        return bool(re.match(r'^[A-Z0-9]{9,20}$', tracking_number))

    @classmethod
    async def track_parcel(cls, tracking_number: str) -> Optional[dict]:
        """
        Scrape tracking information from 17track.net
        
        Args:
            tracking_number: The parcel tracking number
            
        Returns:
            Dictionary with tracking info or None if not found
        """
        tracking_number = tracking_number.strip().upper()

        try:
            # Example using 17track.net API
            # 17track.net has an undocumented API that returns JSON
            url = 'https://api.17track.net/track/simplejson'
            
            payload = {
                'number': tracking_number,
                'type': 0  # Auto-detect carrier
            }

            # Send request with timeout
            response = requests.post(
                url,
                json=payload,
                headers=cls.HEADERS,
                timeout=10
            )
            response.raise_for_status()

            data = response.json()

            # Check if tracking number was found
            if not data or data.get('ret') != 0:
                return None

            # Extract tracking data
            track_info = data.get('data', {})
            events = track_info.get('event', [])

            if not events:
                return None

            # Get the latest event (most recent)
            latest_event = events[0]

            # Parse location and status
            location = latest_event.get('c', 'Unknown')
            status_code = latest_event.get('sta', '')
            event_desc = latest_event.get('html', 'Unknown event')
            
            # Convert timestamp
            timestamp = latest_event.get('time', '')
            if timestamp:
                try:
                    event_date = datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M')
                except (ValueError, TypeError):
                    event_date = timestamp
            else:
                event_date = 'Unknown'

            # Map status codes to readable status
            status_map = {
                '0': 'Picked up',
                '1': 'In transit',
                '2': 'Out for delivery',
                '3': 'Delivered',
                '4': 'Undeliverable',
                '5': 'Not found',
                '10': 'Customs clearance',
            }

            status = status_map.get(status_code, f'Status: {status_code}')

            return {
                'tracking_number': tracking_number,
                'status': status,
                'last_event': event_desc,
                'location': location,
                'date': event_date,
                'carrier': track_info.get('carrier', 'Unknown Carrier'),
            }

        except requests.exceptions.Timeout:
            logger.error(f'Timeout tracking {tracking_number}')
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f'Connection error tracking {tracking_number}')
            return None
        except ValueError as e:
            logger.error(f'JSON decode error: {e}')
            return None
        except Exception as e:
            logger.error(f'Error tracking {tracking_number}: {e}')
            return None

    @classmethod
    async def track_parcel_parcelsapp(cls, tracking_number: str) -> Optional[dict]:
        """
        Alternative scraping method using parcelsapp.com
        This is a fallback if 17track.net fails.
        
        Args:
            tracking_number: The parcel tracking number
            
        Returns:
            Dictionary with tracking info or None if not found
        """
        tracking_number = tracking_number.strip().upper()

        try:
            url = f'https://parcelsapp.com/en/tracking/{tracking_number}'

            response = requests.get(
                url,
                headers=cls.HEADERS,
                timeout=10
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Look for status information in the page
            # Note: Website structure may change, so this is a general example

            # Try to find status badge
            status_element = soup.find('div', class_='status')
            status = status_element.text.strip() if status_element else 'Unknown'

            # Try to find events/tracking history
            events_container = soup.find('div', class_='history')
            last_event = 'No tracking information'
            event_date = 'N/A'
            location = 'Unknown'

            if events_container:
                # Get the first (latest) event
                event = events_container.find('div', class_='event')
                if event:
                    last_event = event.find('p', class_='description')
                    if last_event:
                        last_event = last_event.text.strip()
                    
                    date_elem = event.find('span', class_='date')
                    if date_elem:
                        event_date = date_elem.text.strip()
                    
                    location_elem = event.find('span', class_='location')
                    if location_elem:
                        location = location_elem.text.strip()

            return {
                'tracking_number': tracking_number,
                'status': status,
                'last_event': last_event,
                'location': location,
                'date': event_date,
                'carrier': 'Multiple Carriers',
            }

        except Exception as e:
            logger.error(f'Error tracking via parcelsapp {tracking_number}: {e}')
            return None


# Telegram Bot Handlers (async functions)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /start command.
    Send welcome message explaining bot functionality.
    """
    welcome_message = (
        "Welcome to Parcel Tracker Bot!\n\n"
        "I can help you track your parcels in real-time.\n\n"
        "How to use:\n"
        "Simply send me a tracking number and I'll fetch the latest status.\n\n"
        "Supported formats:\n"
        "• DHL, FedEx, UPS, China Post, and many more\n"
        "• Tracking number length: usually 9-20 characters\n\n"
        "Example: `RB123456789CN`\n\n"
        "This may take a few seconds as I fetch live data.\n"
        "Please be patient!"
    )

    await update.message.reply_text(
        welcome_message,
        parse_mode='HTML'
    )

    logger.info(f'User {update.effective_user.id} started the bot')


async def handle_tracking_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle user messages containing tracking numbers.
    Scrape tracking website and return formatted results.
    """
    tracking_number = update.message.text.strip()

    # Validate tracking number format
    if not ParcelTracker.validate_tracking_number(tracking_number):
        await update.message.reply_text(
            "Invalid tracking number format.\n\n"
            "Please enter a valid tracking number (9-20 alphanumeric characters).\n"
            "Example: <code>RB123456789CN</code>",
            parse_mode='HTML'
        )
        logger.warning(f'Invalid tracking number from {update.effective_user.id}: {tracking_number}')
        return

    # Send "typing" indicator to show bot is working
    await update.message.chat.send_action('typing')

    try:
        # Try primary tracking service (17track)
        tracking_info = await ParcelTracker.track_parcel(tracking_number)

        # Fallback to secondary service if primary fails
        if not tracking_info:
            await update.message.chat.send_action('typing')
            tracking_info = await ParcelTracker.track_parcel_parcelsapp(tracking_number)

        if not tracking_info:
            await update.message.reply_text(
                f"Tracking number <code>{tracking_number}</code> not found.\n\n"
                "Please verify:\n"
                "• The tracking number is correct\n"
                "• The package was shipped recently\n"
                "• Try again in a few minutes if just shipped",
                parse_mode='HTML'
            )
            logger.warning(f'Tracking number not found: {tracking_number}')
            return

        # Format the response
        response_message = (
            f"<b>Tracking Number:</b> <code>{tracking_info['tracking_number']}</code>\n"
            f"<b>Carrier:</b> {tracking_info['carrier']}\n"
            f"<b>Status:</b> {tracking_info['status']}\n"
            f"<b>Location:</b> {tracking_info['location']}\n"
            f"<b>Date:</b> {tracking_info['date']}\n"
            f"<b>Last Update:</b> {tracking_info['last_event']}"
        )

        await update.message.reply_text(
            response_message,
            parse_mode='HTML'
        )

        logger.info(f'Successfully tracked package for {update.effective_user.id}: {tracking_number}')

    except Exception as e:
        logger.error(f'Error handling tracking request: {e}')
        await update.message.reply_text(
            f"An error occurred while tracking your parcel.\n\n"
            f"Error: {str(e)}\n\n"
            "Please try again later or contact support.",
            parse_mode='HTML'
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command."""
    help_text = (
        "<b>Parcel Tracker Bot - Help</b>\n\n"
        "<b>Commands:</b>\n"
        "/start - Show welcome message\n"
        "/help - Show this help message\n\n"
        "<b>How to track:</b>\n"
        "1. Send your tracking number\n"
        "2. Wait for the bot to fetch tracking info\n"
        "3. Get real-time status updates\n\n"
        "<b>Supported carriers:</b>\n"
        "DHL, FedEx, UPS, EMS, China Post, Cainiao, and many more\n\n"
        "<b>Tips:</b>\n"
        "• Make sure the tracking number is correct\n"
        "• Some packages take time to appear in the system\n"
        "• If no results, try without spaces"
    )

    await update.message.reply_text(help_text, parse_mode='HTML')


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors in the application."""
    logger.error(f'Update {update} caused error {context.error}')

    if update and update.effective_message:
        await update.effective_message.reply_text(
            "An unexpected error occurred. Please try again later.",
            parse_mode='HTML'
        )


def main() -> None:
    """Start the bot."""
    # For Python 3.10+ on Windows, explicitly create and set event loop
    if sys.platform == 'win32':
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
    
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))

    # Register message handler for tracking numbers
    # This handler accepts any text that is not a command
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_tracking_number
        )
    )

    # Register error handler
    application.add_error_handler(error_handler)

    # Log bot startup
    logger.info('Starting Parcel Tracker Bot...')

    # Start the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
