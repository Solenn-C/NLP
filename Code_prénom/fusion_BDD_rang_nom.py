import json
import unicodedata
import re

FILE_RANG = 'data/noms_famille_rang_mondial.json'
FILE_BDD = 'data/BDD_Nom_Final.json'
FILE_OUTPUT = 'data/fusion_noms_famille.json'

def normaliser_nom(text):
    """Supprime les accents, les espaces, les tirets et met en majuscules."""
    if not text:
        return ""
    text = str(text)
    text = "".join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    text = text.upper()
    return re.sub(r'[^A-Z]', '', text)

def fusion_enrichissement_bdd():
    try:
        with open(FILE_RANG, 'r', encoding='utf-8') as f:
            data_rang = json.load(f)
        with open(FILE_BDD, 'r', encoding='utf-8') as f:
            data_bdd = json.load(f)
    except Exception as e:
        print(f"Erreur lors de la lecture : {e}")
        return

    # 1. On indexe le FICHIER DE RANG (clé normalisée)
    # On crée un dictionnaire : {'MARTINEZ': {'rang': 1, ...}, 'SMITH': {...}}
    index_rang = {}
    for entry in data_rang:
        nom_mondial = entry.get('nom_famille', "")
        cle = normaliser_nom(nom_mondial)
        if cle:
            index_rang[cle] = entry

    base_enrichie = []
    count_matched = 0

    # 2. On itère sur la BDD de base pour ne rien perdre
    for item in data_bdd:
        # On crée une COPIE pour ne pas modifier l'objet original par référence
        nouvelle_entree = item.copy()
        
        nom_bdd = item.get('main_name', "")
        cle_recherche = normaliser_nom(nom_bdd)
        
        # On cherche la correspondance dans les données de rang
        info_rang = index_rang.get(cle_recherche, {})
        
        if info_rang:
            count_matched += 1
        
        # 3. Ajout des variables de rang sans modifier le reste
        # On utilise .get(..., "N/A") pour remplir si absent
        nouvelle_entree["rang_mondial"] = info_rang.get("rang", "N/A")
        nouvelle_entree["incidence_mondiale"] = info_rang.get("nombre_personnes", "N/A")
        nouvelle_entree["frequence_mondiale"] = info_rang.get("frequence", "N/A")
        
        base_enrichie.append(nouvelle_entree)

    # Sauvegarde
    with open(FILE_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(base_enrichie, f, indent=4, ensure_ascii=False)
    
    print(f"--- Rapport d'enrichissement ---")
    print(f"Total noms conservés (BDD Initiale) : {len(base_enrichie)}")
    print(f"Noms enrichis avec des stats mondiales : {count_matched}")
    print(f"Fichier exporté : {FILE_OUTPUT}")

if __name__ == "__main__":
    fusion_enrichissement_bdd()