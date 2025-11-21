from dataclasses import dataclass
from typing import Optional

from .enums import StyleFilm

@dataclass
class Film:
    titre: str
    duree: int  # en minutes
    note: Optional[float] = None  # sur 10
    style: Optional[StyleFilm] = None

    def __post_init__(self) -> None:
        if self.duree <= 0:
            raise ValueError("La durée d'un film doit être strictement positive.")
        if self.note is not None and not (0 <= self.note <= 10):
            raise ValueError("La note doit être comprise entre 0 et 10.")

    def __str__(self) -> str:
        base = f"{self.titre} ({self.duree} min)"
        details = []
        if self.style:
            details.append(self.style.name.replace("_", " ").title())
        if self.note is not None:
            details.append(f"note {self.note}/10")
        if details:
            return base + " - " + ", ".join(details)
        return base
