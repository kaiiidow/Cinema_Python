from exceptions.film_inexistant import FilmInexistantException

class Reservation:
    def __init__(self, film, salle, nb_places: int):
        if film is None:
            raise FilmInexistantException("Film inexistant !")
        salle.reserver(nb_places)
        self.film = film
        self.salle = salle
        self.nb_places = nb_places
        print(f"✅ Réservation de {nb_places} places pour '{film.titre}' dans la salle {salle.numero}")
