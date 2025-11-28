from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json

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
        # Création Films plus variés
        films_data = [
            ("Inception", 148, StyleFilm.SF, 8.8),
            ("Le Roi Lion", 88, StyleFilm.ANIMATION, 8.5),
            ("Avatar 2", 192, StyleFilm.SF, 7.9),
            ("Interstellar", 169, StyleFilm.SF, 8.6),
            ("La La Land", 128, StyleFilm.COMEDIE, 8.0),
            ("The Dark Knight", 152, StyleFilm.ACTION, 9.0),
            ("Coco", 105, StyleFilm.ANIMATION, 8.4),
            ("Parasite", 132, StyleFilm.DRAME, 8.5)
        ]
        
        for titre, duree, style, note in films_data:
            self.films.append(Film(titre, duree, style, note))

        # Création Salles variées
        salles_data = [
            (1, "L'Odyssée", 100, TypeSalle.CLASSIQUE),
            (2, "Le Grand Large", 50, TypeSalle.IMAX),
            (3, "Dolby Vision", 80, TypeSalle.DOLBY),
            (4, "3D Experience", 60, TypeSalle.TROIS_D),
            (5, "La Petite Salle", 30, TypeSalle.CLASSIQUE)
        ]
        
        for numero, nom, capacite, type_salle in salles_data:
            self.salles.append(Salle(numero, nom, capacite, type_salle))

        # Création Séances variées (sur 2 jours)
        now = datetime.now().replace(minute=0, second=0, microsecond=0)
        
        # Séances d'aujourd'hui
        seances_data = [
            (self.films[0], self.salles[0], 1),   # Inception dans 1h
            (self.films[2], self.salles[1], 2),   # Avatar 2 dans 2h
            (self.films[1], self.salles[4], 3),   # Le Roi Lion dans 3h
            (self.films[3], self.salles[2], 4),   # Interstellar dans 4h
            (self.films[4], self.salles[0], 5),   # La La Land dans 5h
            (self.films[5], self.salles[1], 6),   # Dark Knight dans 6h
            # Séances du lendemain
            (self.films[6], self.salles[4], 25),  # Coco demain 1h
            (self.films[7], self.salles[2], 26),  # Parasite demain 2h
            (self.films[0], self.salles[3], 27),  # Inception 3D demain 3h
            (self.films[2], self.salles[1], 28),  # Avatar 2 IMAX demain 4h
        ]
        
        for i, (film, salle, heure_offset) in enumerate(seances_data):
            seance_id = f"S{i+1:02d}"
            horaire = now + timedelta(hours=heure_offset)
            self.seances.append(Seance(seance_id, film, salle, horaire))

    def get_films(self) -> List[Film]:
        return self.films

    def get_salles(self) -> List[Salle]:
        return self.salles

    def get_toutes_seances(self) -> List[Seance]:
        return self.seances
    
    def get_seances_par_film(self, film_titre: str) -> List[Seance]:
        """Retourne toutes les séances pour un film donné."""
        return [s for s in self.seances if s.film.titre == film_titre]
    
    def get_seances_disponibles(self) -> List[Seance]:
        """Retourne seulement les séances avec des places disponibles."""
        return [s for s in self.seances if not s.est_complete]
    
    def get_seances_par_date(self, date: datetime) -> List[Seance]:
        """Retourne les séances d'une date donnée."""
        return [s for s in self.seances if s.horaire.date() == date.date()]

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
    
    def get_statistiques(self) -> Dict:
        """Retourne des statistiques détaillées sur le cinéma."""
        stats = {
            'total_seances': len(self.seances),
            'total_reservations': len(self.reservations),
            'total_places_vendues': sum(r.nb_places for r in self.reservations),
            'total_revenus': sum(r.prix_total for r in self.reservations),
            'films_populaires': {},
            'occupation_salles': {},
            'repartition_tarifs': {}
        }
        
        # Films populaires
        for reservation in self.reservations:
            film = reservation.seance.film.titre
            if film not in stats['films_populaires']:
                stats['films_populaires'][film] = 0
            stats['films_populaires'][film] += reservation.nb_places
            
        # Occupation des salles
        for seance in self.seances:
            salle = seance.salle.nom
            if salle not in stats['occupation_salles']:
                stats['occupation_salles'][salle] = {
                    'capacite': seance.salle.capacite,
                    'occupee': 0
                }
            stats['occupation_salles'][salle]['occupee'] += seance.places_reservees
            
        # Répartition des tarifs
        for reservation in self.reservations:
            tarif = reservation.tarif.label
            if tarif not in stats['repartition_tarifs']:
                stats['repartition_tarifs'][tarif] = 0
            stats['repartition_tarifs'][tarif] += reservation.nb_places
            
        return stats
    
    def annuler_reservation(self, reservation_id: str) -> bool:
        """Annule une réservation et libère les places."""
        for i, reservation in enumerate(self.reservations):
            if reservation.id == reservation_id:
                # Libérer les places
                reservation.seance.places_reservees -= reservation.nb_places
                # Supprimer la réservation
                del self.reservations[i]
                return True
        return False
    
    def rechercher_films(self, terme: str) -> List[Film]:
        """Recherche des films par titre."""
        terme_lower = terme.lower()
        return [f for f in self.films if terme_lower in f.titre.lower()]