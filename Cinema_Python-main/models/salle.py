from dataclasses import dataclass
from .enums import TypeSalle

@dataclass
class Salle:
    numero: int
    nom: str
    capacite: int
    type_salle: TypeSalle = TypeSalle.CLASSIQUE

    @property
    def supplement_prix(self) -> float:
        """Renvoie le supplément en euros selon le type de salle."""
        if self.type_salle in [TypeSalle.IMAX, TypeSalle.DOLBY, TypeSalle.TROIS_D]:
            return 2.50 # Majoration pour salles spéciales
        return 0.0

    def __str__(self):
        return f"Salle {self.numero} '{self.nom}' ({self.type_salle.value})"