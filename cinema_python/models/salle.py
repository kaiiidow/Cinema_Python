from exceptions.salle_pleine import SallePleineException


class Salle:
    def __init__(
        self,
        numero: int,
        nb_rangees: int,
        nb_sieges_par_rangee: int,
        type_salle: str = "classique",
    ) -> None:
        if nb_rangees <= 0 or nb_sieges_par_rangee <= 0:
            raise ValueError("Le nombre de rangées et de sièges doit être positif.")

        self.numero = numero
        self.nb_rangees = nb_rangees
        self.nb_sieges_par_rangee = nb_sieges_par_rangee
        self.type_salle = type_salle

        self.capacite = nb_rangees * nb_sieges_par_rangee
        self.places_reservees = 0

    @property
    def places_disponibles(self) -> int:
        return self.capacite - self.places_reservees

    def reserver(self, nb_places: int) -> None:
        """Réserve un nombre de places dans la salle.

        Lève SallePleineException si pas assez de places restantes.
        """
        if nb_places <= 0:
            raise ValueError("Le nombre de places réservées doit être positif.")

        if nb_places > self.places_disponibles:
            raise SallePleineException(
                f"Salle {self.numero} pleine ou pas assez de places "
                f"(demandé : {nb_places}, disponibles : {self.places_disponibles})"
            )

        self.places_reservees += nb_places

    def __str__(self) -> str:
        return (
            f"Salle {self.numero} ({self.type_salle}) - "
            f"{self.places_reservees}/{self.capacite} places réservées"
        )
