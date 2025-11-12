import curses
from datetime import datetime
from models.film import Film
from models.salle import Salle
from models.seance import Seance
from models.reservation import Reservation
from exceptions.salle_pleine import SallePleineException
from exceptions.film_inexistant import FilmInexistantException
from exceptions.seance_inexistant import SeanceInexistantException

def main():
# Création des objets


    film1 = Film("Inception", 148, 9, "Sci-Fi")

    salle1 = Salle(1, 10, 10, "Classique")

    seance1 = Seance(film1,salle1, datetime(2025, 11, 12, 20, 30))

    try:
        Reservation(seance1, 120)
    except SallePleineException as e:
        print(f"❌ Erreur : {e}")
    except FilmInexistantException as e:
        print(f"❌ Erreur : {e}")

if __name__ == "__main__":
    main()