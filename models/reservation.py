from dataclasses import dataclass, field
from datetime import datetime
import uuid

from .seance import Seance
from .enums import Tarif

@dataclass
class Reservation:
    seance: Seance
    client_nom: str
    nb_places: int
    tarif: Tarif
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    date_creation: datetime = field(default_factory=datetime.now)

    @property
    def prix_total(self) -> float:
        PRIX_BASE = 10.00
        # Formule : (Prix Base + Supplément Salle) * Coefficient Tarifaire * Nombre places
        prix_unitaire = (PRIX_BASE + self.seance.salle.supplement_prix) * self.tarif.coeff
        return round(prix_unitaire * self.nb_places, 2)

    def __str__(self):
        return (
            f"Ticket #{self.id} | {self.client_nom}\n"
            f"Film : {self.seance.film.titre}\n"
            f"Salle : {self.seance.salle.nom} ({self.seance.salle.type_salle.value})\n"
            f"Horaire : {self.seance.horaire.strftime('%d/%m à %H:%M')}\n"
            f"Places : {self.nb_places} x {self.tarif.label}\n"
            f"TOTAL : {self.prix_total} €"
        )