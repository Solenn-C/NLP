import json

filename = "data/BDD_Prenom_Final.json"

try:
    # 1. Lecture du fichier actuel
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 2. Ajout de la colonne type pour chaque entrée
    for entry in data:
        entry["type"] = "prenom"

    # 3. Écriture du nouveau fichier
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"✅ Transformation terminée ! {len(data)} entrées mises à jour avec type='prenom'.")

except Exception as e:
    print(f"❌ Erreur : {e}")