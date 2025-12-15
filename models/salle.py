from dataclasses import dataclass
from .enums import TypeSalle

@dataclass
class Salle:
    """
    Représente une salle de cinéma.

    Attributes:
        numero (int): Le numéro unique de la salle.
        nom (str): Le nom de la salle (ex: "L'Odyssée").
        capacite (int): Le nombre total de sièges dans la salle.
        type_salle (TypeSalle): Le type de technologie de la salle
            (ex: Classique, IMAX).
    """
    numero: int
    nom: str
    capacite: int
    type_salle: TypeSalle = TypeSalle.CLASSIQUE

    @property
    def supplement_prix(self) -> float:
        """
        Détermine le supplément de prix en euros en fonction du type de salle.

        Les salles spéciales (IMAX, Dolby, 3D) entraînent une majoration.
        """
        if self.type_salle in [TypeSalle.IMAX, TypeSalle.DOLBY, TypeSalle.TROIS_D]:
            return 2.50
        return 0.0

    def __str__(self):
        """Retourne une représentation textuelle de la salle."""
        return f"Salle {self.numero} '{self.nom}' ({self.type_salle.value})"