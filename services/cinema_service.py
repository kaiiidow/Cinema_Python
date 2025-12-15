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
        """
        Initialise le service du cinéma.

        Ce service agit comme une couche de logique métier (business logic) et
        simule une base de données en mémoire pour gérer les films, salles,
        séances et réservations.
        """
        self.films: List[Film] = []
        self.salles: List[Salle] = []
        self.tarifs: List[Tarif] = []
        self.seances: List[Seance] = []
        self.reservations: List[Reservation] = []
        self._init_demo_data()

    def verifier_conflit_seance(self, nouvelle_seance: Seance) -> Optional[Seance]:
        """
        Vérifie si une nouvelle séance entre en conflit avec une séance existante.

        Un conflit se produit si la plage horaire de la nouvelle séance (début à
        fin, durée du film incluse) se chevauche avec celle d'une séance
        existante dans la même salle.

        Args:
            nouvelle_seance (Seance): La nouvelle séance à vérifier.

        Returns:
            Optional[Seance]: La séance en conflit si elle existe, sinon None.
        """
        from datetime import timedelta

        # Heure de début et de fin de la nouvelle séance
        debut_nouvelle = nouvelle_seance.horaire
        fin_nouvelle = debut_nouvelle + timedelta(minutes=nouvelle_seance.film.duree)

        # On ne vérifie que les séances dans la même salle
        for seance_existante in self.seances:
            if seance_existante.salle.numero == nouvelle_seance.salle.numero:
                # Heure de début et de fin de la séance existante
                debut_existante = seance_existante.horaire
                fin_existante = debut_existante + timedelta(minutes=seance_existante.film.duree)

                # Condition de chevauchement d'intervalles: (StartA < EndB) and (StartB < EndA)
                if (debut_nouvelle < fin_existante) and (debut_existante < fin_nouvelle):
                    return seance_existante
        return None

    def _init_demo_data(self):
        """
        Initialise le système avec un jeu de données de démonstration.

        Cette méthode peuple les listes de films, salles, tarifs et séances
        pour permettre de tester l'application sans avoir à tout créer
        manuellement.
        """
        # Catalogue de films de démonstration
        films_data = [
            ("Inception", 148, StyleFilm.SF, 8.8, "inception.jpg", "Dom Cobb est un voleur expérimenté, le meilleur dans l'art dangereux de l'extraction : il vole des secrets précieux enfouis au plus profond du subconscient pendant le rêve. Sa dernière mission est différente : il ne doit pas voler une idée, mais en implanter une. S'il réussit, ce sera le crime parfait."),
            ("Le Roi Lion", 88, StyleFilm.ANIMATION, 8.5, "le-roi-lion.jpg", "Sur les hautes terres d’Afrique, le jeune lionceau Simba est destiné à succéder à son père, le roi Mufasa. Mais son oncle jaloux, Scar, élabore un plan diabolique pour prendre le pouvoir. Exilé, Simba devra affronter son passé et accepter son destin pour reprendre sa place dans le grand cycle de la vie."),
            ("Avatar 2", 192, StyleFilm.SF, 7.9, "avatar-2.jpg", "Plus d'une décennie après les événements du premier film, Jake Sully et Ney'tiri ont fondé une famille. Cependant, leur bonheur est menacé lorsqu'une ancienne menace, la RDA, revient pour achever sa mission. Contraints de fuir, les Sully cherchent refuge auprès du clan Metkayina, un peuple de l'eau, et doivent apprendre à survivre dans un environnement aquatique inconnu."),
            ("Interstellar", 169, StyleFilm.SF, 8.6, "interstellar.jpg", "Dans un futur où la Terre se meurt, un groupe d'explorateurs mené par Cooper, un ancien pilote de la NASA, se voit confier la mission la plus cruciale de l'histoire : voyager à travers un trou de ver récemment découvert pour trouver une nouvelle planète habitable pour l'humanité et assurer sa survie."),
            ("La La Land", 128, StyleFilm.COMEDIE, 8.0, "la-la-land.jpg", "Mia, une actrice en herbe, et Sebastian, un musicien de jazz passionné, se rencontrent à Los Angeles. Alors qu'ils luttent pour joindre les deux bouts, ils s'encouragent mutuellement à poursuivre leurs rêves. Mais à mesure que le succès approche, les choix qu'ils doivent faire menacent de déchirer leur couple et de briser leurs espoirs."),
            ("The Dark Knight", 152, StyleFilm.ACTION, 9.0, "the-dark-knight.jpg", "Avec l'aide du lieutenant Gordon et du procureur Harvey Dent, Batman a réussi à contenir le crime à Gotham. Mais leur succès est de courte durée lorsqu'un nouveau génie du crime, le Joker, apparaît. Sadique et imprévisible, il plonge la ville dans le chaos et force le Chevalier Noir à franchir la fine ligne qui sépare le héros du justicier."),
            ("Coco", 105, StyleFilm.ANIMATION, 8.4, "coco.jpg", "Miguel, un jeune garçon passionné de guitare, est né dans une famille qui a banni la musique. Déterminé à prouver son talent, il se retrouve mystérieusement transporté dans le spectaculaire Pays des Morts. Il y rencontre un charmant filou, Hector, et ensemble, ils se lancent dans un voyage extraordinaire pour découvrir la véritable histoire de la famille de Miguel."),
            ("Parasite", 132, StyleFilm.DRAME, 8.5, "parasite.jpg", "La famille de Ki-taek est au chômage et vit dans un sous-sol miteux. Leur vie bascule lorsque le fils aîné décroche un poste de tuteur pour la fille d'une famille richissime. Usant de ruse, toute la famille parvient à s'infiltrer dans la maison luxueuse, mais leur plan est menacé par un secret inattendu caché dans les murs de la demeure."),
            ("Pulp Fiction", 154, StyleFilm.DRAME, 8.9, "pulp-fiction.jpg", "Ce film culte entremêle plusieurs histoires de criminels à Los Angeles. Suivez les péripéties de deux tueurs à gages philosophes, d'un boxeur en fuite, de la femme d'un gangster qui frôle l'overdose, et d'un couple de braqueurs de diner. Leurs destins se croisent dans une série d'événements violents, comiques et inattendus."),
            ("Forrest Gump", 142, StyleFilm.DRAME, 8.8, "forrest-gump.jpg", "Assis sur un banc, Forrest Gump, un homme simple d'esprit mais au grand cœur, raconte l'histoire extraordinaire de sa vie. De son enfance en Alabama à la guerre du Vietnam, en passant par sa rencontre avec des présidents, Forrest traverse les grands moments de l'histoire américaine sans jamais perdre son optimisme ni l'amour qu'il porte à son amie d'enfance, Jenny."),
            ("The Matrix", 136, StyleFilm.SF, 8.7, "the-matrix.jpg", "Thomas Anderson mène une double vie. Le jour, il est programmeur. La nuit, il est Neo, un pirate informatique. Sa vie bascule lorsqu'il est contacté par Morpheus, qui lui révèle la vérité : le monde qu'il connaît n'est qu'une simulation, la Matrice, créée par des machines pour asservir l'humanité. Neo doit alors choisir de rejoindre la rébellion."),
            ("Le Seigneur des Anneaux : La Communauté de l'Anneau", 178, StyleFilm.SF, 8.8, "le-seigneur-des-anneaux.jpg", "Dans les paisibles terres de la Comté, le jeune hobbit Frodon hérite d'un anneau. Loin d'être un simple bijou, il s'agit de l'Anneau Unique, un instrument de pouvoir absolu qui permettrait à Sauron, le Seigneur des Ténèbres, de régner sur la Terre du Milieu. Frodon doit se lancer dans une quête périlleuse pour le détruire."),
            ("Gladiator", 155, StyleFilm.ACTION, 8.5, "gladiator.jpg", "En l'an 180, le général romain Maximus est trahi par Commode, le fils jaloux de l'empereur. Condamné à mort, il s'échappe mais ne peut sauver sa famille. Capturé et réduit en esclavage, il devient gladiateur. Sa renommée dans l'arène le mènera jusqu'au Colisée de Rome, où il cherchera à accomplir sa vengeance."),
            ("Le Voyage de Chihiro", 125, StyleFilm.ANIMATION, 8.6, "le-voyage-de-chihiro.jpg", "Chihiro, une fillette de dix ans, s'égare avec ses parents et découvre un passage vers un monde peuplé de dieux, d'esprits et de monstres. Lorsque ses parents sont transformés en porcs, Chihiro doit travailler dans un établissement de bains dirigé par la sorcière Yubaba pour survivre et trouver un moyen de rentrer chez elle."),
            ("Le Parrain", 175, StyleFilm.DRAME, 9.2, "le-parrain.jpg", "Don Vito Corleone est le chef respecté et craint de l'une des cinq familles de la mafia de New York. Lorsque son plus jeune fils, Michael, un héros de guerre qui a toujours refusé de s'impliquer dans les affaires familiales, rentre à la maison, une tentative d'assassinat contre son père le force à plonger dans un monde de violence et de trahison."),
            ("Fight Club", 139, StyleFilm.DRAME, 8.8, "fight-club.jpg", "Le narrateur, un employé de bureau souffrant d'insomnie, est désabusé par sa vie consumériste. Sa rencontre avec Tyler Durden, un vendeur de savon charismatique, va tout changer. Ensemble, ils créent le 'Fight Club', un exutoire brutal pour les hommes frustrés, qui va rapidement évoluer en un projet anarchiste d'envergure nationale."),
            ("Les Évadés", 142, StyleFilm.DRAME, 9.3, "les-evades.jpg", "En 1947, Andy Dufresne, un jeune banquier, est condamné à la prison à vie pour un crime qu'il clame ne pas avoir commis. Dans le pénitencier de Shawshank, il se lie d'amitié avec Red, un détenu qui connaît les rouages de la vie carcérale. Au fil des années, Andy utilise son intelligence et son espoir pour survivre et changer la vie de ses codétenus."),
            ("Jurassic Park", 127, StyleFilm.SF, 8.2, "jurassic-park.jpg", "Le milliardaire John Hammond a réussi l'impossible : cloner des dinosaures et créer un parc d'attractions sur une île isolée. Avant l'ouverture, il invite un groupe d'experts pour obtenir leur approbation. Mais une tempête et un acte de sabotage provoquent une panne de courant, libérant les créatures préhistoriques."),
        ]
        
        for titre, duree, style, note, poster, resume in films_data:
            self.films.append(Film(titre, duree, style, note, f"assets/posters/{poster}", resume))

        # Salles de cinéma de démonstration
        salles_data = [
            (1, "L'Odyssée", 100, TypeSalle.CLASSIQUE),
            (2, "Le Grand Large", 50, TypeSalle.IMAX),
            (3, "Dolby Vision", 80, TypeSalle.DOLBY),
            (4, "3D Experience", 60, TypeSalle.TROIS_D),
            (5, "La Petite Salle", 30, TypeSalle.CLASSIQUE)
        ]
        
        for numero, nom, capacite, type_salle in salles_data:
            self.salles.append(Salle(numero, nom, capacite, type_salle))

        # Tarifs de démonstration
        self.tarifs.extend([
            Tarif("Plein tarif", 1.0),
            Tarif("Etudiant", 0.8),
            Tarif("Senior (-65 ans)", 0.9),
            Tarif("Enfant (-14 ans)", 0.6)
        ])

        # Génération de séances de démonstration
        import random
        
        now = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
        horaires_possibles = [10, 14, 17, 20]
        
        seance_id = 1
        for jour in range(3):
            date = now + timedelta(days=jour)
            for film in self.films:
                # Assigner des horaires aléatoires pour varier la programmation
                horaires_film = random.sample(horaires_possibles, k=random.randint(2, 4))
                horaires_film.sort()
                
                for heure in horaires_film:
                    # Randomiser la salle
                    salle = random.choice(self.salles)
                    horaire = date.replace(hour=heure)
                    self.seances.append(Seance(f"S{seance_id:02d}", film, salle, horaire))
                    seance_id += 1

    def get_toutes_seances(self) -> List[Seance]:
        """Retourne la liste de toutes les séances programmées."""
        return self.seances
    
    def get_seances_par_film(self, film_titre: str) -> List[Seance]:
        """
        Filtre les séances pour un film spécifique.

        Args:
            film_titre (str): Le titre du film à rechercher.

        Returns:
            List[Seance]: Une liste des séances correspondant au film.
        """
        return [s for s in self.seances if s.film.titre == film_titre]
    
    def get_seances_disponibles(self) -> List[Seance]:
        """
        Retourne la liste des séances qui ne sont pas complètes.

        Returns:
            List[Seance]: Une liste des séances avec au moins une place disponible.
        """
        return [s for s in self.seances if not s.est_complete]
    
    def get_seances_par_date(self, date: datetime) -> List[Seance]:
        """
        Filtre les séances pour une date spécifique.

        Args:
            date (datetime): La date pour laquelle filtrer les séances.

        Returns:
            List[Seance]: Une liste des séances pour la date donnée.
        """
        return [s for s in self.seances if s.horaire.date() == date.date()]

    def creer_reservation_avec_seance(self, seance: 'Seance', nom_client: str, nb_places: int, tarif: Tarif, numeros_places: Optional[List[int]] = None) -> Reservation:
        """
        Crée et enregistre une nouvelle réservation pour une séance donnée.

        Cette méthode valide les entrées, met à jour l'état d'occupation de la
        séance, et ajoute la nouvelle réservation à la liste globale.

        Args:
            seance (Seance): L'objet séance pour lequel la réservation est faite.
            nom_client (str): Le nom du client.
            nb_places (int): Le nombre de places à réserver.
            tarif (Tarif): Le tarif appliqué à la réservation.
            numeros_places (Optional[List[int]]): La liste des numéros de sièges
                spécifiques choisis par le client.

        Returns:
            Reservation: L'objet réservation nouvellement créé.

        Raises:
            ValueError: Si le nombre de places est invalide.
            SallePleineException: Si la séance est complète ou si les sièges
                demandés sont déjà occupés.
        """
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
        """
        Calcule et retourne des statistiques détaillées sur l'activité du cinéma.

        Les statistiques incluent des données sur les revenus, la popularité des
        films, l'occupation des salles et la répartition des tarifs.

        Returns:
            Dict: Un dictionnaire contenant diverses métriques de performance.
        """
        stats = {
            'total_films': len(self.films),
            'total_salles': len(self.salles),
            'total_seances': len(self.seances),
            'total_reservations': len(self.reservations),
            'total_places_vendues': sum(r.nb_places for r in self.reservations),
            'total_revenus': sum(r.prix_total for r in self.reservations),
            'films_populaires': {},
            'occupation_salles': {},
            'repartition_tarifs': {}
        }
        
        # Agrégation des données par film
        for reservation in self.reservations:
            film = reservation.seance.film.titre
            if film not in stats['films_populaires']:
                stats['films_populaires'][film] = {'places': 0, 'revenus': 0.0}
            stats['films_populaires'][film]['places'] += reservation.nb_places
            stats['films_populaires'][film]['revenus'] += reservation.prix_total
            
        # Agrégation des données par salle
        for seance in self.seances:
            salle = seance.salle.nom
            if salle not in stats['occupation_salles']:
                stats['occupation_salles'][salle] = {
                    'capacite_totale': 0,
                    'places_vendues': 0
                }
            stats['occupation_salles'][salle]['capacite_totale'] += seance.salle.capacite
            stats['occupation_salles'][salle]['places_vendues'] += seance.places_reservees
            
        # Agrégation des données par tarif
        for reservation in self.reservations:
            tarif = reservation.tarif.label
            if tarif not in stats['repartition_tarifs']:
                stats['repartition_tarifs'][tarif] = 0
            stats['repartition_tarifs'][tarif] += reservation.nb_places
            
        return stats
    
    def creer_seances_pour_film(self, film: Film):
        """
        Génère automatiquement un programme de séances pour un nouveau film.

        Crée des séances sur 7 jours avec des horaires et des salles
        sélectionnés aléatoirement pour simuler une programmation rapide.

        Args:
            film (Film): Le film pour lequel générer les séances.
        """
        import random
        
        now = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
        horaires_possibles = [10, 14, 17, 20]
        
        if not self.salles:
            return
        
        seance_id = len(self.seances) + 1
        for jour in range(7):  # 7 jours (1 semaine)
            date = now + timedelta(days=jour)
            horaires_film = random.sample(horaires_possibles, k=random.randint(2, 4))
            horaires_film.sort()
            
            for heure in horaires_film:
                horaire = date.replace(hour=heure)
                # Randomiser la salle pour chaque séance
                salle = random.choice(self.salles)
                self.seances.append(Seance(f"S{seance_id:02d}", film, salle, horaire))
                seance_id += 1
    
    def annuler_reservation(self, reservation_id: str) -> bool:
        """
        Annule une réservation spécifiée par son ID.

        Recherche la réservation, libère les places associées dans la séance
        correspondante, et supprime la réservation de la liste.

        Args:
            reservation_id (str): L'identifiant unique de la réservation à annuler.

        Returns:
            bool: True si l'annulation a réussi, False si la réservation
                  n'a pas été trouvée.
        """
        for i, reservation in enumerate(self.reservations):
            if reservation.id == reservation_id:
                reservation.seance.liberer_places(reservation.nb_places, reservation.numeros_places)
                del self.reservations[i]
                return True
        return False
    
    def rechercher_films(self, terme: str) -> List[Film]:
        """
        Recherche des films par titre de manière non sensible à la casse.

        Args:
            terme (str): Le terme de recherche à trouver dans les titres de films.

        Returns:
            List[Film]: Une liste de films dont le titre contient le terme de recherche.
        """
        terme_lower = terme.lower()
        return [f for f in self.films if terme_lower in f.titre.lower()]