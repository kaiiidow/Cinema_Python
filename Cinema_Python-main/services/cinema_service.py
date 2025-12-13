from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json

from models.film import Film
from models.salle import Salle
from models.seance import Seance
from models.reservation import Reservation, Tarif
from models.enums import StyleFilm, TypeSalle

class CinemaService:
    def __init__(self):
        # Simulation de base de données
        self.films: List[Film] = []
        self.salles: List[Salle] = []
        self.tarifs: List[Tarif] = []
        self.seances: List[Seance] = []
        self.reservations: List[Reservation] = []
        # Pool global de places occupées par (film_titre, date)
        self.places_occupees_globales: Dict[tuple, set] = {}
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

        # Création Tarifs
        self.tarifs.extend([
            Tarif("Plein tarif", 1.0),
            Tarif("Etudiant", 0.8),
            Tarif("Senior (-65 ans)", 0.9),
            Tarif("Enfant (-14 ans)", 0.6)
        ])

        # Création Séances variées (horaires randomisés par film, 3 jours)
        import random
        
        now = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
        horaires_possibles = [10, 14, 17, 20]  # Horaires possibles
        
        seance_id = 1
        for jour in range(3):  # 3 jours
            date = now + timedelta(days=jour)
            for film in self.films:
                # Randomiser les horaires pour chaque film
                horaires_film = random.sample(horaires_possibles, k=random.randint(2, 4))
                horaires_film.sort()
                
                for heure in horaires_film:
                    # Randomiser la salle
                    salle = random.choice(self.salles)
                    horaire = date.replace(hour=heure)
                    self.seances.append(Seance(f"S{seance_id:02d}", film, salle, horaire))
                    seance_id += 1

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

    def creer_reservation(self, seance_index: int, nom_client: str, nb_places: int, tarif: Tarif, numeros_places: Optional[List[int]] = None,) -> Reservation:
        """Gère la logique d'une réservation complète."""
        if not (0 <= seance_index < len(self.seances)):
             raise IndexError("Séance invalide")
             
        seance = self.seances[seance_index]
        
        if nb_places <= 0:
            raise ValueError("Il faut réserver au moins 1 place.")

        if numeros_places is not None:
            if len(numeros_places) != nb_places:
                raise ValueError("Le nombre de places ne correspond pas au nombre de sièges choisis.")
            seance.reserver_places_numeros(numeros_places)
        else:
            seance.reserver_places(nb_places)

        # Cette méthode lève une exception si la salle est pleine
        #seance.reserver_places(nb_places)
        
        resa = Reservation(seance, nom_client, nb_places, tarif, numeros_places=numeros_places if numeros_places is not None else [])
        self.reservations.append(resa)
        return resa
    
    def creer_reservation_avec_seance(self, seance: 'Seance', nom_client: str, nb_places: int, tarif: Tarif, numeros_places: Optional[List[int]] = None) -> Reservation:
        """Crée une réservation directement avec l'objet séance (plus simple que par index)."""
        if nb_places <= 0:
            raise ValueError("Il faut réserver au moins 1 place.")

        if numeros_places is not None:
            if len(numeros_places) != nb_places:
                raise ValueError("Le nombre de places ne correspond pas au nombre de sièges choisis.")
            seance.reserver_places_numeros(numeros_places)
        else:
            seance.reserver_places(nb_places)
        
        resa = Reservation(seance, nom_client, nb_places, tarif, numeros_places=numeros_places if numeros_places is not None else [])
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
    
    def creer_seances_pour_film(self, film: Film):
        """Crée automatiquement des séances avec horaires et salles randomisés sur 7 jours."""
        import random
        
        now = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
        horaires_possibles = [10, 14, 17, 20]
        
        if not self.salles:
            return  # Pas de salle disponible
        
        seance_id = len(self.seances) + 1
        for jour in range(7):  # 7 jours (1 semaine)
            date = now + timedelta(days=jour)
            # Randomiser les horaires pour ce film
            horaires_film = random.sample(horaires_possibles, k=random.randint(2, 4))
            horaires_film.sort()
            
            for heure in horaires_film:
                horaire = date.replace(hour=heure)
                # Randomiser la salle pour chaque séance
                salle = random.choice(self.salles)
                self.seances.append(Seance(f"S{seance_id:02d}", film, salle, horaire))
                seance_id += 1
    
    def annuler_reservation(self, reservation_id: str) -> bool:
        """Annule une réservation et libère les places."""
        for i, reservation in enumerate(self.reservations):
            if reservation.id == reservation_id:
                # Libérer les places
                if hasattr(reservation, 'numeros_places') and reservation.numeros_places:
                    reservation.seance.places_occupees.difference_update(reservation.numeros_places)
                    reservation.seance.places_reservees = len(reservation.seance.places_occupees)
                else:
                    # Fallback pour les anciennes réservations ou celles sans numéros de siège
                    reservation.seance.places_reservees -= reservation.nb_places
                # Supprimer la réservation
                del self.reservations[i]
                return True
        return False
    
    def rechercher_films(self, terme: str) -> List[Film]:
        """Recherche des films par titre."""
        terme_lower = terme.lower()
        return [f for f in self.films if terme_lower in f.titre.lower()]