class Film:
    def __init__(self, titre: str, duree: int, note : int, style : str):
        self.titre = titre
        self.duree = duree
        self.note = note
        self.style = style

    # Sert à bien afficher: "Inception (148 min)" 
    # Si y'a pas __str__ sa fais un truc moche : <models.film.Film object at 0x7e8d22a38f50> (y'a pas la fonction tout court)
    def __str__(self):
        return f"{self.titre} ({self.duree} min)"

    def to_dict(self):
        return {
            "titre": self.titre,
            "duree": self.duree,
            "note": self.note,
            "style": self.style,
        }
    
    @staticmethod
    def from_dict(data: dict):
        return Film(
            titre=data["titre"],
            duree=data["duree"],
            note=data["note"],
            style=data["style"],
        )