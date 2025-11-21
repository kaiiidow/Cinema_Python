from enum import Enum, auto

class TypeSalle(Enum):
    CLASSIQUE = "Classique"
    IMAX = "IMAX"          
    DOLBY = "Dolby Cinema" 
    TROIS_D = "3D"         

class StyleFilm(Enum):
    ACTION = auto()
    COMEDIE = auto()
    DRAME = auto()
    SF = auto()
    HORREUR = auto()
    ANIMATION = auto()

class Tarif(Enum):
    PLEIN = ("Plein tarif", 1.0)
    ETUDIANT = ("Etudiant", 0.8)       # -20%
    SENIOR = ("Senior", 0.9)           # -10%
    ENFANT = ("Enfant (-14 ans)", 0.6) # -40%

    def __init__(self, label, coeff):
        self.label = label
        self.coeff = coeff