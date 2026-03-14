import time
import pandas as pd
import string
from playwright.sync_api import sync_playwright

def scrape_btm_alphabet():
    all_results = []
    # Génère la liste ['a', 'b', 'c', ..., 'z']
    alphabet = list(string.ascii_lowercase)

    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0"
        )
        page = context.new_page()
        page.route("**/*.{png,jpg,jpeg,gif,svg}", lambda route: route.abort())

        for letter in alphabet:
            print(f"\n--- 🔠 DEBUT LETTRE : {letter.upper()} ---")
            current_url = f"https://www.behindthename.com/names/letter/{letter}"
            
            while current_url:
                try:
                    print(f"🔗 Scraping : {current_url}")
                    page.goto(current_url, wait_until="domcontentloaded", timeout=45000)
                    page.wait_for_selector(".browsename", timeout=15000)
                    
                    name_blocks = page.query_selector_all(".browsename")
                    page_count = 0

                    for block in name_blocks:
                        name_el = block.query_selector("a")
                        name = name_el.inner_text().strip() if name_el else "Inconnu"

                        origin_elements = block.query_selector_all(".usg")
                        origins = [el.inner_text().strip() for el in origin_elements]
                        origins_str = ", ".join(origins) if origins else "Inconnue"

                        gender_el = block.query_selector(".masc, .fem, .common, .gender")
                        gender = gender_el.inner_text().strip() if gender_el else "N/A"

                        if name != "Inconnu":
                            all_results.append({
                                "name": name,
                                "gender": gender,
                                "origins": origins_str
                            })
                            page_count += 1

                    print(f"✅ {page_count} prénoms récupérés sur cette page.")

                    # --- GESTION DE LA PAGINATION (Page Suivante) ---
                    # On cherche le lien "Next" ou "2", "3" dans la barre de navigation
                    next_page_el = page.query_selector("a:has-text('Next'), a:has-text('>')")
                    if next_page_el:
                        # On récupère l'URL de la page suivante
                        relative_url = next_page_el.get_attribute("href")
                        current_url = f"https://www.behindthename.com{relative_url}"
                        time.sleep(1) # Petit délai pour la courtoisie serveur
                    else:
                        current_url = None # Fin de la lettre
                
                except Exception as e:
                    print(f"⚠️ Erreur sur {current_url}: {e}")
                    current_url = None

            # Sauvegarde intermédiaire après chaque lettre (sécurité)
            temp_df = pd.DataFrame(all_results)
            temp_df.to_csv("data/dataset_nlp_final_progress.csv", index=False, encoding="utf-8-sig")

        browser.close()
    
    return all_results

# --- LANCEMENT FINAL ---
start_time = time.time()
final_data = scrape_btm_alphabet()
end_time = time.time()

if final_data:
    df = pd.DataFrame(final_data)
    df.to_csv("data/dataset_prenoms_BT_complet.csv", index=False, encoding="utf-8-sig")
    print("\n" + "="*30)
    print(f"🏆 SCRAPING TERMINE !")
    print(f"📊 Total prénoms : {len(df)}")
    print(f"⏳ Temps total : {round((end_time - start_time)/60, 2)} minutes")
    print("="*30)