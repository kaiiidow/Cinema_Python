from enum import Enum, auto

class TypeSalle(Enum):
    CLASSIQUE = "Classique"
    IMAX = "IMAX"          
    DOLBY = "Dolby Cinema" 
    TROIS_D = "3D"         

class StyleFilm(Enum):
    ACTION = "Action"
    COMEDIE = "Comédie"
    DRAME = "Drame"
    SF = "Science-fiction"
    HORREUR = "Horreur"
    ANIMATION = "Animation"