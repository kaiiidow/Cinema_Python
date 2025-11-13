import json
import os
from models.film import Film


# Chemin vers le projet (dossier cinéma_python)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Chemin vers data/films.json
JSON_PATH = os.path.join(BASE_DIR, "data", "films.json")

def charger_film():
    if not  os.path.exists(JSON_PATH): #si le fichier n'existe pas sa retourne une liste vide films
        return []
    # permet d'ouvrir le fichier films.json 
    with open( "data/films.json", "r", encoding="utf-8") as f: #JSON_PATH
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return []
    return [Film.from_dict(d) for d in data]

def sauvegarder_film(films):
    data = [f.to_dict() for f in films]

    with open("data/films.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def film_existe(films,film):
    for f in films:
        if f.titre == film.titre and f.duree == film.duree:
            return True 
    return False 

def ajouter_film_si_nouveau(film):
    films = charger_film()
    if film_existe(films,film):
        print("film existant")
        return False
    films.append(film)
    sauvegarder_film(films)
    print("film ajouté")
    return True

    