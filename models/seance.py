from datetime import datetime
from exceptions.film_inexistant import FilmInexistantException

class Seance:
    def __init__(self,film,salle,horaire: datetime):
        if film is None:
            raise FilmInexistantException("Film inexistant !")
        self.film = film
        self.salle = salle
        self.horaire = horaire
        self.reservations = []


    def reserver(self, nb_places: int):
        """Crée une réservation pour cette séance."""
        from models.reservation import Reservation  # import local pour éviter les import circulaires
        reservation = Reservation(self.film, self.salle, nb_places)
        self.reservations.append(reservation)
        return reservation

    def places_restantes(self):
        """Retourne le nombre de places encore disponibles dans la salle."""
        return self.salle.capacite - self.salle.places_reservees

    def __str__(self):
        return f"Séance de '{self.film.titre}' le {self.horaire.strftime('%d/%m/%Y')} à {self.horaire.strftime('%H:%M')} dans {self.salle}"
            