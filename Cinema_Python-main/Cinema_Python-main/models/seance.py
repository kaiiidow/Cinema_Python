from dataclasses import dataclass
from datetime import datetime
from .film import Film
from .salle import Salle
from .exceptions import SallePleineException
from dataclasses import dataclass, field
from typing import Set, List

@dataclass
class Seance:
    id: str
    film: Film
    salle: Salle
    horaire: datetime
    places_reservees: int = 0
    places_occupees: Set[int] = field(default_factory=set)

    @property
    def places_disponibles(self) -> int:
        return self.salle.capacite - self.places_reservees

    @property
    def est_complete(self) -> bool:
        return self.places_disponibles <= 0

    def reserver_places(self, nombre: int):
        """Tente de bloquer des places pour cette séance."""
        if nombre > self.places_disponibles:
            raise SallePleineException(
                f"Impossible : {nombre} places demandées, {self.places_disponibles} restantes."
            )
        self.places_reservees += nombre
    
    def reserver_places_numeros(self, numeros: List[int]):
        """
        Réserve des places identifiées par leur numéro (1..capacité).
        Utilisé par l'interface graphique avec plan de salle.
        """
        # Vérif basique
        for p in numeros:
            if p < 1 or p > self.salle.capacite:
                raise ValueError(f"Numéro de place invalide: {p}")
            if p in self.places_occupees:
                raise SallePleineException(f"La place {p} est déjà réservée.")

        if len(numeros) > self.places_disponibles:
            raise SallePleineException(
                f"Impossible : {len(numeros)} places demandées, {self.places_disponibles} restantes."
            )

        # On ajoute les sièges
        self.places_occupees.update(numeros)
        # On garde places_reservees cohérent pour les stats
        self.places_reservees = len(self.places_occupees)

    def __str__(self):
        heure = self.horaire.strftime("%H:%M")
        etat = "COMPLET" if self.est_complete else f"{self.places_disponibles} places dispo"
        return f"[{heure}] {self.film.titre} en {self.salle.nom} ({self.salle.type_salle.value}) - {etat}"