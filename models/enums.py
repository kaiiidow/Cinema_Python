from enum import Enum, auto

class TypeSalle(Enum):
    """Énumération des différents types de technologies de salle."""
    CLASSIQUE = "Classique"
    IMAX = "IMAX"          
    DOLBY = "Dolby Cinema" 
    TROIS_D = "3D"         

class StyleFilm(Enum):
    """Énumération des différents genres de films."""
    ACTION = "Action"
    COMEDIE = "Comédie"
    DRAME = "Drame"
    SF = "Science-fiction"
    HORREUR = "Horreur"
    ANIMATION = "Animation"