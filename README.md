# 🎬 Cinéma Deluxe - Système de Gestion et Réservation
Bienvenue sur le projet **Cinéma Deluxe**, une application de bureau complète pour la gestion et la réservation de séances de cinéma, développée en Python avec l'interface graphique Tkinter.

Ce projet simule un système de cinéma moderne, offrant une interface intuitive pour les clients et un panneau de contrôle puissant pour les administrateurs. Il a été conçu pour démontrer l'application des principes de génie logiciel (conception modulaire, séparation des préoccupations) dans un contexte réel et interactif.

---

## ✨ Aperçu de l'Interface


| Vue Principale des Séances | Sélection des Sièges | Panneau Manager |
| :------------------------: | :--------------------: | :---------------: |
| ![Aperçu des séances](https://via.placeholder.com/400x250.png?text=Vue+Principale) | ![Sélection des sièges](https://via.placeholder.com/400x250.png?text=Sélection+des+Sièges) | ![Panneau Manager](https://via.placeholder.com/400x250.png?text=Panneau+Manager) |

---

## 🚀 Fonctionnalités Clés

Le système est divisé en deux expériences distinctes pour répondre aux besoins de chaque type d'utilisateur.

### 👤 Espace Client

Une interface épurée et intuitive pour une réservation sans effort.

- **Navigation Facile :** Consultez les films à l'affiche et naviguez entre les jours de la semaine.
- **Disponibilité en Temps Réel :** Des barres de progression visuelles indiquent le taux de remplissage de chaque séance.
- **Plan de Salle Interactif :** Choisissez vos sièges préférés directement sur un plan de la salle, avec une distinction claire entre les places libres, occupées et sélectionnées.
- **Historique Personnel :** Gardez une trace de toutes vos réservations.

### ⚙️ Panneau Manager

Un centre de contrôle complet pour une gestion totale du cinéma.

- **Gestion des Films :** CRUD (Créer, Lire, Mettre à jour, Supprimer) complet pour le catalogue de films, incluant titre, durée, genre, note et synopsis.
- **Gestion des Salles :** Gérez les salles, leur capacité et leur type (Classique, IMAX, Dolby, etc.).
- **Gestion des Séances :**
    - Planifiez de nouvelles séances avec une grande flexibilité.
    - Visualisez les séances existantes dans une **vue hiérarchique intelligente** (Jour → Film → Séance) pour une lisibilité optimale.
- **Gestion des Tarifs :** Définissez et ajustez dynamiquement les tarifs (Plein, Étudiant, Senior...).
- **Rapports et Analytiques :** Accédez à des statistiques détaillées sur les revenus, les films les plus populaires et le taux d'occupation pour prendre des décisions éclairées.

---

## 🛠️ Architecture et Technologies

Le projet suit une architecture inspirée du modèle MVC (Modèle-Vue-Contrôleur) pour garantir une séparation claire des préoccupations et faciliter la maintenance.

- **Langage :** **Python 3**
- **Interface Graphique :** **Tkinter** (avec le module `ttk` pour un style moderne et des widgets thématiques).
- **Structure des Données :** Utilisation des `dataclasses` pour des modèles de données clairs et robustes.

### Structure du Projet

```
.
├── models/         # Structures de données (Film, Salle, Seance...)
│   ├── enums.py
│   ├── exceptions.py
│   └── ...
├── services/       # Logique métier (CinemaService)
│   └── cinema_service.py
├── gui_cinema.py   # Couche de présentation (toute la logique de l'interface)
└── run_gui.py      # Point d'entrée de l'application
```

---

## 🏃 Démarrage Rapide

Suivez ces étapes pour lancer l'application sur votre machine.

### Prérequis

- **Python 3.7 ou supérieur.**
- Le module `tkinter` doit être installé (il est généralement inclus par défaut avec Python).

### Installation et Lancement

1.  **Clonez le dépôt sur votre machine locale :**
   ```bash
   git clone <URL_DU_DEPOT>
   ```

2.  **Naviguez vers le répertoire du projet :**
   ```bash
   cd Cinema_Python-main
   ```

3.  **Exécutez le script principal :**
   > L'application est conçue pour se lancer en mode plein écran pour une expérience immersive.
    ```bash
    python run_gui.py
    ```

---