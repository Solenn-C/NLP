import requests
from bs4 import BeautifulSoup
import json

def scrape_noms_famille_mondial():
    # URL spécifique pour les noms de famille (surnames)
    url_cible = "https://forebears.io/earth/surnames"
    file_name = "noms_famille_rang_mondial.json"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
        "Accept-Language": "fr,fr-FR;q=0.9,en;q=0.8"
    }

    print(f"Chargement de la liste mondiale des noms de famille...")
    try:
        response = requests.get(url_cible, headers=headers, timeout=30)
        if response.status_code != 200:
            print(f"Erreur HTTP {response.status_code}")
            return

        soup = BeautifulSoup(response.content, 'html.parser')
        
        # On cible le tableau des noms (surname-table)
        # La structure est identique à celle des prénoms (image_bc2eb5.png)
        lignes = soup.select("table.surname-table tbody tr")
        
        # Si le sélecteur ci-dessus ne donne rien, on essaie le plus générique
        if not lignes:
            lignes = soup.select("table.forename-table tbody tr")

        resultats = []

        for index, ligne in enumerate(lignes):
            colonnes = ligne.find_all("td")
            if len(colonnes) >= 3:
                # Calcul du rang basé sur l'ordre d'apparition
                rang = index + 1 
                nom_famille = colonnes[1].get_text(strip=True) # Colonne du nom
                incidence = colonnes[2].get_text(strip=True) # Nombre de personnes
                frequence = colonnes[3].get_text(strip=True) if len(colonnes) > 3 else "N/A"
                
                resultats.append({
                    "rang": rang,
                    "nom_famille": nom_famille,
                    "nombre_personnes": incidence,
                    "frequence": frequence
                })

        # Sauvegarde au format JSON
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(resultats, f, ensure_ascii=False, indent=4)

        print(f"Succès ! {len(resultats)} noms de famille extraits dans '{file_name}'.")

    except Exception as e:
        print(f"Erreur lors de l'extraction : {e}")

if __name__ == "__main__":
    scrape_noms_famille_mondial()
    