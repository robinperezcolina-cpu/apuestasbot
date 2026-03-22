"""
Config module - loads environment variables.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Telegram
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "")
ADMIN_USER_ID = os.getenv("ADMIN_USER_ID", "")

# Affiliate
AFFILIATE_LINK = os.getenv("AFFILIATE_LINK", "https://stake.com")

# Scraping
SCAN_INTERVAL = int(os.getenv("SCAN_INTERVAL_MINUTES", "30"))

# Headers for web scraping (mimic browser)
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}
