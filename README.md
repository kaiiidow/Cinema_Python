# 🎬 Cinema Python - Interface Tkinter

Un système de réservation de cinéma en Python avec interface graphique moderne utilisant Tkinter et programmation orientée objet.

## 🚀 Nouvelles fonctionnalités (v2.0)

- **Interface graphique complète** avec Tkinter
- **4 onglets** : Séances, Réservation, Historique, Statistiques  
- **Visualisation avancée** des séances avec codes couleur
- **Récapitulatif en temps réel** lors de la réservation
- **Statistiques détaillées** du cinéma
- **Plus de données de démonstration** (8 films, 5 salles, 10+ séances)

## 📁 Structure du projet

```
Cinema_Python/
├── main.py              # Interface console avec tkinter basique
├── gui_cinema.py        # Interface graphique complète
├── run_gui.py          # Lanceur simplifié pour l'interface graphique
├── README_TKINTER.md   # Ce fichier (guide pour la version tkinter)
├── models/             # Modèles de données
│   ├── __init__.py
│   ├── enums.py        # Énumérations (Tarif, TypeSalle, StyleFilm)
│   ├── exceptions.py   # Exceptions métier
│   ├── film.py         # Classe Film
│   ├── salle.py        # Classe Salle  
│   ├── seance.py       # Classe Seance
│   └── reservation.py  # Classe Reservation
└── services/           # Services métier
    ├── __init__.py
    └── cinema_service.py # Service principal (amélioré)
```

## 🎯 Utilisation

### Interface Graphique Complète (Recommandée)
```bash
python gui_cinema.py
```

### Lanceur Simplifié
```bash
python run_gui.py
```

### Interface Console avec Tkinter (Version transformée)
```bash
python main.py
```

## 🖥️ Interface Graphique - Guide

### 📅 Onglet "Séances"
- Visualisation de toutes les séances dans un tableau
- **Codes couleur** :
  - 🟢 Vert : Séances avec beaucoup de places
  - 🟡 Jaune : Peu de places restantes  
  - 🔴 Rouge : Séances complètes

### 🎫 Onglet "Réserver"
1. **Sélection de séance** : Cliquez sur la séance désirée
2. **Informations client** : Nom, nombre de places, type de tarif
3. **Récapitulatif temps réel** : Prix calculé automatiquement
4. **Validation** : Bouton "RÉSERVER" pour confirmer

### 📋 Onglet "Historique"
- Liste complète des réservations effectuées
- Détails complets : ticket, client, film, horaire, prix
- Bouton pour effacer l'historique

### 📊 Onglet "Statistiques"
- **Données générales** : nombre de séances, réservations, revenus
- **Films populaires** : classement par nombre de places vendues
- **Répartition des tarifs** : pourcentages d'utilisation
- **Occupation des salles** : taux de remplissage

## 🎭 Données de démonstration

### Films disponibles
- **Inception** (SF, 148 min) - Note: 8.8/10
- **Avatar 2** (SF, 192 min) - Note: 7.9/10  
- **Le Roi Lion** (Animation, 88 min) - Note: 8.5/10
- **Interstellar** (SF, 169 min) - Note: 8.6/10
- **La La Land** (Comédie, 128 min) - Note: 8.0/10
- **The Dark Knight** (Action, 152 min) - Note: 9.0/10
- **Coco** (Animation, 105 min) - Note: 8.4/10
- **Parasite** (Drame, 132 min) - Note: 8.5/10

### Salles disponibles
- **L'Odyssée** (100 places) - Classique
- **Le Grand Large** (50 places) - IMAX
- **Dolby Vision** (80 places) - Dolby Cinema
- **3D Experience** (60 places) - 3D
- **La Petite Salle** (30 places) - Classique

## 💰 Système de tarification

### Types de tarifs
- **Plein tarif** : 100% du prix de base (10€)
- **Étudiant** : 80% du prix de base (-20%)
- **Senior** : 90% du prix de base (-10%) 
- **Enfant** : 60% du prix de base (-40%)

### Suppléments par type de salle
- **Classique** : Prix de base (10€)
- **IMAX/Dolby/3D** : Supplément de +2,50€

### Exemple de calcul
```
Film en salle IMAX avec tarif Étudiant (2 places) :
(10€ + 2,50€) × 0.8 × 2 = 20€
```

## 🔧 Fonctionnalités techniques

### Classes principales

#### Film
```python
@dataclass
class Film:
    titre: str
    duree: int  # en minutes  
    style: StyleFilm
    note: float = 0.0
```

#### Salle
```python
@dataclass  
class Salle:
    numero: int
    nom: str
    capacite: int
    type_salle: TypeSalle = TypeSalle.CLASSIQUE
```

#### Seance
```python
@dataclass
class Seance:
    id: str
    film: Film
    salle: Salle  
    horaire: datetime
    places_reservees: int = 0
```

#### Reservation
```python
@dataclass
class Reservation:
    seance: Seance
    client_nom: str
    nb_places: int
    tarif: Tarif
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    date_creation: datetime = field(default_factory=datetime.now)
```

### Gestion des exceptions
- **CinemaException** : Exception de base
- **SallePleineException** : Séance complète
- **FilmIntrouvableException** : Film non trouvé

## 🎨 Améliorations de l'interface

- **Style moderne** avec thème Clam de ttk
- **Codes couleur** pour l'état des séances
- **Police Courier** pour les données tabulaires  
- **Icônes emoji** pour une meilleure UX
- **Messages de confirmation** détaillés
- **Mise à jour automatique** des vues après réservation

## 📋 Prérequis

- **Python 3.7+**
- **tkinter** (inclus par défaut avec Python)
- Modules standard : `datetime`, `dataclasses`, `enum`, `uuid`

## 🎯 Cas d'usage

1. **Consultation rapide** des séances via l'onglet "Séances"
2. **Réservation guidée** avec récapitulatif temps réel  
3. **Suivi des réservations** dans l'historique
4. **Analyse des performances** via les statistiques
5. **Gestion des erreurs** (salle pleine, données invalides)

## 🚀 Transformation réalisée

Le projet original en ligne de commande a été entièrement transformé en :

### ✅ Version main.py (Tkinter basique)
- Interface graphique simple avec 2 onglets
- Remplacement complet de l'interface console
- Conservation de toute la logique métier

### ✅ Version gui_cinema.py (Tkinter avancée) 
- Interface complète avec 4 onglets
- Fonctionnalités avancées (statistiques, codes couleur)
- Expérience utilisateur optimisée

### ✅ Améliorations du backend
- Service enrichi avec plus de données
- Nouvelles méthodes (statistiques, recherche)
- Gestion améliorée des erreurs

---
*Version 2.0 - Interface Tkinter | Transformation complète réussie 🎉*
