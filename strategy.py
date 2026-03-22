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
        reasons_text = "\n".join(f"   {r}" for r in prediction.reasons[:4])

        message = (
            f"{flag} {prediction.tier} — SEÑAL DE VALOR\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"\n"
            f"🏟️ {race.track} | Carrera {race.race_number}\n"
            f"📏 {race.distance} | {race.surface.upper()}\n"
        )

        if race.race_time:
            message += f"🕐 Hora: {race.race_time.strftime('%I:%M %p')}\n"

        if race.race_class:
            message += f"🏷️ Clase: {race.race_class}\n"

        message += (
            f"\n"
            f"🐴 <b>{horse.name}</b> #{horse.number}\n"
            f"👤 Jockey: {horse.jockey}\n"
            f"🎓 Entrenador: {horse.trainer}\n"
        )

        if horse.weight:
            message += f"⚖️ Peso: {horse.weight}\n"

        message += (
            f"\n"
            f"📊 <b>Confianza: {prediction.confidence}%</b> {prediction.emoji_confidence}\n"
            f"💰 Odds: {horse.odds}\n"
            f"🎯 Apuesta sugerida: {prediction.suggested_bet}\n"
        )

        if prediction.value_score > 0:
            message += f"📈 Valor detectado: +{prediction.value_score}%\n"

        if horse.win_rate > 0:
            message += (
                f"\n"
                f"📋 Estadísticas:\n"
                f"   • Victorias: {horse.wins}/{horse.total_races} ({horse.win_rate:.0f}%)\n"
                f"   • Top 3: {horse.place_rate:.0f}%\n"
            )
            if horse.recent_form:
                message += f"   • Forma reciente: {horse.recent_form}\n"

        message += (
            f"\n"
            f"📌 Análisis:\n"
            f"{reasons_text}\n"
            f"\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🎰 <a href='{AFFILIATE_LINK}'>¡Apuesta ahora!</a>\n"
            f"⚠️ <i>Apuesta responsablemente. Esto es análisis, no garantía.</i>\n"
            f"\n"
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
