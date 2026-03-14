import json

# Chemins de vos fichiers
FILE_RANG = 'data/prenoms_rang_mondial.json'
FILE_ORIGINE = 'data/BDD_Prenom_Final.json'
FILE_OUTPUT = 'data/BDD_Fusionnée_Final_Prénom.json'

def fusionner_bases():
    # 1. Chargement des données
    try:
        with open(FILE_RANG, 'r', encoding='utf-8') as f:
            data_rang = json.load(f)
            
        with open(FILE_ORIGINE, 'r', encoding='utf-8') as f:
            data_origine = json.load(f)
    except Exception as e:
        print(f"Erreur lors du chargement : {e}")
        return

    # 2. Indexation du fichier de RANG
    # On normalise les clés (minuscules et sans espaces)
    rang_index = {
        str(item.get('prenom')).strip().lower(): item 
        for item in data_rang 
        if item.get('prenom')
    }

    # 3. Fusion en partant de la base d'origine
    resultat_final = []
    count_enriched = 0
    
    for item in data_origine:
        name_original = item.get('name')
        if not name_original:
            continue
            
        # On fait le lien entre 'name' (origine) et 'prenom' (index rang)
        name_key = str(name_original).strip().lower()
        info_rang = rang_index.get(name_key, {})
        
        if info_rang:
            count_enriched += 1
        
        # Construction de l'entrée fusionnée
        fusion = {
            "prenom": name_original,
            "gender": item.get("gender", "N/A"),
            "origin_cleaned": item.get("origins_clean", "N/A"),
            "variants": item.get("variants", []),
            "type": item.get("type", "N/A"),
            "rang_mondial": info_rang.get("rang", "N/A"),
            "incidence_mondiale": info_rang.get("incidence", "N/A"),
            "frequence_mondiale": info_rang.get("frequence", "N/A")
        }
        resultat_final.append(fusion)

    # 4. Exportation
    with open(FILE_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(resultat_final, f, indent=4, ensure_ascii=False)
    
    # 5. Affichage des 10 premiers pour vérification
    print(f"\n--- Aperçu des 10 premiers résultats ---")
    for i, entree in enumerate(resultat_final[:10]):
        print(f"\n[{i+1}] {entree['prenom']} :")
        print(json.dumps(entree, indent=4, ensure_ascii=False))

    print(f"\n--- Rapport de fusion ---")
    print(f"Total prénoms traités : {len(resultat_final)}")
    print(f"Prénoms enrichis (lien réussi) : {count_enriched}")
    print(f"Fichier exporté : {FILE_OUTPUT}")

if __name__ == "__main__":
    fusionner_bases()
