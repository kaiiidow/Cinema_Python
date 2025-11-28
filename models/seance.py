from dataclasses import dataclass
from datetime import datetime
from .film import Film
from .salle import Salle
from .exceptions import SallePleineException

@dataclass
class Seance:
    id: str
    film: Film
    salle: Salle
    horaire: datetime
    places_reservees: int = 0

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

    def __str__(self):
        heure = self.horaire.strftime("%H:%M")
        etat = "COMPLET" if self.est_complete else f"{self.places_disponibles} places dispo"
        return f"[{heure}] {self.film.titre} en {self.salle.nom} ({self.salle.type_salle.value}) - {etat}"