"""
Configuration file for Parcel Tracker Bot
Customize bot behavior and tracking settings here
"""

# Tracking Service Timeouts (seconds)
REQUEST_TIMEOUT = 10

# Tracking Number Validation
MIN_TRACKING_LENGTH = 9
MAX_TRACKING_LENGTH = 20

# Bot Settings
ENABLE_FALLBACK_TRACKING = True  # Try alternative service if primary fails
TYPING_INDICATOR = True  # Show "typing" indicator while processing
LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Status Codes
STATUS_MAP = {
    '0': 'Picked up',
    '1': 'In transit',
    '2': 'Out for delivery',
    '3': 'Delivered',
    '4': 'Undeliverable',
    '5': 'Not found',
    '10': 'Customs clearance',
    '11': 'Return in transit',
    '12': 'Returned',
}

# Tracking Service URLs
TRACKING_SERVICES = {
    '17track': {
        'name': '17Track',
        'endpoint': 'https://api.17track.net/track/simplejson',
        'method': 'POST',
        'primary': True,
    },
    'parcelsapp': {
        'name': 'ParcelsApp',
        'endpoint': 'https://parcelsapp.com/en/tracking/',
        'method': 'GET',
        'primary': False,
    }
}

# Message Templates
MESSAGES = {
    'welcome': (
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
    ),
    'invalid_format': (
        "Invalid tracking number format.\n\n"
        "Please enter a valid tracking number (9-20 alphanumeric characters).\n"
        "Example: <code>RB123456789CN</code>"
    ),
    'not_found': (
        "Tracking number <code>{tracking_number}</code> not found.\n\n"
        "Please verify:\n"
        "• The tracking number is correct\n"
        "• The package was shipped recently\n"
        "• Try again in a few minutes if just shipped"
    ),
    'error': (
        "An error occurred while tracking your parcel.\n\n"
        "Error: {error}\n\n"
        "Please try again later or contact support."
    ),
    'help': (
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
    ),
}

# Carrier IDs for 17track.net (optional, 0 = auto-detect)
CARRIER_CODES = {
    'dhl': 1,
    'fedex': 2,
    'ups': 3,
    'ems': 4,
    'china_post': 5,
    'cainiao': 6,
}
