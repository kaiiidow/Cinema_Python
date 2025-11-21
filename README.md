# Système de réservation de cinéma (Python)

Petit projet de gestion de réservations de places de cinéma en Python.

## Fonctionnalités

- Modélisation de :
  - **Film** (titre, durée, style, note)
  - **Salle** (numéro, type, capacité, places réservées)
  - **Reservation** (film, salle, nombre de places)
- Gestion d’exceptions :
  - `SallePleineException` quand il n’y a plus assez de places
  - `FilmInexistantException` quand un film n’est pas trouvé
- Petite interface **console** pour :
  - Afficher les films disponibles
  - Afficher les salles et leur occupation
  - Faire une réservation de places

## Lancer le projet

```bash
python main.py
```

Python 3.10+ recommandé.
