"""
DerbySignals — Main entry point.
Starts the Telegram bot and the automated broadcaster.
"""
import logging
import sys
import io

# Configure logging with UTF-8 support for Windows
handler = logging.StreamHandler(
    io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
)
handler.setFormatter(logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s"))

logging.basicConfig(
    level=logging.INFO,
    handlers=[handler],
)
logger = logging.getLogger(__name__)


def main():
    """Start the DerbySignals bot."""
    logger.info("=" * 50)
    logger.info("[DerbySignals] Bot Starting...")
    logger.info("=" * 50)

    from config import BOT_TOKEN, CHANNEL_ID, SCAN_INTERVAL
    from bot import create_bot
    from broadcaster import Broadcaster

    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set! Add it to .env")
        sys.exit(1)

    logger.info(f"Channel: {CHANNEL_ID}")
    logger.info(f"Scan interval: {SCAN_INTERVAL} minutes")

    # Create bot
    app = create_bot()
    logger.info("Bot created successfully")

    # Setup broadcaster
    broadcaster = Broadcaster(app)
    broadcaster.schedule()
    logger.info("Broadcaster scheduled")

    # Start polling
    logger.info("Bot is running! Press Ctrl+C to stop.")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
