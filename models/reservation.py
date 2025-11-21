from dataclasses import dataclass

from .film import Film
from .salle import Salle


@dataclass
class Reservation:
    """Représente une demande de réservation qui n'a pas encore été confirmée."""
    film: Film
    salle: Salle
    nb_places: int

    def __post_init__(self) -> None:
        """Valide les données de la réservation à sa création."""
        if self.nb_places <= 0:
            raise ValueError("Le nombre de places doit être strictement positif.")

    def confirmer(self) -> None:
        """Confirme la réservation en mettant à jour la salle."""
        self.salle.reserver(self.nb_places)
        print(f"Réservation confirmée : {self}")

    def __str__(self) -> str:
        return (
            f"Réservation de {self.nb_places} places pour '{self.film.titre}' "
            f"dans la salle {self.salle.numero}"
        )
