"""
Strategy module - filters predictions and formats signals.
"""
import logging
from typing import List
from models import Prediction, Race
from predictor import Predictor
from config import AFFILIATE_LINK

logger = logging.getLogger(__name__)


class Strategy:
    """
    Filters predictions and formats them for broadcasting.
    Only signals with sufficient confidence are sent.
    """

    MIN_CONFIDENCE = 60  # Minimum confidence to send signal
    MIN_VALUE_CONFIDENCE = 65  # Minimum for "value bet" signals

    def __init__(self):
        self.predictor = Predictor()

    def analyze_races(self, races: List[Race]) -> List[Prediction]:
        """Analyze all races and return filtered predictions."""
        all_predictions = []

        for race in races:
            predictions = self.predictor.analyze_race(race)
            # Take top predictions from each race
            for pred in predictions:
                if pred.confidence >= self.MIN_CONFIDENCE:
                    all_predictions.append(pred)

        # Sort by confidence
        all_predictions.sort(key=lambda p: p.confidence, reverse=True)
        logger.info(f"📊 {len(all_predictions)} señales generadas de {len(races)} carreras")
        return all_predictions

    def format_signal(self, prediction: Prediction) -> str:
        """Format a single prediction as a Telegram message."""
        race = prediction.race
        horse = prediction.horse

        # Country flag
        flag = "🇻🇪" if race.country == "VE" else "🇺🇸"

        # Build reasons string
        reasons_text = "\n".join(f"• {r}" for r in prediction.reasons[:4])

        message = (
            f"<b>{flag} {prediction.tier} | SEÑAL PRIVADA</b> 🎯\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🏇 <b>Caballo:</b> <code>{horse.name}</code> (#{horse.number})\n"
            f"🎯 <b>Apuesta:</b> {prediction.suggested_bet}\n"
            f"💎 <b>Cuota (Odds):</b> {horse.odds}\n"
            f"📈 <b>Confianza:</b> {prediction.confidence}% {prediction.emoji_confidence}\n"
            f"\n"
            f"📍 <b>Pista:</b> {race.track}\n"
            f"🏁 <b>Carrera:</b> {race.race_number} ({race.distance} | {race.surface.upper()})\n"
        )

        if race.race_time:
            message += f"⏱ <b>Hora:</b> {race.race_time.strftime('%I:%M %p')}\n"

        message += f"\n<blockquote><b>📊 ESTADÍSTICAS DEL EJEMPLAR:</b>\n"
        
        if horse.win_rate > 0:
            message += (
                f"• Victorias: {horse.wins}/{horse.total_races} ({horse.win_rate:.0f}%)\n"
                f"• Win/Place (Top 3): {horse.place_rate:.0f}%\n"
            )
        message += (
            f"• Jockey: {horse.jockey}\n"
            f"• Preparador: {horse.trainer}\n"
        )
        if horse.weight:
            message += f"• Peso: {horse.weight}\n"

        message += (
            f"\n<b>🧠 ANÁLISIS DE LA IA:</b>\n"
            f"{reasons_text}</blockquote>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🤖 @DerbySignals_bot"
        )
        return message

    def format_race_list(self, races: List[Race]) -> str:
        """Format a list of races for display."""
        if not races:
            return "❌ No se encontraron carreras programadas."

        lines = ["🏇 <b>CARRERAS PRÓXIMAS</b>\n"]

        # Group by country
        ve_races = [r for r in races if r.country == "VE"]
        usa_races = [r for r in races if r.country == "USA"]

        if ve_races:
            lines.append("🇻🇪 <b>VENEZUELA</b>")
            for race in ve_races:
                time_str = race.race_time.strftime("%I:%M %p") if race.race_time else "TBD"
                lines.append(
                    f"  🏁 C{race.race_number} | {race.track} | "
                    f"{race.distance} {race.surface} | {time_str} | "
                    f"{len(race.horses)} caballos"
                )
            lines.append("")

        if usa_races:
            lines.append("🇺🇸 <b>USA</b>")
            # Group by track
            tracks = {}
            for race in usa_races:
                tracks.setdefault(race.track, []).append(race)

            for track_name, track_races in tracks.items():
                lines.append(f"  📍 <b>{track_name}</b>")
                for race in track_races:
                    time_str = race.race_time.strftime("%I:%M %p") if race.race_time else "TBD"
                    lines.append(
                        f"    🏁 C{race.race_number} | {race.distance} {race.surface} | "
                        f"{time_str} | {len(race.horses)} caballos"
                    )
            lines.append("")

        total = len(ve_races) + len(usa_races)
        lines.append(f"📊 Total: {total} carreras")
        return "\n".join(lines)

    def format_predictions_summary(self, predictions: List[Prediction]) -> str:
        """Format a summary of top predictions."""
        if not predictions:
            return "❌ No se generaron predicciones con suficiente confianza."

        lines = [
            "🏇 <b>TOP PREDICCIONES</b>",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n",
        ]

        for i, pred in enumerate(predictions[:10], 1):
            flag = "🇻🇪" if pred.race.country == "VE" else "🇺🇸"
            lines.append(
                f"{i}. {pred.emoji_confidence} <b>{pred.horse.name}</b>\n"
                f"   {flag} {pred.race.track} C{pred.race.race_number} | "
                f"Conf: {pred.confidence}% | Odds: {pred.horse.odds}\n"
                f"   🎯 {pred.suggested_bet}"
            )
            if pred.value_score > 0:
                lines.append(f"   💰 Valor: +{pred.value_score}%")
            lines.append("")

        lines.append(f"\n🎰 <a href='{AFFILIATE_LINK}'>¡Apuesta ahora!</a>")
        lines.append("⚠️ <i>Apuesta responsablemente.</i>")
        return "\n".join(lines)
