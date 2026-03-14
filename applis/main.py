from fastapi import FastAPI, HTTPException
import json
import pandas as pd

app = FastAPI()

# Chargement des données
try:
    with open("BDD_Fusionnée_Final_Prénom.json", "r", encoding="utf-8") as f:
        prenoms_data = json.load(f)
    with open("BDD_Nom_famille_Final.json", "r", encoding="utf-8") as f:
        noms_data = json.load(f)
    
    # Marquage du type
    for p in prenoms_data: 
        p['_type'] = 'prenom'
        
    for n in noms_data: 
        n['_type'] = 'names' # Type interne
        if 'main_name' in n:
            n['nom_famille'] = n['main_name']
        if 'migration_data' in n and isinstance(n['migration_data'], dict):
            n['origin_country'] = n['migration_data'].get('origin_country')
    
    all_data = prenoms_data + noms_data
    
    country_df = pd.read_csv("countries_fr.csv")
    name_to_iso = dict(zip(country_df['origin_fr'], country_df['iso_alpha']))
    
    print(f"✅ Chargement terminé : {len(all_data)} entrées.")
except Exception as e:
    print(f"❌ Erreur : {e}")
    all_data = []
    name_to_iso = {}

@app.get("/api/search/{search_type}/{query}")
async def get_name(search_type: str, query: str):
    query_clean = query.strip().lower()
    st = search_type.lower()
    
    # --- FLEXIBILITÉ DU TYPE ---
    # Si le front envoie "nom", on cherche dans "names"
    target_type = 'names' if st in ['nom', 'names', 'nom_famille'] else 'prenom'
    
    # Filtrage
    filtered = [n for n in all_data if n.get('_type') == target_type]

    # Recherche
    result = next((n for n in filtered if (str(n.get('prenom', '')) or str(n.get('nom_famille', ''))).lower() == query_clean), None)
    
    if not result:
        result = next((n for n in filtered if query_clean in (str(n.get('prenom', '')) or str(n.get('nom_famille', ''))).lower()), None)

    if result:
        name_display = result.get('prenom') or result.get('nom_famille')
        origins_str = result.get('origin_cleaned') or result.get('origin_country') or "Inconnue"
        
        # Extraction ISO
        parts = [p.strip() for p in str(origins_str).split(',')]
        iso_codes = [name_to_iso.get(p) for p in parts if p in name_to_iso]

        # Variants
        raw_v = result.get('variants', [])
        if isinstance(raw_v, str):
            v_list = [v.strip() for v in raw_v.split(',') if v.strip().lower() != name_display.lower()]
        else:
            v_list = [v for v in raw_v if str(v).lower() != name_display.lower()]

        # Rang
        rank_raw = result.get('rang_mondial', 'N/A')
        clean_rank = str(rank_raw).replace('#', '').strip()
        rank_display = f"{clean_rank}{'er' if clean_rank == '1' else 'e'}" if clean_rank.isdigit() else "N/A"

        # Fréquence
        freq_raw = result.get('frequence_mondiale', 'N/A')
        freq_display = f"1/ {str(freq_raw).split(':')[-1].strip()} personnes" if ":" in str(freq_raw) else freq_raw

        return {
            "name": name_display,
            "gender": result.get('gender', 'u'),
            "origins": origins_str,
            "iso_codes": list(set(filter(None, iso_codes))),
            "variants_list": v_list,
            "rank": rank_display,
            "incidence": result.get('incidence_mondiale', 'N/A'),
            "frequency": freq_display
        }
    
    raise HTTPException(status_code=404, detail="Entrée introuvable")