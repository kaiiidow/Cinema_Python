import sys
from services.cinema_service import CinemaService
from models.enums import Tarif
from models.exceptions import CinemaException

def afficher_titre():
    print("\n" + "="*40)
    print("   🎬 SYSTÈME DE RÉSERVATION CINÉMA")
    print("="*40)

def menu_choix_seance(service: CinemaService):
    print("\n--- Séances disponibles ---")
    seances = service.get_toutes_seances()
    for i, s in enumerate(seances, 1):
        print(f"{i}. {s}")
    
    try:
        choix = int(input("\nVotre choix de séance (numéro) : "))
        if 1 <= choix <= len(seances):
            return seances[choix - 1], choix - 1
        print("Numéro invalide.")
        return None, None
    except ValueError:
        print("Veuillez entrer un nombre.")
        return None, None

def menu_choix_tarif():
    print("\n--- Tarifs ---")
    tarifs = list(Tarif)
    for i, t in enumerate(tarifs, 1):
        print(f"{i}. {t.label}")
    
    try:
        choix = int(input("Votre tarif : "))
        if 1 <= choix <= len(tarifs):
            return tarifs[choix - 1]
    except ValueError:
        pass
    print("Choix par défaut : Plein Tarif")
    return Tarif.PLEIN

def main():
    service = CinemaService()
    
    while True:
        afficher_titre()
        print("1. Voir les séances et réserver")
        print("2. Voir mes réservations (Session actuelle)")
        print("3. Quitter")
        
        choix = input("\nVotre choix > ")
        
        if choix == "1":
            # Étape 1 : Choisir Séance
            seance, index = menu_choix_seance(service)
            if not seance: continue
            
            # Étape 2 : Infos Client
            print(f"\nVous avez choisi : {seance.film.titre}")
            try:
                nb = int(input("Nombre de places : "))
                nom = input("Votre nom : ")
                tarif = menu_choix_tarif()
                
                # Étape 3 : Appel au Service
                reservation = service.creer_reservation(index, nom, nb, tarif)
                
                print("\n" + "✅"*10 + " SUCCÈS " + "✅"*10)
                print(reservation)
                input("\nAppuyez sur Entrée pour continuer...")
                
            except CinemaException as e:
                print(f"\n❌ ERREUR MÉTIER : {e}")
            except ValueError:
                print("\n❌ Erreur de saisie.")

        elif choix == "2":
            print("\n--- Historique Session ---")
            if not service.reservations:
                print("Aucune réservation effectuée.")
            for r in service.reservations:
                print("-" * 20)
                print(r)
            input("\nEntrée pour retour menu...")

        elif choix == "3":
            print("Au revoir !")
            sys.exit()

if __name__ == "__main__":
    main()