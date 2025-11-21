from datetime import datetime, timedelta
from typing import List

from models.film import Film
from models.salle import Salle
from models.seance import Seance
from models.reservation import Reservation
from models.enums import StyleFilm, TypeSalle, Tarif

class CinemaService:
    def __init__(self):
        # Simulation de base de données
        self.films: List[Film] = []
        self.salles: List[Salle] = []
        self.seances: List[Seance] = []
        self.reservations: List[Reservation] = []
        self._init_demo_data()

    def _init_demo_data(self):
        """Crée quelques données pour tester directement."""
        # Création Films
        f1 = Film("Inception", 148, StyleFilm.SF, 8.8)
        f2 = Film("Le Roi Lion", 88, StyleFilm.ANIMATION, 8.5)
        f3 = Film("Avatar 2", 192, StyleFilm.SF, 7.9)
        self.films.extend([f1, f2, f3])

        # Création Salles
        s1 = Salle(1, "L'Odyssée", 100, TypeSalle.CLASSIQUE)
        s2 = Salle(2, "Le Grand Large", 50, TypeSalle.IMAX)
        self.salles.extend([s1, s2])

        # Création Séances (aujourd'hui)
        now = datetime.now().replace(minute=0, second=0, microsecond=0)
        
        self.seances.append(Seance("S1", f1, s1, now + timedelta(hours=1))) # Dans 1h
        self.seances.append(Seance("S2", f3, s2, now + timedelta(hours=2))) # Dans 2h
        self.seances.append(Seance("S3", f2, s1, now + timedelta(hours=4))) # Dans 4h

    def get_films(self) -> List[Film]:
        return self.films

    def get_toutes_seances(self) -> List[Seance]:
        return self.seances

    def creer_reservation(self, seance_index: int, nom_client: str, nb_places: int, tarif: Tarif) -> Reservation:
        """Gère la logique d'une réservation complète."""
        if not (0 <= seance_index < len(self.seances)):
             raise IndexError("Séance invalide")
             
        seance = self.seances[seance_index]
        
        if nb_places <= 0:
            raise ValueError("Il faut réserver au moins 1 place.")
            
        # Cette méthode lève une exception si la salle est pleine
        seance.reserver_places(nb_places)
        
        resa = Reservation(seance, nom_client, nb_places, tarif)
        self.reservations.append(resa)
        return resa