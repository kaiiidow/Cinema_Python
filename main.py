from models.film import Film
from models.salle import Salle
from models.reservation import Reservation
from exceptions.salle_pleine import SallePleineException
from exceptions.film_inexistant import FilmInexistantException

def main():
    # Création des objets
    film1 = Film("Inception", 148)
    salle1 = Salle(1, 10, 10, "classique")

    # Tentative de réservations
    try:
        Reservation(film1, salle1, 40)
        Reservation(film1, salle1, 15)  # Salle pleine ici
    except SallePleineException as e:
        print(f"❌ Erreur : {e}")
    except FilmInexistantException as e:
        print(f"❌ Erreur : {e}")

if __name__ == "__main__":
    main()


