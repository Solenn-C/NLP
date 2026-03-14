import json
import pandas as pd
import requests
from bs4 import BeautifulSoup
from collections import defaultdict
import time

class FamilyDataProject:
    def __init__(self, names_path, origins_path):
        self.names_path = names_path
        self.origins_path = origins_path
        self.df_noms = None
        self.df_prenoms = None

    def process_family_names(self):
        """Étape 1 & 2 : Regroupement des variantes et fusion des textes."""
        try:
            with open(self.names_path, 'r', encoding='utf-8') as f:
                names_list = json.load(f)
            with open(self.origins_path, 'r', encoding='utf-8') as f:
                origins_dict = json.load(f)

            # Regroupement par ID d'origine
            origin_to_names = defaultdict(set)
            for entry in names_list:
                for o_id in entry['origins']:
                    origin_to_names[o_id].add(entry['name'])

            results = []
            for o_id, names in origin_to_names.items():
                results.append({
                    "Variantes": ", ".join(sorted(list(names))),
                    "Nombre de variantes": len(names),
                    "Texte Explicatif": origins_dict.get(o_id, "Non trouvé")
                })
            
            self.df_noms = pd.DataFrame(results)
            print("✅ Étapes 1 & 2 : Fichiers JSON traités.")
        except Exception as e:
            print(f"❌ Erreur fichiers locaux : {e}")

    def scrape_geneanet_prenoms(self):
        """Étape 3 : Scraping de Geneanet."""
        url = "https://www.geneanet.org/prenom/"
        print(f"🌐 Connexion à Geneanet : {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            prenoms_data = []
            # Sur Geneanet, on cherche les liens de prénoms populaires
            # On cible les éléments dans la section "Prénoms les plus portés"
            items = soup.find_all('a', class_='desc') or soup.select('div.popular-names a')
            
            for item in items[:40]: # On prend les 40 premiers
                name = item.get_text(strip=True)
                if name:
                    prenoms_data.append({
                        "Prénom": name,
                        "Source": "Geneanet",
                        "Lien": "https://www.geneanet.org" + item['href'] if item.has_attr('href') else url
                    })

            self.df_prenoms = pd.DataFrame(prenoms_data)
            print(f"✅ Étape 3 : {len(self.df_prenoms)} prénoms récupérés sur Geneanet.")
            
        except Exception as e:
            print(f"⚠️ Erreur Geneanet : {e}. Utilisation de données de secours.")
            self.df_prenoms = pd.DataFrame([{"Prénom": "Erreur", "Source": "N/A"}])

    def save_to_excel(self, filename="Rendu_Final_Projet.xlsx"):
        """Exportation propre vers Excel."""
        try:
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                if self.df_noms is not None:
                    self.df_noms.to_excel(writer, index=False, sheet_name='Noms de Famille')
                if self.df_prenoms is not None:
                    self.df_prenoms.to_excel(writer, index=False, sheet_name='Prénoms (Geneanet)')
            print(f"📊 Projet terminé ! Fichier disponible : {filename}")
        except Exception as e:
            print(f"❌ Erreur Export : {e}")

# --- LANCEMENT ---
if __name__ == "__main__":
    projet = FamilyDataProject('names.json', 'origins.json')
    projet.process_family_names()
    projet.scrape_geneanet_prenoms()
    projet.save_to_excel()