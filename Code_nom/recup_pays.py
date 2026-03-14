import json
import re
import csv
from tqdm import tqdm

# --- 1. CHARGEMENT DU RÉFÉRENTIEL CSV ---
def load_country_ref(csv_path):
    country_map = {} 
    iso_map = {}     
    
    with open(csv_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row['origin_fr'].strip()
            iso = row['iso_alpha'].strip()
            iso_map[name] = iso
            country_map[name.lower()] = name
            
    return country_map, iso_map

# --- 2. LOGIQUE D'EXTRACTION ---

def find_standard_geo(text, country_map, iso_map):
    if not text: 
        return "Inconnu", "N/A"
    
    text_lower = text.lower()
    
    # --- A. PRIORITÉ 1 : Détection directe des Pays du CSV ---
    for pattern, official_name in country_map.items():
        if re.search(rf"\b{pattern}\b", text_lower):
            return official_name, iso_map[official_name]

    # --- B. PRIORITÉ 2 : Adjectifs de nationalité et extensions ---
    nationalities = {
        "catalan": "Espagne", "catalogne": "Espagne", "castille": "Espagne", 
        "espagnol": "Espagne", "hispano": "Espagne", "basque": "Espagne",
        "castillan": "Espagne", "aragon": "Espagne",
        "italien": "Italie", "toscane": "Italie", "lombardie": "Italie",
        "allemand": "Allemagne", "germanique": "Allemagne", "prusse": "Allemagne", "rhénanie": "Allemagne",
        "belge": "Belgique", "flamand": "Belgique", "wallon": "Belgique", "vander": "Belgique", "steen": "Belgique",
        "portugais": "Portugal", "polonais": "Pologne",
        "hollandais": "Pays-Bas", "néerlandais": "Pays-Bas", "zélande": "Pays-Bas",
        "anglais": "Angleterre", "britannique": "Angleterre", "écossais": "Angleterre",
        "chypre": "Grèce", "grec": "Grèce", "arménien": "Arménie", "-djian": "Arménie", "-ian": "Arménie",
        "turc": "Turquie", "turco": "Turquie", "luxembourg": "Luxembourg",
        "arabe": "Algérie", "maghreb": "Algérie", "islam": "Algérie", "algérienne : Algérie" "musulman": "Algérie",
        "marocain": "Maroc", "tunisien": "Tunisie", "abdel": "Algérie", "abder": "Algérie",
        "juif": "Israël (Biblique)", "hébreu": "Israël (Biblique)",
        "breton": "France", "normand": "France", "alsacien": "France", 
        "provençal": "France", "gascon": "France", "auvergnat": "France",
        "picard": "France", "savoyard": "France", "boulonnais": "France", "lyonnais": "France"
    }
    
    # On force la vérification de Chypre spécifiquement si présent dans ton CSV
    if "chypre" in text_lower:
        if "Chypre" in iso_map: return "Chypre", iso_map["Chypre"]
        else: return "Grèce", "GRC"

    for adj, official_name in nationalities.items():
        if adj in text_lower:
            return official_name, iso_map.get(official_name, "FRA")

    # --- C. PRIORITÉ 3 : Régions, Départements et Chiffres Français ---
    regions_fr = [
        "bretagne", "normandie", "alsace", "lorraine", "provence", "savoie", "auvergne", 
        "limousin", "berry", "poitou", "picardie", "flandre", "corse", "languedoc", 
        "guyenne", "gascogne", "béarn", "dauphiné", "franche-comté", "anjou", "touraine",
        "périgord", "roussillon", "cevennes", "vendée", "limagne", "brie", "beauce",
        "boulonnais", "carcassonne", "limousin", "angoumois", "saintonge", "rennes"
    ]

    departements_fr = [
        "ain", "aisne", "allier", "alpes", "ardèche", "ardennes", "ariège", "aube", "aude",
        "aveyron", "bouches-du-rhône", "calvados", "cantal", "charente", "cher", "corrèze",
        "côte-d'or", "côte d'or", "côte d’or", "côtes-d'armor", "creuse", "dordogne", "doubs", 
        "drôme", "eure", "finistère", "gard", "garonne", "gers", "gironde", "hérault", 
        "ille-et-vilaine", "indre", "isère", "jura", "landes", "loire", "lot", "lozère", 
        "manche", "marne", "mayenne", "moselle", "nièvre", "nord", "oise", "orne", 
        "pas-de-calais", "puy-de-dôme", "pyrénées", "rhône", "saône", "sarthe", "seine", 
        "somme", "tarn", "var", "vaucluse", "vosges", "yonne", "deux-sèvres", "morbihan"
    ]

    departements_nums = [
        "01", "02", "03", "04", "05", "06", "07", "08", "09", "10",
        "11", "12", "13", "14", "15", "16", "17", "18", "19", "20",
        "21", "22", "23", "24", "25", "26", "27", "28", "29", "30",
        "31", "32", "33", "34", "35", "36", "37", "38", "39", "40",
        "41", "42", "43", "44", "45", "46", "47", "48", "49", "50",
        "51", "52", "53", "54", "55", "56", "57", "58", "59", "60",
        "61", "62", "63", "64", "65", "66", "67", "68", "69", "70",
        "71", "72", "73", "74", "75", "76", "77", "78", "79", "80",
        "81", "82", "83", "84", "85", "86", "87", "88", "89", "90",
        "91", "92", "93", "94", "95", "2A", "2B", "971", "972", "973", "974", "976"
    ]

    # Vérification textuelle
    if any(rf in text_lower for rf in regions_fr) or any(df in text_lower for df in departements_fr):
        return "France", "FRA"

    # Vérification numérique (ex: "dans le 29")
    if any(re.search(rf"\b{num}\b", text_lower) for num in departements_nums):
        return "France", "FRA"

    # --- D. PRIORITÉ 4 : Indices génériques ---
    if any(clue in text_lower for clue in ["porté dans", "département", "nom de famille", "commune de"]):
        return "France", "FRA"

    return "Inconnu", "N/A"

# --- 3. TRAITEMENT ---

def process_with_csv_standard(json_in, csv_path, json_out):
    country_map, iso_map = load_country_ref(csv_path)
    
    with open(json_in, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Extraction et Standardisation...")
    
    for cluster in tqdm(data):
        description = cluster.get("origin_raw", "")
        country_name, iso_code = find_standard_geo(description, country_map, iso_map)
        
        cluster["migration_data"] = {
            "origin_country": country_name,
            "iso_alpha": iso_code,
            "has_clue": True if country_name != "Inconnu" else False
        }

    with open(json_out, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print(f"Fichier généré avec succès : {json_out}")

if __name__ == "__main__":
    PATH_CSV = 'C:/Users/cocop/Desktop/SUP_DE_VINCI/NLP/Projet/data/countries_fr.csv'
    PATH_JSON_IN = 'C:/Users/cocop/Desktop/SUP_DE_VINCI/NLP/Projet/data/final_names_COMPLETE.json'
    PATH_JSON_OUT = 'C:/Users/cocop/Desktop/SUP_DE_VINCI/NLP/Projet/data/final_names_GEOLOC.json'
    
    process_with_csv_standard(PATH_JSON_IN, PATH_CSV, PATH_JSON_OUT)