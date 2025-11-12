from exceptions.seance_inexistant import SeanceInexistantException

# class Reservation:
#     def __init__(self, film, salle, nb_places: int):
#         if film is None:
#             raise FilmInexistantException("Film inexistant !")
#         salle.reserver(nb_places)
#         self.film = film
#         self.salle = salle
#         self.nb_places = nb_places
#         print(f"✅ Réservation de {nb_places} places pour '{film.titre}' dans la salle {salle.numero}")

class Reservation: 
    def __init__(self, seance, nb_places: int):
        if seance is None:
            raise SeanceInexistantException("Séance inexistant !")
        seance.salle.reserver(nb_places)
        self.seance = seance
        self.nb_places = nb_places
        # seance.reservations.append(self)
        print(f"✅ Réservation de {nb_places} places pour '{seance.film.titre}' dans la salle {seance.salle.numero}")
