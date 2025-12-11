class CinemaException(Exception):
    """Exception de base du projet cinéma."""
    pass

class SallePleineException(CinemaException):
    """Levée quand une séance est complète."""
    pass

class FilmIntrouvableException(CinemaException):
    pass