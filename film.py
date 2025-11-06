class Film:
    def __init__(self, titre: str, duree: int, note : int, style : str):
        self.titre = titre
        self.duree = duree

    def __str__(self):
        return f"{self.titre} ({self.duree} min)"
