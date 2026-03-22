"""
Telegram Bot - DerbySignals
Commands for users and admin to interact with the horse racing system.
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
)
from telegram.constants import ParseMode

from scraper_venezuela import VenezuelaScraper
from scraper_usa import USAScraper
from strategy import Strategy
from config import BOT_TOKEN, ADMIN_USER_ID, AFFILIATE_LINK, CHANNEL_ID

logger = logging.getLogger(__name__)

# Initialize components
ve_scraper = VenezuelaScraper()
usa_scraper = USAScraper()
strategy = Strategy()


# ─────────────────────────────────────────────────
# PUBLIC COMMANDS
# ─────────────────────────────────────────────────

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    user = update.effective_user
    welcome = (
        f"🏇 <b>¡Bienvenido a DerbySignals, {user.first_name}!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Soy tu bot de análisis hípico para carreras en:\n"
        f"🇻🇪 <b>Venezuela</b> (La Rinconada)\n"
        f"🇺🇸 <b>USA</b> (Churchill Downs, Santa Anita, y más)\n\n"
        f"📊 Uso análisis estadístico avanzado para encontrar\n"
        f"caballos con <b>alto valor</b> de apuesta.\n\n"
        f"<b>Comandos disponibles:</b>\n"
        f"🏁 /carreras — Ver próximas carreras\n"
        f"🔮 /predicciones — Ver predicciones activas\n"
        f"🏆 /resultados — Últimos resultados\n"
        f"❓ /help — Ayuda y más información\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔔 <b>Únete al canal para señales automáticas:</b>\n"
        f"📢 {CHANNEL_ID}\n\n"
        f"🎰 <a href='{AFFILIATE_LINK}'>¡Apuesta ahora!</a>"
    )

    keyboard = [
        [
            InlineKeyboardButton("🏁 Carreras", callback_data="carreras"),
            InlineKeyboardButton("🔮 Predicciones", callback_data="predicciones"),
        ],
        [
            InlineKeyboardButton("📢 Canal", url=f"https://t.me/{CHANNEL_ID.replace('@', '')}"),
            InlineKeyboardButton("🎰 Apostar", url=AFFILIATE_LINK),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        welcome,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup,
        disable_web_page_preview=True,
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    help_text = (
        "🏇 <b>DerbySignals — Ayuda</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "<b>📋 Comandos:</b>\n"
        "/start — Mensaje de bienvenida\n"
        "/carreras — Listar próximas carreras\n"
        "/predicciones — Ver predicciones con mayor confianza\n"
        "/predicciones_ve — Solo predicciones de Venezuela\n"
        "/predicciones_usa — Solo predicciones de USA\n"
        "/resultados — Últimos resultados\n"
        "/help — Este mensaje\n\n"
        "<b>📊 ¿Cómo funciona?</b>\n"
        "Analizamos datos de carreras usando múltiples factores:\n"
        "• Historial de victorias del caballo\n"
        "• Racha actual (forma reciente)\n"
        "• Rendimiento del jockey y entrenador\n"
        "• Preferencia de superficie\n"
        "• Detección de valor en las odds\n\n"
        "<b>🔥 Niveles de confianza:</b>\n"
        "🏆 PREMIUM (80%+) — Señal de alta confianza\n"
        "⭐ ALTA (70-79%) — Buena oportunidad\n"
        "📊 MEDIA (60-69%) — Para considerar\n\n"
        "⚠️ <i>Las predicciones son análisis estadístico, "
        "no garantías. Apuesta responsablemente.</i>"
    )
    await update.message.reply_text(
        help_text, parse_mode=ParseMode.HTML
    )


async def carreras_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /carreras command — list upcoming races."""
    await update.message.reply_text("🔄 Buscando carreras...")

    try:
        ve_races = ve_scraper.get_upcoming_races()
        usa_races = usa_scraper.get_upcoming_races()
        all_races = ve_races + usa_races

        message = strategy.format_race_list(all_races)

        keyboard = [
            [
                InlineKeyboardButton("🔮 Ver Predicciones", callback_data="predicciones"),
                InlineKeyboardButton("🎰 Apostar", url=AFFILIATE_LINK),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            message,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup,
        )
    except Exception as e:
        logger.error(f"Error fetching races: {e}")
        await update.message.reply_text(
            "❌ Error buscando carreras. Intenta de nuevo en unos minutos."
        )


async def predicciones_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /predicciones command — show top predictions."""
    await update.message.reply_text("🔄 Analizando carreras... Esto puede tomar unos segundos.")

    try:
        ve_races = ve_scraper.get_upcoming_races()
        usa_races = usa_scraper.get_upcoming_races()
        all_races = ve_races + usa_races

        predictions = strategy.analyze_races(all_races)

        if not predictions:
            await update.message.reply_text(
                "❌ No se encontraron predicciones con suficiente confianza.\n"
                "Intenta más tarde cuando haya más carreras disponibles."
            )
            return

        # Send summary
        summary = strategy.format_predictions_summary(predictions)
        await update.message.reply_text(
            summary,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )

        # Send top 3 detailed signals
        top_preds = [p for p in predictions if p.confidence >= 65][:3]
        for pred in top_preds:
            signal = strategy.format_signal(pred)
            await update.message.reply_text(
                signal,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )

    except Exception as e:
        logger.error(f"Error generating predictions: {e}")
        await update.message.reply_text(
            "❌ Error generando predicciones. Intenta de nuevo."
        )


async def predicciones_ve_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /predicciones_ve — Venezuela only."""
    await update.message.reply_text("🇻🇪 Analizando carreras de Venezuela...")

    try:
        races = ve_scraper.get_upcoming_races()
        predictions = strategy.analyze_races(races)

        if not predictions:
            await update.message.reply_text("❌ No hay predicciones para Venezuela ahora.")
            return

        summary = strategy.format_predictions_summary(predictions)
        await update.message.reply_text(
            summary, parse_mode=ParseMode.HTML, disable_web_page_preview=True
        )
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("❌ Error. Intenta de nuevo.")


async def predicciones_usa_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /predicciones_usa — USA only."""
    await update.message.reply_text("🇺🇸 Analizando carreras de USA...")

    try:
        races = usa_scraper.get_upcoming_races()
        predictions = strategy.analyze_races(races)

        if not predictions:
            await update.message.reply_text("❌ No hay predicciones para USA ahora.")
            return

        summary = strategy.format_predictions_summary(predictions)
        await update.message.reply_text(
            summary, parse_mode=ParseMode.HTML, disable_web_page_preview=True
        )
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("❌ Error. Intenta de nuevo.")


async def resultados_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /resultados command."""
    await update.message.reply_text("🔄 Buscando resultados...")

    try:
        ve_results = ve_scraper.get_results()
        usa_results = usa_scraper.get_results()

        if not ve_results and not usa_results:
            await update.message.reply_text(
                "📋 No hay resultados recientes disponibles.\n"
                "Los resultados se actualizan después de cada jornada."
            )
            return

        lines = ["🏆 <b>RESULTADOS RECIENTES</b>\n"]

        if ve_results:
            lines.append("🇻🇪 <b>Venezuela</b>")
            for r in ve_results[:10]:
                lines.append(f"  {r['position']}° — {r['horse']} ({r['track']})")
            lines.append("")

        if usa_results:
            lines.append("🇺🇸 <b>USA</b>")
            for r in usa_results[:10]:
                lines.append(f"  {r['position']}° — {r['horse']} ({r['track']})")

        await update.message.reply_text(
            "\n".join(lines), parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"Error fetching results: {e}")
        await update.message.reply_text("❌ Error buscando resultados.")


# ─────────────────────────────────────────────────
# ADMIN COMMANDS
# ─────────────────────────────────────────────────

def is_admin(user_id: int) -> bool:
    """Check if user is admin."""
    if not ADMIN_USER_ID:
        return True  # If no admin set, allow all
    try:
        return str(user_id) == str(ADMIN_USER_ID)
    except ValueError:
        return False


async def scan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin: /scan — Force a manual scan."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Solo el admin puede usar este comando.")
        return

    await update.message.reply_text("🔍 Escaneando todas las fuentes...")

    try:
        ve_races = ve_scraper.get_upcoming_races()
        usa_races = usa_scraper.get_upcoming_races()
        all_races = ve_races + usa_races
        predictions = strategy.analyze_races(all_races)

        await update.message.reply_text(
            f"✅ Escaneo completado:\n"
            f"🏁 {len(all_races)} carreras encontradas\n"
            f"🇻🇪 {len(ve_races)} en Venezuela\n"
            f"🇺🇸 {len(usa_races)} en USA\n"
            f"📊 {len(predictions)} señales generadas"
        )

        # Send top predictions
        top = [p for p in predictions if p.confidence >= 65][:5]
        for pred in top:
            signal = strategy.format_signal(pred)
            await update.message.reply_text(
                signal, parse_mode=ParseMode.HTML, disable_web_page_preview=True
            )

    except Exception as e:
        logger.error(f"Scan error: {e}")
        await update.message.reply_text(f"❌ Error en escaneo: {e}")


async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin: /broadcast — Force broadcast to channel."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Solo el admin puede usar este comando.")
        return

    await update.message.reply_text("📡 Generando y enviando señales al canal...")

    try:
        ve_races = ve_scraper.get_upcoming_races()
        usa_races = usa_scraper.get_upcoming_races()
        all_races = ve_races + usa_races
        predictions = strategy.analyze_races(all_races)

        top_preds = [p for p in predictions if p.confidence >= 65][:5]

        if not top_preds:
            await update.message.reply_text("❌ No hay señales con suficiente confianza para enviar.")
            return

        sent = 0
        for pred in top_preds:
            signal = strategy.format_signal(pred)
            try:
                await context.bot.send_message(
                    chat_id=CHANNEL_ID,
                    text=signal,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )
                sent += 1
            except Exception as e:
                logger.error(f"Failed to send to channel: {e}")

        await update.message.reply_text(
            f"✅ {sent}/{len(top_preds)} señales enviadas al canal {CHANNEL_ID}"
        )

    except Exception as e:
        logger.error(f"Broadcast error: {e}")
        await update.message.reply_text(f"❌ Error: {e}")


# ─────────────────────────────────────────────────
# CALLBACK HANDLER (inline buttons)
# ─────────────────────────────────────────────────

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline button presses."""
    query = update.callback_query
    await query.answer()

    if query.data == "carreras":
        try:
            ve_races = ve_scraper.get_upcoming_races()
            usa_races = usa_scraper.get_upcoming_races()
            all_races = ve_races + usa_races
            message = strategy.format_race_list(all_races)
            await query.message.reply_text(
                message, parse_mode=ParseMode.HTML
            )
        except Exception as e:
            await query.message.reply_text("❌ Error buscando carreras.")

    elif query.data == "predicciones":
        try:
            ve_races = ve_scraper.get_upcoming_races()
            usa_races = usa_scraper.get_upcoming_races()
            all_races = ve_races + usa_races
            predictions = strategy.analyze_races(all_races)
            summary = strategy.format_predictions_summary(predictions)
            await query.message.reply_text(
                summary, parse_mode=ParseMode.HTML, disable_web_page_preview=True
            )
        except Exception as e:
            await query.message.reply_text("❌ Error generando predicciones.")


# ─────────────────────────────────────────────────
# BOT SETUP
# ─────────────────────────────────────────────────

def create_bot() -> Application:
    """Create and configure the Telegram bot application."""
    if not BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN not set in .env")

    app = Application.builder().token(BOT_TOKEN).build()

    # Public commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("carreras", carreras_command))
    app.add_handler(CommandHandler("predicciones", predicciones_command))
    app.add_handler(CommandHandler("predicciones_ve", predicciones_ve_command))
    app.add_handler(CommandHandler("predicciones_usa", predicciones_usa_command))
    app.add_handler(CommandHandler("resultados", resultados_command))

    # Admin commands
    app.add_handler(CommandHandler("scan", scan_command))
    app.add_handler(CommandHandler("broadcast", broadcast_command))

    # Callback handler for inline buttons
    app.add_handler(CallbackQueryHandler(button_callback))

    return app
