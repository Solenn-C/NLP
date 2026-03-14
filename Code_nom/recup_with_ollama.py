import json
import requests
from tqdm import tqdm

def call_ollama_tiny(prompt):
    url = "http://localhost:11434/api/generate"
    data = {
        "model": "tinyllama",
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }
    try:
        # Timeout court : si TinyLlama ne répond pas en 5s, c'est qu'il y a un souci système
        response = requests.post(url, json=data, timeout=5)
        if response.status_code == 200:
            return json.loads(response.text)['response']
    except:
        return None

def process_inconnus_tiny(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    inconnus = [c for c in data if c['migration_data'].get('origin_country') == "Inconnu"]
    print(f"Analyse de {len(inconnus)} noms avec TinyLlama...")

    for cluster in tqdm(inconnus):
        name = cluster['main_name']
        # On ne prend que le strict nécessaire de la description
        desc = cluster.get('origin_raw', '')[:100]
        
        # Prompt ultra-minimaliste pour gagner en rapidité
        prompt = f"Identify country for {name} from text: {desc}. Return JSON: {{\"country\": \"...\"}}"
        
        res_raw = call_ollama_tiny(prompt)
        if res_raw:
            try:
                res_json = json.loads(res_raw)
                country = res_json.get('country')
                if country and country != "Inconnu":
                    cluster['migration_data']['origin_country'] = country
                    cluster['migration_data']['has_clue'] = True
            except:
                continue

    # Sauvegarde du fichier mis à jour
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Terminé ! Fichier prêt pour conversion binôme : {output_path}")

if __name__ == "__main__":
    PATH_IN = 'C:/Users/cocop/Desktop/SUP_DE_VINCI/NLP/Projet/data/final_names_GEOLOC.json'
    PATH_OUT = 'C:/Users/cocop/Desktop/SUP_DE_VINCI/NLP/Projet/data/final_names_GEOLOC_OLLAMA.json'
    process_inconnus_tiny(PATH_IN, PATH_OUT)