from dataclasses import dataclass, field
from datetime import datetime
import uuid
from typing import List

from .seance import Seance

@dataclass
class Tarif:
    """
    Représente un type de tarif avec un coefficient de réduction.

    Attributes:
        label (str): Le nom du tarif (ex: "Plein tarif", "Étudiant").
        coeff (float): Le coefficient multiplicateur appliqué au prix de base.
            (ex: 1.0 pour 100%, 0.8 pour 80%).
    """
    label: str
    coeff: float

    def __str__(self):
        """Retourne une représentation textuelle du tarif."""
        return f"{self.label} ({self.coeff*100:.0f}%)"

@dataclass
class Reservation:
    """
    Représente une réservation effectuée par un client pour une séance.

    Attributes:
        seance (Seance): La séance concernée par la réservation.
        client_nom (str): Le nom du client ayant effectué la réservation.
        nb_places (int): Le nombre de places réservées.
        tarif (Tarif): Le tarif appliqué.
        numeros_places (List[int]): Liste des numéros de sièges spécifiques.
        id (str): Un identifiant unique généré pour la réservation.
        date_creation (datetime): La date et l'heure de la création de la réservation.
    """
    seance: Seance
    client_nom: str
    nb_places: int
    tarif: Tarif
    numeros_places: List[int] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    date_creation: datetime = field(default_factory=datetime.now)

    @property
    def prix_total(self) -> float:
        """
        Calcule le prix total de la réservation.

        Le calcul se base sur un prix de base, un éventuel supplément de salle,
        le coefficient du tarif et le nombre de places.
        """
        PRIX_BASE = 10.00
        prix_unitaire = (PRIX_BASE + self.seance.salle.supplement_prix) * self.tarif.coeff
        return round(prix_unitaire * self.nb_places, 2)

    def __str__(self):
        """Retourne une représentation textuelle formatée du ticket de réservation."""
        sieges_str = f" (Sièges: {', '.join(map(str, sorted(self.numeros_places)))})" if self.numeros_places else ""
        return (
            f"Ticket #{self.id} | {self.client_nom}\n"
            f"Film : {self.seance.film.titre}\n"
            f"Salle : {self.seance.salle.nom} ({self.seance.salle.type_salle.value})\n"
            f"Horaire : {self.seance.horaire.strftime('%d/%m à %H:%M')}\n"
            f"Places : {self.nb_places} x {self.tarif.label}{sieges_str}\n"
            f"TOTAL : {self.prix_total} €"
        )