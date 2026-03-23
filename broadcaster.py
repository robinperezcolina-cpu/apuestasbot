"""
Broadcaster - Automated signal sending to Telegram channel.
Uses APScheduler for periodic scanning and broadcasting.
"""
import logging
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application
from telegram.constants import ParseMode

from scraper_venezuela import VenezuelaScraper
from scraper_usa import USAScraper
from strategy import Strategy
from config import CHANNEL_ID, SCAN_INTERVAL, AFFILIATE_LINK

logger = logging.getLogger(__name__)

class Broadcaster:
    """
    Automatically scans for races and broadcasts top predictions
    to the Telegram channel at regular intervals.
    """

    def __init__(self, app: Application):
        self.app = app
        self.ve_scraper = VenezuelaScraper()
        self.usa_scraper = USAScraper()
        self.strategy = Strategy()
        self.last_sent_ids = set()  # Track sent predictions to avoid duplicates
        self.scan_count = 0

    async def run_scan_and_broadcast(self, context=None):
        """Scan for races and broadcast top signals."""
        self.scan_count += 1
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        logger.info(f"🔄 Auto-scan #{self.scan_count} at {now}")

        try:
            # Fetch races
            ve_races = self.ve_scraper.get_upcoming_races()
            usa_races = self.usa_scraper.get_upcoming_races()
            all_races = ve_races + usa_races

            logger.info(f"📊 Found {len(all_races)} total races "
                       f"({len(ve_races)} VE, {len(usa_races)} USA)")

            if not all_races:
                logger.info("No races found, skipping broadcast")
                return

            # Analyze
            predictions = self.strategy.analyze_races(all_races)

            # Filter: only high confidence, not yet sent
            new_signals = []
            for pred in predictions:
                signal_id = f"{pred.race.id}_{pred.horse.name}"
                if pred.confidence >= 65 and signal_id not in self.last_sent_ids:
                    new_signals.append((pred, signal_id))

            if not new_signals:
                logger.info("No new signals to broadcast")
                return

            # Send top 3 new signals
            sent = 0
            for pred, signal_id in new_signals[:3]:
                try:
                    message = self.strategy.format_signal(pred)
                    bot = self.app.bot
                    keyboard = [[InlineKeyboardButton("🎰 ¡Apuesta ahora!", url=AFFILIATE_LINK)]]
                    reply_markup = InlineKeyboardMarkup(keyboard)

                    await bot.send_message(
                        chat_id=CHANNEL_ID,
                        text=message,
                        parse_mode=ParseMode.HTML,
                        disable_web_page_preview=True,
                        reply_markup=reply_markup,
                    )
                    self.last_sent_ids.add(signal_id)
                    sent += 1
                    logger.info(
                        f"📡 Sent signal: {pred.horse.name} "
                        f"({pred.confidence}%) at {pred.race.track}"
                    )
                except Exception as e:
                    logger.error(f"Failed to send signal: {e}")

            logger.info(f"✅ Broadcast complete: {sent} signals sent")

            # Clean old IDs (keep last 100)
            if len(self.last_sent_ids) > 100:
                self.last_sent_ids = set(list(self.last_sent_ids)[-50:])

        except Exception as e:
            logger.error(f"❌ Broadcast error: {e}", exc_info=True)

    def schedule(self):
        """Schedule periodic broadcasting using the bot's job queue."""
        job_queue = self.app.job_queue

        # Run first scan 30 seconds after startup
        job_queue.run_once(self.run_scan_and_broadcast, when=30)

        # Then run every SCAN_INTERVAL minutes
        job_queue.run_repeating(
            self.run_scan_and_broadcast,
            interval=SCAN_INTERVAL * 60,  # Convert minutes to seconds
            first=SCAN_INTERVAL * 60,
        )

        logger.info(
            f"📡 Broadcaster scheduled: every {SCAN_INTERVAL} minutes "
            f"to channel {CHANNEL_ID}"
        )
