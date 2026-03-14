import pandas as pd
import unicodedata
import re
from rapidfuzz import fuzz
import json
from tqdm import tqdm
from sklearn.metrics import f1_score, precision_score, recall_score

def strict_normalize(text):
    if not isinstance(text, str): return ""
    text = re.sub(r'\d+', '', text)
    nfkd_form = unicodedata.normalize('NFKD', text)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)]).lower().strip()

def get_skeleton(text):
    name = strict_normalize(text)
    if len(name) < 1: return ""
    skeleton = name[0] + "".join([c for c in name[1:] if c not in 'aeiouy'])
    return skeleton

def process_data(path_csv):
    df = pd.read_csv(path_csv, encoding='utf-8-sig')
    
    df['name_clean'] = df['name'].apply(strict_normalize)
    # On simplifie le skeleton pour être moins restrictif (juste la première lettre)
    # Cela permet à Mary (mry) et Marie (mr) de se rencontrer dans le groupe 'm'
    df['skeleton'] = df['name_clean'].apply(lambda x: x[0] if len(x) > 0 else "")
    
    final_data = []
    groups = df.groupby('skeleton')
    
    for _, group in tqdm(groups, desc="🛡️ Recherche des variantes"):
        names_in_group = group.to_dict('records')
        
        for item in names_in_group:
            current_name_clean = item['name_clean']
            
            # Utilisation de WRATIO : plus intelligent pour les terminaisons (Martine/Martina)
            # Et seuil abaissé à 85 pour capter les différences de genre
            variants_mask = group['name_clean'].apply(lambda x: fuzz.WRatio(current_name_clean, x) >= 91)
            similar_names_df = group[variants_mask]
            
            raw_variants = sorted(list(set(re.sub(r'\d+', '', n).strip() for n in similar_names_df['name'])))
            
            current_origins = item.get('origins', 'Inconnue')
            if pd.isna(current_origins) or str(current_origins).strip() == "":
                current_origins = "Inconnue"

            final_data.append({
                "name": re.sub(r'\d+', '', item['name']).strip(),
                "gender": item.get('gender', 'unknown'),
                "origins": current_origins,
                "variants": ", ".join(raw_variants)
            })

    return final_data

def run_full_evaluation(results):
    # Dictionnaire de test (Vérité Terrain)
    # À adapter selon tes prénoms réels pour un score précis
    ground_truth = {
        "Aline": ["Aline", "Alyne", "Eline"],
        "Nicolas": ["Nicolas", "Nikolas"],
        "Jean": ["Jean"]
    }
    
    y_true, y_pred = [], []
    
    for item in results:
        name = item['name']
        if name in ground_truth:
            actual = set(ground_truth[name])
            predicted = set(v.strip() for v in item['variants'].split(','))
            
            all_names = actual.union(predicted)
            for n in all_names:
                y_true.append(1 if n in actual else 0)
                y_pred.append(1 if n in predicted else 0)
    
    if not y_true: return 0, 0, 0
    
    return (f1_score(y_true, y_pred), 
            precision_score(y_true, y_pred), 
            recall_score(y_true, y_pred))

if __name__ == "__main__":
    PATH_INPUT = 'data/dataset_prenoms_BT_complet.csv'
    
    try:
        # On garde ton seuil de 90 qui semble être le meilleur compromis
        results = process_data(PATH_INPUT)
        
        f1, prec, rec = run_full_evaluation(results)
        
        print(f"\n--- RAPPORT D'EXPERTISE ---")
        print(f"✅ F1-Score  : {f1:.4f}")
        print(f"🎯 Précision : {prec:.4f} (Qualité des variants)")
        print(f"🔎 Rappel    : {rec:.4f} (Quantité trouvée)")
        
        with open('data/dataset_prenoms_NLP_final_V2.json', "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)

    except FileNotFoundError:
        print(f"❌ Fichier {PATH_INPUT} introuvable.")