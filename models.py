"""
Data models for horse racing bot.
"""
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class Horse:
    """Represents a horse in a race."""
    name: str
    number: int = 0
    jockey: str = "Desconocido"
    trainer: str = "Desconocido"
    odds: float = 0.0
    weight: str = ""
    age: str = ""
    wins: int = 0
    places: int = 0  # top 2-3 finishes
    total_races: int = 0
    recent_form: str = ""  # e.g. "1-3-2-5-1"
    surface_preference: str = ""  # "arena", "grama", "sintética"

    @property
    def win_rate(self) -> float:
        if self.total_races == 0:
            return 0.0
        return (self.wins / self.total_races) * 100

    @property
    def place_rate(self) -> float:
        if self.total_races == 0:
            return 0.0
        return ((self.wins + self.places) / self.total_races) * 100


@dataclass
class Race:
    """Represents a horse race."""
    track: str  # e.g. "La Rinconada", "Churchill Downs"
    country: str  # "VE" or "USA"
    race_number: int
    distance: str  # e.g. "1200m"
    surface: str  # "arena", "grama", "dirt", "turf"
    race_time: Optional[datetime] = None
    race_class: str = ""
    purse: str = ""
    horses: List[Horse] = field(default_factory=list)
    conditions: str = ""  # track conditions
    race_name: str = ""

    @property
    def id(self) -> str:
        date_str = self.race_time.strftime("%Y%m%d") if self.race_time else "nodate"
        return f"{self.track}_{date_str}_R{self.race_number}"


@dataclass
class Prediction:
    """Represents a prediction for a horse in a race."""
    race: Race
    horse: Horse
    confidence: float  # 0-100
    reasons: List[str] = field(default_factory=list)
    suggested_bet: str = ""  # "Ganador", "Place", "Show"
    value_score: float = 0.0  # how much value the bet offers

    @property
    def emoji_confidence(self) -> str:
        if self.confidence >= 80:
            return "🔥🔥🔥"
        elif self.confidence >= 70:
            return "🔥🔥"
        elif self.confidence >= 60:
            return "🔥"
        return "⭐"

    @property
    def tier(self) -> str:
        if self.confidence >= 80:
            return "🏆 PREMIUM"
        elif self.confidence >= 70:
            return "⭐ ALTA"
        elif self.confidence >= 60:
            return "📊 MEDIA"
        return "📈 BAJA"
