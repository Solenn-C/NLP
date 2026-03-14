import json

def check_unknown_origins(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Filtrer les clusters où l'origine est inconnue
        unknowns = [c for c in data if c.get('migration_data', {}).get('origin_country') == "Inconnu"]
        
        print(f"\n{'='*60}")
        print(f"  RAPPORT DES ORIGINES INCONNUES")
        print(f"{'='*60}")
        print(f"Total de clusters : {len(data)}")
        print(f"Total Inconnus    : {len(unknowns)} ({(len(unknowns)/len(data)*100):.1f}%)")
        print(f"{'-'*60}")
        print("Top 20 des noms à corriger (et leur description) :")
        
        for i, c in enumerate(unknowns[:20]):
            name = c.get('main_name', 'SANS NOM')
            # On affiche les 100 premiers caractères de la description pour comprendre pourquoi ça rate
            desc = (c.get('origin_raw', '')[:100] + '...') if c.get('origin_raw') else "Pas de description"
            print(f"{i+1:2}. [{name}] -> {desc}")
            
        print(f"{'='*60}\n")

    except FileNotFoundError:
        print(" Fichier introuvable. Vérifie le chemin.")

if __name__ == "__main__":
    PATH = 'C:/Users/cocop/Desktop/SUP_DE_VINCI/NLP/Projet/data/final_names_FORMAT_BINOME.json'
    check_unknown_origins(PATH)