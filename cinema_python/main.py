from models import Film, Salle, Reservation
from exceptions import SallePleineException, FilmInexistantException


def creer_films_de_demo() -> list[Film]:
    """Crée quelques films pour tester l'application."""
    return [
        Film("Inception", 148, 8.8, "Science-fiction"),
        Film("Interstellar", 169, 8.6, "Science-fiction"),
        Film("Le Roi Lion", 88, 8.5, "Animation"),
    ]


def creer_salles_de_demo() -> list[Salle]:
    """Crée quelques salles pour tester l'application."""
    return [
        Salle(1, 10, 10, "classique"),    # 100 places
        Salle(2, 8, 15, "IMAX"),          # 120 places
        Salle(3, 5, 20, "3D"),            # 100 places
    ]


def afficher_films(films: list[Film]) -> None:
    print("\n=== Liste des films ===")
    for i, film in enumerate(films, start=1):
        print(f"{i}. {film}")
    print()


def afficher_salles(salles: list[Salle]) -> None:
    print("\n=== Liste des salles ===")
    for i, salle in enumerate(salles, start=1):
        print(
            f"{i}. Salle {salle.numero} ({salle.type_salle}) "
            f"- {salle.places_reservees}/{salle.capacite} réservées "
            f"- {salle.places_disponibles} dispo"
        )
    print()


def demander_choix(max_index: int, message: str = "Votre choix : ") -> int:
    while True:
        try:
            choix = int(input(message))
            if 1 <= choix <= max_index:
                return choix
            print(f"Veuillez entrer un nombre entre 1 et {max_index}.")
        except ValueError:
            print("Entrée invalide, veuillez entrer un nombre.")


def faire_reservation(films: list[Film], salles: list[Salle]) -> None:
    if not films:
        print("Aucun film disponible.")
        return
    if not salles:
        print("Aucune salle disponible.")
        return

    afficher_films(films)
    choix_film = demander_choix(len(films), "Choisissez un film : ")
    film = films[choix_film - 1]

    afficher_salles(salles)
    choix_salle = demander_choix(len(salles), "Choisissez une salle : ")
    salle = salles[choix_salle - 1]

    while True:
        try:
            nb_places = int(input("Nombre de places à réserver : "))
            if nb_places <= 0:
                print("Le nombre de places doit être positif.")
                continue
            break
        except ValueError:
            print("Entrée invalide, veuillez entrer un nombre.")

    try:
        reservation = Reservation(film, salle, nb_places)
        print(f"✅ {reservation}")
    except SallePleineException as e:
        print(f"❌ Erreur de réservation : {e}")
    except FilmInexistantException as e:
        print(f"❌ Erreur de film : {e}")
    except ValueError as e:
        print(f"❌ Erreur de saisie : {e}")


def menu() -> None:
    films = creer_films_de_demo()
    salles = creer_salles_de_demo()

    while True:
        print("\n=== Système de réservation cinéma ===")
        print("1. Afficher les films")
        print("2. Afficher les salles")
        print("3. Faire une réservation")
        print("4. Quitter")

        choix = input("Votre choix : ").strip()
        if choix == "1":
            afficher_films(films)
        elif choix == "2":
            afficher_salles(salles)
        elif choix == "3":
            faire_reservation(films, salles)
        elif choix == "4":
            print("Au revoir !")
            break
        else:
            print("Choix invalide, veuillez réessayer.")


if __name__ == "__main__":
    menu()
