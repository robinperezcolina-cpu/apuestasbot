"""
Prediction engine for horse racing.
Analyzes race data and generates confidence scores.
"""
import logging
from typing import List
from models import Horse, Race, Prediction

logger = logging.getLogger(__name__)


class Predictor:
    """
    Statistical analysis engine that scores horses based on multiple factors.

    Factors analyzed:
    1. Morning line odds (market sentiment)
    2. Win/place rate (historical success)
    3. Recent form (momentum)
    4. Jockey consistency
    5. Surface preference match
    6. Distance suitability
    7. Odds value detection (steam moves)
    """

    # Weights for each factor (sum = 100)
    WEIGHTS = {
        "odds_rank": 15,       # Market position
        "win_rate": 20,        # Historical win percentage
        "place_rate": 10,      # Consistency (top 3)
        "recent_form": 25,     # Latest race performances
        "surface_match": 15,   # Surface preference alignment
        "value_odds": 15,      # Value bet detection
    }

    def analyze_race(self, race: Race) -> List[Prediction]:
        """
        Analyze all horses in a race and return predictions sorted by confidence.
        """
        if not race.horses:
            return []

        predictions = []

        for horse in race.horses:
            score = self._calculate_score(horse, race)
            reasons = self._generate_reasons(horse, race, score)

            # Determine suggested bet type
            if score >= 75:
                suggested_bet = "Ganador"
            elif score >= 65:
                suggested_bet = "Place (Top 2)"
            elif score >= 55:
                suggested_bet = "Show (Top 3)"
            else:
                suggested_bet = "Observar"

            # Calculate value score (compare confidence to implied probability from odds)
            implied_prob = (1 / horse.odds * 100) if horse.odds > 0 else 0
            value_score = score - implied_prob  # positive = value bet

            prediction = Prediction(
                race=race,
                horse=horse,
                confidence=round(score, 1),
                reasons=reasons,
                suggested_bet=suggested_bet,
                value_score=round(value_score, 1),
            )
            predictions.append(prediction)

        # Sort by confidence (highest first)
        predictions.sort(key=lambda p: p.confidence, reverse=True)
        return predictions

    def _calculate_score(self, horse: Horse, race: Race) -> float:
        """Calculate overall confidence score for a horse."""
        scores = {}

        # 1. Odds rank score (lower odds = higher score)
        scores["odds_rank"] = self._score_odds_rank(horse, race)

        # 2. Win rate score
        scores["win_rate"] = self._score_win_rate(horse)

        # 3. Place rate score
        scores["place_rate"] = self._score_place_rate(horse)

        # 4. Recent form score
        scores["recent_form"] = self._score_recent_form(horse)

        # 5. Surface match score
        scores["surface_match"] = self._score_surface_match(horse, race)

        # 6. Value odds score
        scores["value_odds"] = self._score_value_odds(horse, race)

        # Calculate weighted average
        total_score = 0
        for factor, weight in self.WEIGHTS.items():
            factor_score = scores.get(factor, 50)
            total_score += (factor_score * weight / 100)

        # Clamp between 0-100
        return max(0, min(100, total_score))

    def _score_odds_rank(self, horse: Horse, race: Race) -> float:
        """Score based on position in odds ranking."""
        if not race.horses or horse.odds <= 0:
            return 50

        sorted_horses = sorted(race.horses, key=lambda h: h.odds)
        rank = next(
            (i for i, h in enumerate(sorted_horses) if h.name == horse.name),
            len(sorted_horses)
        )

        num_horses = len(race.horses)
        if num_horses <= 1:
            return 75

        # Top-ranked horses get higher scores
        rank_percentile = 1.0 - (rank / num_horses)
        return rank_percentile * 90 + 10  # Range: 10-100

    def _score_win_rate(self, horse: Horse) -> float:
        """Score based on career win rate."""
        if horse.total_races == 0:
            return 40  # Unknown horses get neutral-low score

        win_rate = horse.win_rate
        if win_rate >= 30:
            return 90
        elif win_rate >= 20:
            return 75
        elif win_rate >= 15:
            return 65
        elif win_rate >= 10:
            return 55
        elif win_rate >= 5:
            return 40
        return 25

    def _score_place_rate(self, horse: Horse) -> float:
        """Score based on top-3 finish rate (consistency)."""
        if horse.total_races == 0:
            return 40

        place_rate = horse.place_rate
        if place_rate >= 50:
            return 90
        elif place_rate >= 40:
            return 75
        elif place_rate >= 30:
            return 65
        elif place_rate >= 20:
            return 50
        return 30

    def _score_recent_form(self, horse: Horse) -> float:
        """Score based on recent race positions."""
        if not horse.recent_form:
            return 45

        try:
            positions = [int(p) for p in horse.recent_form.split("-") if p.strip().isdigit()]
        except ValueError:
            return 45

        if not positions:
            return 45

        # Weight recent races more heavily
        weights = [0.35, 0.25, 0.20, 0.12, 0.08]
        score = 0

        for i, pos in enumerate(positions[:5]):
            weight = weights[i] if i < len(weights) else 0.05

            # Convert position to score (1st = 100, 2nd = 85, 3rd = 70, etc.)
            if pos == 1:
                pos_score = 100
            elif pos == 2:
                pos_score = 85
            elif pos == 3:
                pos_score = 72
            elif pos <= 5:
                pos_score = 55
            elif pos <= 8:
                pos_score = 35
            else:
                pos_score = 15

            score += pos_score * weight

        return score

    def _score_surface_match(self, horse: Horse, race: Race) -> float:
        """Score based on surface preference alignment."""
        if not horse.surface_preference:
            return 50  # Unknown = neutral

        race_surface = race.surface.lower()
        pref_surface = horse.surface_preference.lower()

        # Normalize surface names
        surface_groups = {
            "dirt": ["dirt", "arena"],
            "turf": ["turf", "grama", "grass"],
            "synthetic": ["synthetic", "sintética", "all-weather"],
        }

        race_group = None
        pref_group = None
        for group_name, surfaces in surface_groups.items():
            if race_surface in surfaces:
                race_group = group_name
            if pref_surface in surfaces:
                pref_group = group_name

        if race_group and pref_group:
            if race_group == pref_group:
                return 85  # Strong surface match
            return 35  # Surface mismatch
        return 50  # Can't determine

    def _score_value_odds(self, horse: Horse, race: Race) -> float:
        """
        Score based on odds value detection.
        Identifies horses whose odds may be higher than their true probability.
        """
        if horse.odds <= 0 or horse.total_races == 0:
            return 50

        # Implied probability from odds
        implied_prob = (1 / horse.odds) * 100

        # Estimated probability from stats
        estimated_prob = horse.win_rate

        # Value = when estimated probability > implied probability
        value_diff = estimated_prob - implied_prob

        if value_diff > 15:
            return 95  # Huge overlay
        elif value_diff > 10:
            return 85  # Significant value
        elif value_diff > 5:
            return 72  # Good value
        elif value_diff > 0:
            return 60  # Slight value
        elif value_diff > -5:
            return 45  # Fair odds
        return 30  # Underlay (poor value)

    def _generate_reasons(self, horse: Horse, race: Race, score: float) -> List[str]:
        """Generate human-readable reasons for the prediction."""
        reasons = []

        # Win rate reason
        if horse.win_rate >= 25:
            reasons.append(f"📈 Alta tasa de victoria: {horse.win_rate:.0f}%")
        elif horse.win_rate >= 15:
            reasons.append(f"📊 Buena tasa de victoria: {horse.win_rate:.0f}%")

        # Consistency
        if horse.place_rate >= 45:
            reasons.append(f"🎯 Muy consistente: {horse.place_rate:.0f}% en top 3")

        # Recent form
        if horse.recent_form:
            positions = horse.recent_form.split("-")
            if positions and positions[0] in ("1", "2"):
                reasons.append(f"🔥 Viene de buena racha: últimos resultados {horse.recent_form}")

        # Odds position
        if race.horses:
            sorted_h = sorted(race.horses, key=lambda h: h.odds)
            rank = next((i + 1 for i, h in enumerate(sorted_h) if h.name == horse.name), 0)
            if rank <= 3:
                reasons.append(f"⭐ Favorito #{rank} del mercado (odds: {horse.odds})")

        # Surface match
        if horse.surface_preference and horse.surface_preference.lower() in race.surface.lower():
            reasons.append(f"✅ Superficie preferida: {race.surface}")

        # Value bet
        if horse.odds > 0 and horse.total_races > 0:
            implied = (1 / horse.odds) * 100
            if horse.win_rate > implied + 5:
                reasons.append(f"💰 APUESTA DE VALOR: odds ofrecen más de lo que merece")

        if not reasons:
            reasons.append("📋 Análisis basado en datos disponibles")

        return reasons

    def analyze_demo(self) -> str:
        """Demo analysis for testing."""
        from scraper_venezuela import VenezuelaScraper

        scraper = VenezuelaScraper()
        races = scraper.get_upcoming_races()

        if not races:
            return "No se encontraron carreras."

        results = []
        for race in races[:2]:
            predictions = self.analyze_race(race)
            results.append(f"\n🏁 {race.track} - Carrera {race.race_number} ({race.distance})")
            for pred in predictions[:3]:
                results.append(
                    f"  {pred.emoji_confidence} {pred.horse.name} | "
                    f"Confianza: {pred.confidence}% | "
                    f"Odds: {pred.horse.odds}"
                )
                for reason in pred.reasons:
                    results.append(f"    {reason}")

        return "\n".join(results)
