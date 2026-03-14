import json
import unicodedata
import re
from rapidfuzz import fuzz
from tqdm import tqdm

# --- 1. CONFIGURATION ---

GEO_CONFLICTS = [
    {"keywords": ['arabe', 'maghreb', 'islam', 'orient', 'afrique du nord'], "label": "ARABIC"},
    {"keywords": ['allemagne', 'germanique', 'alsace', 'allemand', 'prussien'], "label": "GERMANIC"},
    {"keywords": ['espagne', 'espagnol', 'hispano', 'castille'], "label": "HISPANIC"},
    {"keywords": ['italie', 'italien', 'lombardie', 'toscan'], "label": "ITALIAN"}
]

def normalize(text):
    if not text: return ""
    text = unicodedata.normalize('NFD', text.lower())
    return "".join([c for c in text if unicodedata.category(c) != 'Mn']).strip()

def get_semantic_tags(text):
    text = text.lower()
    tags = set()
    for conflict in GEO_CONFLICTS:
        for kw in conflict['keywords']:
            if kw in text:
                tags.add(conflict['label'])
    return tags

# --- 2. FONCTIONS DE TRAITEMENT ---

def final_expert_clustering(names_data, origins_data):
    name_to_info = {}
    print("Phase 1 : Analyse des profils...")
    for item in names_data:
        raw_name = item['name']
        norm_name = normalize(raw_name)
        text = " ".join([origins_data[oid] for oid in item.get('origins', []) if oid in origins_data])
        
        name_to_info[norm_name] = {
            "raw": raw_name,
            "tags": get_semantic_tags(text),
            "pivots": set(re.findall(r"voir\s+([a-zà-ÿ-]+)", text.lower())),
            "text": text
        }

    all_names = list(name_to_info.keys())
    all_names.sort(key=len, reverse=True) 
    
    clusters = []
    processed = set()

    print(f"Phase 2 : Clustering sécurisé (Volume: {len(all_names)} noms)...")
    pbar = tqdm(total=len(all_names))

    for name in all_names:
        if name in processed:
            pbar.update(1)
            continue
            
        current_cluster = {name}
        processed.add(name)
        info_main = name_to_info[name]
        
        if len(name) < 4:
            clusters.append(current_cluster)
            pbar.update(1)
            continue

        for other in all_names:
            if other in processed: continue
            info_oth = name_to_info[other]
            
            score = fuzz.ratio(name, other)
            is_pivot = (other in info_main['pivots']) or (name in info_oth['pivots'])
            
            has_collision = False
            if info_main['tags'] and info_oth['tags']:
                if not (info_main['tags'] & info_oth['tags']):
                    has_collision = True

            if is_pivot:
                current_cluster.add(other)
                processed.add(other)
            elif not has_collision:
                if abs(len(name) - len(other)) <= 1 and score >= 91:
                    current_cluster.add(other)
                    processed.add(other)
                elif (other in name or name in other) and min(len(name), len(other)) >= 4:
                    if abs(len(name) - len(other)) <= 4 and score >= 75:
                        current_cluster.add(other)
                        processed.add(other)

        clusters.append(current_cluster)
        pbar.update(1)

    pbar.close() # Indispensable pour fermer la barre
    return clusters, name_to_info # Indispensable pour renvoyer les données

# --- 3. FONCTIONS D'EXPORT ET DIAGNOSTIC ---

def diagnostic_clusters(clusters, name_info):
    print(f"\n{'='*40}")
    print("DIAGNOSTIC DES CLUSTERS")
    print(f"{'='*40}")
    sorted_clusters = sorted(clusters, key=len, reverse=True)
    print(f"Top 5 des plus gros regroupements :")
    for i, cluster in enumerate(sorted_clusters[:5]):
        main_name = min(list(cluster), key=len)
        raw_main = name_info[main_name]['raw'].upper()
        print(f"{i+1}. {raw_main:<15} : {len(cluster)} membres")
        members = [name_info[m]['raw'] for m in list(cluster)[:10]]
        print(f"Ex: {', '.join(members)}...")
    print(f"{'='*40}\n")

def export_to_json(clusters, name_info, output_path):
    final_output = []
    for cluster in clusters:
        if not cluster: continue
        main_name_norm = min(list(cluster), key=len)
        
        final_output.append({
            "main_name": name_info[main_name_norm]['raw'].upper(),
            "variants": [name_info[m]['raw'].upper() for m in cluster],
            "type": "names",
            "origin_raw": " ".join(list(dict.fromkeys([name_info[m]['text'] for m in cluster if name_info[m]['text']]))),
            "migration_data": {}
        })
        
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(final_output, f, indent=4, ensure_ascii=False)

# --- 4. EXECUTION ---

if __name__ == "__main__":
    PATH_NAMES = 'C:/Users/cocop/Desktop/SUP_DE_VINCI/NLP/Projet/data/names.json'
    PATH_ORIGINS = 'C:/Users/cocop/Desktop/SUP_DE_VINCI/NLP/Projet/data/origins.json'
    PATH_OUT = 'C:/Users/cocop/Desktop/SUP_DE_VINCI/NLP/Projet/data/final_names.json'

    try:
        with open(PATH_NAMES, 'r', encoding='utf-8') as f: n_raw = json.load(f)
        with open(PATH_ORIGINS, 'r', encoding='utf-8') as f: o_raw = json.load(f)

        res_clusters, res_infos = final_expert_clustering(n_raw, o_raw)
        diagnostic_clusters(res_clusters, res_infos)
        export_to_json(res_clusters, res_infos, PATH_OUT)
        print(f"Script terminé avec succès. Fichier généré : {PATH_OUT}")
        
    except Exception as e:
        print(f"Erreur lors de l'exécution : {e}")