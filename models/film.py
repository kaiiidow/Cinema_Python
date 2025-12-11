from dataclasses import dataclass
from .enums import StyleFilm

@dataclass
class Film:
    titre: str
    duree: int  # en minutes
    style: StyleFilm
    note: float = 0.0
    resume: str = "Pas de synopsis"
    
    def __str__(self):
        return f"{self.titre} ({self.duree} min) - {self.style.name}"