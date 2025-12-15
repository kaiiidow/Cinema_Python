from dataclasses import dataclass
from datetime import datetime
from .film import Film
from .salle import Salle
from .exceptions import SallePleineException
from dataclasses import dataclass, field
from typing import Set, List, Optional

@dataclass
class Seance:
    """
    Représente une projection unique d'un film dans une salle à un horaire donné.

    Attributes:
        id (str): Identifiant unique de la séance (ex: "S01").
        film (Film): L'objet Film projeté.
        salle (Salle): L'objet Salle où a lieu la projection.
        horaire (datetime): La date et l'heure exactes du début de la séance.
        places_reservees (int): Le nombre total de places actuellement réservées.
        places_occupees (Set[int]): L'ensemble des numéros de sièges spécifiques
            qui sont occupés.
    """
    id: str
    film: Film
    salle: Salle
    horaire: datetime
    places_reservees: int = 0
    places_occupees: Set[int] = field(default_factory=set)

    @property
    def places_disponibles(self) -> int:
        """Calcule le nombre de places restantes pour la séance."""
        return self.salle.capacite - self.places_reservees

    @property
    def est_complete(self) -> bool:
        """Vérifie si la séance est complète."""
        return self.places_disponibles <= 0

    def reserver_places(self, nombre: int):
        """
        Réserve un certain nombre de places sans spécifier les numéros de siège.

        Args:
            nombre (int): Le nombre de places à réserver.

        Raises:
            SallePleineException: Si le nombre de places demandées est supérieur
                au nombre de places disponibles.
        """
        if nombre > self.places_disponibles:
            raise SallePleineException(
                f"Impossible : {nombre} places demandées, {self.places_disponibles} restantes."
            )
        self.places_reservees += nombre
    
    def reserver_places_numeros(self, numeros: List[int]):
        """
        Réserve des places spécifiques identifiées par leur numéro.

        Args:
            numeros (List[int]): La liste des numéros de siège à réserver.

        Raises:
            ValueError: Si un numéro de siège est invalide (hors capacité).
            SallePleineException: Si un siège est déjà occupé ou si le nombre
                de places demandées est supérieur au nombre de places disponibles.
        """
        for p in numeros:
            if p < 1 or p > self.salle.capacite:
                raise ValueError(f"Numéro de place invalide: {p}")
            if p in self.places_occupees:
                raise SallePleineException(f"La place {p} est déjà réservée.")

        if len(numeros) > self.places_disponibles:
            raise SallePleineException(
                f"Impossible : {len(numeros)} places demandées, {self.places_disponibles} restantes."
            )

        self.places_occupees.update(numeros)
        # Maintient la cohérence du compteur global de places réservées.
        self.places_reservees = len(self.places_occupees)

    def liberer_places(self, nombre: int, numeros: Optional[List[int]] = None):
        """
        Libère des places pour cette séance.

        Si des numéros de siège sont fournis, ils sont retirés de l'ensemble des
        places occupées. Sinon, le compteur global est simplement décrémenté.

        Args:
            nombre (int): Le nombre de places à libérer (utilisé en fallback).
            numeros (Optional[List[int]]): La liste des numéros de siège à libérer.
        """
        if numeros:
            self.places_occupees.difference_update(numeros)
            self.places_reservees = len(self.places_occupees)
        else:
            self.places_reservees -= nombre
        
        self.places_reservees = max(0, self.places_reservees)

    def __str__(self):
        heure = self.horaire.strftime("%H:%M")
        etat = "COMPLET" if self.est_complete else f"{self.places_disponibles} places dispo"
        return f"[{heure}] {self.film.titre} en {self.salle.nom} ({self.salle.type_salle.value}) - {etat}"