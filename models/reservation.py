from dataclasses import dataclass, field
from datetime import datetime
import uuid
from typing import List

from .seance import Seance

@dataclass
class Tarif:
    label: str
    coeff: float # ex: 1.0 pour plein, 0.8 pour étudiant

    def __str__(self):
        return f"{self.label} ({self.coeff*100:.0f}%)"

@dataclass
class Reservation:
    seance: Seance
    client_nom: str
    nb_places: int
    tarif: Tarif
    numeros_places: List[int] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    date_creation: datetime = field(default_factory=datetime.now)

    @property
    def prix_total(self) -> float:
        PRIX_BASE = 10.00
        # Formule : (Prix Base + Supplément Salle) * Coefficient Tarifaire * Nombre places
        prix_unitaire = (PRIX_BASE + self.seance.salle.supplement_prix) * self.tarif.coeff
        return round(prix_unitaire * self.nb_places, 2)

    def __str__(self):
        sieges_str = f" (Sièges: {', '.join(map(str, sorted(self.numeros_places)))})" if self.numeros_places else ""
        return (
            f"Ticket #{self.id} | {self.client_nom}\n"
            f"Film : {self.seance.film.titre}\n"
            f"Salle : {self.seance.salle.nom} ({self.seance.salle.type_salle.value})\n"
            f"Horaire : {self.seance.horaire.strftime('%d/%m à %H:%M')}\n"
            f"Places : {self.nb_places} x {self.tarif.label}{sieges_str}\n"
            f"TOTAL : {self.prix_total} €"
        )