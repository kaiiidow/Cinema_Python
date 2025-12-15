class CinemaException(Exception):
    """Exception de base pour toutes les erreurs personnalisées du projet cinéma."""
    pass

class SallePleineException(CinemaException):
    """
    Levée lorsqu'une tentative de réservation est faite pour une séance
    qui n'a pas assez de places disponibles.
    """
    pass

class ConflitSeanceException(CinemaException):
    """
    Levée lors de la création d'une séance si celle-ci se chevauche
    temporellement avec une autre séance dans la même salle.
    """
    pass

class FilmIntrouvableException(CinemaException):
    """
    Levée lorsqu'une opération tente d'accéder à un film qui n'existe pas
    dans le catalogue.
    """
    pass