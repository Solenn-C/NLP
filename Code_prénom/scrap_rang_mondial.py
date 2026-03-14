import requests
from bs4 import BeautifulSoup
import json

def scrape_rang_complet_prenoms():
    base_url = "https://forebears.io/earth/forenames"
    file_name = "data/prenoms_rang_mondial.json"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
        "Accept-Language": "fr,fr-FR;q=0.9,en;q=0.8"
    }

    print(f"Chargement de la liste mondiale des prénoms...")
    try:
        response = requests.get(base_url, headers=headers, timeout=30)
        if response.status_code != 200:
            print(f"Erreur HTTP {response.status_code}")
            return

        soup = BeautifulSoup(response.content, 'html.parser')
        # On cible le corps du tableau identifié dans vos captures
        lignes = soup.select("table.forename-table tbody tr")
        
        resultats = []

        for index, ligne in enumerate(lignes):
            colonnes = ligne.find_all("td")
            
            # Vérification qu'on a bien assez de colonnes (Rang, Nom, Incidence, Fréquence)
            if len(colonnes) >= 4:
                resultats.append({
                    "rang": index + 1,
                    "prenom": colonnes[1].get_text(strip=True),     # Colonne avec le lien
                    "incidence": colonnes[2].get_text(strip=True),  # Nombre total
                    "frequence": colonnes[3].get_text(strip=True)   # Ex: 1 sur 78
                })

        # Sauvegarde au format JSON
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(resultats, f, ensure_ascii=False, indent=4)

        print(f"Succès ! {len(resultats)} prénoms extraits avec fréquences dans '{file_name}'.")

    except Exception as e:
        print(f"Erreur : {e}")

if __name__ == "__main__":
    scrape_rang_complet_prenoms()