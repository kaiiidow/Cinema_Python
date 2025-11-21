from dataclasses import dataclass

from exceptions.film_inexistant import FilmInexistantException
from .film import Film
from .salle import Salle


@dataclass
class Reservation:
    film: Film
    salle: Salle
    nb_places: int

    def __post_init__(self) -> None:
        if self.film is None:
            raise FilmInexistantException("Film inexistant !")

        if self.nb_places <= 0:
            raise ValueError("Le nombre de places doit être strictement positif.")

        # On tente la réservation dans la salle
        self.salle.reserver(self.nb_places)

    def __str__(self) -> str:
        return (
            f"Réservation de {self.nb_places} places pour '{self.film.titre}' "
            f"dans la salle {self.salle.numero}"
        )
