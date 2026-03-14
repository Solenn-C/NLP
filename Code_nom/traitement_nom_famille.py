import json
import pandas as pd
from collections import defaultdict

def identifier_et_regrouper(names_path, origins_path):
    print("📦 Analyse des fichiers JSON...")
    with open(names_path, 'r', encoding='utf-8') as f:
        names_data = json.load(f)
    with open(origins_path, 'r', encoding='utf-8') as f:
        origins_dict = json.load(f)

    # Étape 1 : Regroupement par ID d'origine
    mapping = defaultdict(set)
    for item in names_data:
        for o_id in item['origins']:
            mapping[o_id].add(item['name'].capitalize())

    # Étape 2 : Résumé et reformulation (Nettoyage des textes)
    final_data = []
    for o_id, names in mapping.items():
        text = origins_dict.get(o_id, "")
        # On simplifie les espaces et la ponctuation pour le "résumé"
        summary = " ".join(text.split()) 
        
        final_data.append({
            "Groupe": ", ".join(sorted(list(names))),
            "Nombre": len(names),
            "Explication Reformulée": summary
        })
    
    return pd.DataFrame(final_data)

if __name__ == "__main__":
    df = identifier_et_regrouper('names.json', 'origins.json')
    df.to_excel("Analyse_Noms_Famille.xlsx", index=False)
    print("✅ Fichier 'Analyse_Noms_Famille.xlsx' généré.")