import json
import re

def generer_json_unifie(input_file, output_file):
    # 1. Chargement des données
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 2. Mapping de normalisation (à compléter selon vos besoins spécifiques)
    mapping_fr = {
        "Arabic": "Arabie",
        "Persian": "Iran",
        "Spanish": "Espagne",
        "French": "France",
        "German": "Allemagne",
        "Italian": "Italie",
        "English": "Angleterre",
        "Japanese": "Japon",
        "Chinese": "Chine",
        "Russian": "Russie",
        "Biblical Hebrew": "Israël (Biblique)",
        "Greek": "Grèce",
        "Ancient Greek": "Grèce Antique",
        "Azerbaijani": "Azerbaïdjan",
        "Kurdish": "Kurdistan",
        "Portuguese": "Portugal",
        "Turkish": "Turquie",
        "Dutch": "Pays-Bas",
        "Western African": "Afrique de l'Ouest",
        "Central African": "Afrique Centrale",
        "Latin American": "Amérique Latine",
        "Romanian": "Roumanie",
        "Hungarian": "Hongrie",
        "Finnish": "Finlande",
        "Swedish": "Suède",
        "Norwegian": "Norvège",
        "Danish": "Danemark",
        "Scottish": "Écosse",
        "Irish": "Irlande",
        "Welsh": "Pays de Galles",
        "Catalan": "Catalogne",
        "Basque": "Pays Basque",
        "Polish": "Pologne",
        "Czech": "Tchéquie",
        "Slovak": "Slovaquie",
        "Indonesian": "Indonésie",
        "Malay": "Malaisie",
        "Vietnamese": "Vietnam",
        "Thai": "Thaïlande"
    }

    # Liste des termes à supprimer (variations inutiles)
    terms_to_remove = [
        r'History', r'Mythology', r'Literature', 
        r'\(Modern\)', r'\(Rare\)', r'\(Ancient\)', r'\(Latinized\)'
    ]

    new_data = []

    for entry in data:
        raw_origins = entry.get('origins', '')
        
        # Nettoyage et unification
        parts = [p.strip() for p in raw_origins.split(',')]
        unified_origins = []
        
        for part in parts:
            clean_part = part
            # Suppression des mots comme "History"
            for term in terms_to_remove:
                clean_part = re.sub(term, '', clean_part, flags=re.IGNORECASE).strip()
            
            # Nettoyage final des virgules ou parenthèses traînantes
            clean_part = clean_part.strip(' ,()')
            
            if clean_part:
                # Traduction via le mapping, sinon formatage par défaut
                final_origin = mapping_fr.get(clean_part, clean_part)
                if final_origin not in unified_origins:
                    unified_origins.append(final_origin)

        # Création du nouvel objet
        new_entry = {
            "name": entry.get('name'),
            "gender": entry.get('gender'),
            "origins_clean": ", ".join(unified_origins),
            "variants": entry.get('variants')
        }
        new_data.append(new_entry)

    # 3. Export en format JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, ensure_ascii=False, indent=4)
    
    print(f"Fichier unifié généré : {output_file}")

# Exécution du script
generer_json_unifie('data/dataset_prenoms_NLP_final.json', 'data/dataset_unifie.json')