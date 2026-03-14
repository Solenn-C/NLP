import json
import re
from tqdm import tqdm
from collections import defaultdict

def semantic_pattern_refine_v4(input_path, output_path):
    print(f"Lecture : {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        clusters = json.load(f)

    name_to_idx = {c['main_name'].upper(): i for i, c in enumerate(clusters)}
    to_merge = defaultdict(set)

    print("Analyse : Patterns sémantiques + Identité d'entête...")
    for i, c in enumerate(tqdm(clusters)):
        txt = c.get('origin_raw', '').strip()
        if not txt: continue
        
        # --- RÈGLE 1 : PATTERNS (Voir Durand, etc.) ---
        patterns = [r"(?:voir|variante[s]? de|diminutif de|racine de|forme de)\s+([A-ZÀ-ÿa-z-]+)"]
        for pattern in patterns:
            matches = re.findall(pattern, txt, re.IGNORECASE)
            for match in matches:
                target_name = match.upper()
                if target_name in name_to_idx:
                    t_idx = name_to_idx[target_name]
                    if i != t_idx:
                        to_merge[i].add(t_idx)
                        to_merge[t_idx].add(i)

        # --- RÈGLE 2 : IDENTITÉ D'ENTÊTE ---
        # Si deux clusters commencent par les mêmes 300 caractères, c'est la même notice
        prefix = txt[:300].lower()
        if len(prefix) >= 80:
            for j in range(i + 1, len(clusters)):
                txt_other = clusters[j].get('origin_raw', '').strip()
                if txt_other.lower().startswith(prefix):
                    to_merge[i].add(j)
                    to_merge[j].add(i)

    # 3. Reconstruction par Union-Find
    processed = set()
    final_clusters = []
    
    for i in range(len(clusters)):
        if i in processed: continue
        stack = [i]
        component = set()
        while stack:
            curr = stack.pop()
            if curr not in component:
                component.add(curr)
                processed.add(curr)
                stack.extend(to_merge[curr] - component)
        
        all_variants = set()
        all_texts = []
        best_main = None
        
        for idx in component:
            cl = clusters[idx]
            all_variants.update(cl['variants'])
            all_texts.append(cl['origin_raw'])
            # On cherche le nom le plus court MAIS on évite les noms de 3 lettres 
            # comme "MAH" ou "ROC" si un nom plus long existe (plus parlant)
            curr_name = cl['main_name'].upper()
            if best_main is None:
                best_main = curr_name
            else:
                if len(curr_name) < len(best_main) and len(curr_name) >= 4:
                    best_main = curr_name
                elif len(best_main) < 4 and len(curr_name) >= 4:
                    best_main = curr_name

        # Sécurité anti gros cluster (sauf Durand)
        if len(all_variants) > 50 and "DURAN" not in best_main:
             for idx in component:
                 final_clusters.append(clusters[idx])
        else:
            final_clusters.append({
                "main_name": best_main,
                "variants": sorted(list(all_variants)),
                "type": "names",
                "origin_raw": ". ".join(list(dict.fromkeys(all_texts))),
                "migration_data": {}
            })

    print(f"Terminé ! {len(clusters)} -> {len(final_clusters)} clusters.")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(final_clusters, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    INPUT = 'C:/Users/cocop/Desktop/SUP_DE_VINCI/NLP/Projet/data/final_names.json'
    OUTPUT = 'C:/Users/cocop/Desktop/SUP_DE_VINCI/NLP/Projet/data/final_names_COMPLETE.json'
    semantic_pattern_refine_v4(INPUT, OUTPUT)