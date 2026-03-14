import json

def convert_to_binome_format(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    new_data = []

    for cluster in data:
        # Extraction de l'origine
        origin = cluster.get('migration_data', {}).get('origin_country', 'Inconnu')
        
        # Transformation de la liste de variants en string "Var1, Var2"
        variants_list = cluster.get('variants', [])
        variants_str = ", ".join(variants_list)

        # Création du nouvel objet selon le format de la binôme
        new_entry = {
            "nom": cluster.get('main_name'),
            "gender": "n/a", # Les noms n'ont pas de genre
            "origin_cleaned": origin,
            "variants": variants_str,
            "type": "nom",
            "rang": cluster.get('rang', 0), # Valeur par défaut
            "incidence": cluster.get('incidence', "unknown"),
            "frequence": cluster.get('frequence', "unknown")
        }
        new_data.append(new_entry)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, indent=4, ensure_ascii=False)

    print(f"Conversion terminée ! {len(new_data)} noms formatés.")

if __name__ == "__main__":
    PATH_IN = 'C:/Users/cocop/Desktop/SUP_DE_VINCI/NLP/Projet/data/final_names_GEOLOC_OLLAMA.json'
    PATH_OUT = 'C:/Users/cocop/Desktop/SUP_DE_VINCI/NLP/Projet/data/final_names_FORMAT_BINOME.json'
    convert_to_binome_format(PATH_IN, PATH_OUT)