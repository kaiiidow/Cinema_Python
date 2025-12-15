from dataclasses import dataclass
from .enums import StyleFilm

@dataclass
class Film:
    """
    Représente un film dans le catalogue du cinéma.

    Attributes:
        titre (str): Le titre du film.
        duree (int): La durée du film en minutes.
        style (StyleFilm): Le genre du film (ex: Action, Comédie).
        note (float): La note moyenne du film sur 10.
        poster_path (str): Le chemin relatif vers l'image de l'affiche du film.
        resume (str): Un court synopsis du film.
    """
    titre: str
    duree: int  # en minutes
    style: StyleFilm
    note: float = 0.0
    poster_path: str = ""
    resume: str = "Pas de synopsis"
    
    def __str__(self):
        """Retourne une représentation textuelle simple du film."""
        return f"{self.titre} ({self.duree} min) - {self.style.name}"