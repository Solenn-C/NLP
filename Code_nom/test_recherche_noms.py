import json

def search_name_in_clusters(json_path, search_query):
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        search_query = search_query.upper()
        found = False
        
        print(f"\n Recherche de '{search_query}' dans {json_path}...")
        print("-" * 50)
        
        for entry in data:
            # On cherche dans le nom principal ET dans les variantes
            if search_query == entry['main_name'] or search_query in entry['variants']:
                found = True
                print(f" NOM PRINCIPAL : {entry['main_name']}")
                print(f" VARIANTES     : {', '.join(entry['variants'])}")
                print(f" TEXTE REGROUPÉ: {entry['origin_raw'][:200]}...") # On coupe pour la lisibilité
                print("-" * 50)
        
        if not found:
            print(f" Aucun cluster trouvé pour le nom '{search_query}'.")
            
    except FileNotFoundError:
        print(" Fichier non trouvé. Vérifie le chemin de ton JSON.")
    except Exception as e:
        print(f" Erreur : {e}")

if __name__ == "__main__":
    FILE = 'C:/Users/cocop/Desktop/SUP_DE_VINCI/NLP/Projet/data/final_names_COMPLETE.json'
    
    while True:
        nom = input("\nEntrez un nom à chercher (ou 'q' pour quitter) : ")
        if nom.lower() == 'q':
            break
        search_name_in_clusters(FILE, nom)