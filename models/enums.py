from enum import Enum, auto


class TypeSalle(Enum):
    CLASSIQUE = "classique"
    IMAX = "IMAX"
    DOLBY_CINEMA = "Dolby Cinema"


class StyleFilm(Enum):
    ACTION = auto()
    COMEDIE = auto()
    DRAME = auto()
    SCIENCE_FICTION = auto()
    HORREUR = auto()