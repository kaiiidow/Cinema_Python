from exceptions.salle_pleine import SallePleineException

class Salle:
    def __init__(self, numero: int, rangees : int, siege : int, type : str):
        self.numero = numero
        self.nb_rangees = rangees
        self.nb_siege = siege
        self.capacite = self.nb_rangees * self.nb_siege
        self.places_reservees = 0

    def reserver(self, nb_places: int):
        if self.places_reservees + nb_places > self.capacite:
            raise SallePleineException(f"Salle {self.numero} pleine !")
        self.places_reservees += nb_places

    def __str__(self):
        return f"Salle {self.numero} ({self.places_reservees}/{self.capacite} places réservées)"
    
    def creer_salle(self):
        pass
