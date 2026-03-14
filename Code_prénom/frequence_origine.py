import asyncio
import pandas as pd
from playwright.async_api import async_playwright
from tqdm.asyncio import tqdm

# --- CONFIGURATION TURBO ---
ROOT_URL = "https://forebears.io/forenames"
CONCURRENCY_LIMIT = 10  # On traite 10 noms en parallèle

async def block_aggressively(route):
    """Bloque les images, CSS et polices pour accélérer le chargement."""
    if route.request.resource_type in ["image", "stylesheet", "font", "media"]:
        await route.abort()
    else:
        await route.continue_()

async def scrape_details(context, slug, semaphore, pbar):
    async with semaphore:
        page = await context.new_page()
        # Optimisation réseau : ne charger que le HTML
        await page.route("**/*", block_aggressively)
        
        url = f"https://forebears.io/forenames/{slug}"
        try:
            # wait_until="commit" est le plus rapide possible
            await page.goto(url, wait_until="commit", timeout=20000)
            
            # Attente courte pour le tableau
            table_selector = "table.sur-stats"
            await page.wait_for_selector(table_selector, timeout=5000)
            
            data = await page.evaluate("""(selector) => {
                const rows = Array.from(document.querySelectorAll(`${selector} tbody tr`));
                return rows.map(row => {
                    const cols = row.querySelectorAll('td');
                    if (cols.length >= 3) {
                        return {
                            'pays': cols[1]?.innerText.trim() || 'Inconnu',
                            'frequence': cols[2]?.innerText.trim().replace(/[, ]/g, '') || '0',
                            'ratio': cols[3]?.innerText.trim() || ''
                        };
                    }
                    return null;
                }).filter(i => i !== null);
            }""", table_selector)
            
            for entry in data: entry['prenom'] = slug
            return data
        except:
            return []
        finally:
            pbar.update(1)
            await page.close()

async def main():
    async with async_playwright() as p:
        # Lancement avec des arguments de performance Chrome
        browser = await p.chromium.launch(headless=True, args=["--disable-gpu", "--no-sandbox"])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        
        main_page = await context.new_page()
        semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)

        print(f"Initialisation Turbo sur {ROOT_URL}...")
        await main_page.goto(ROOT_URL, wait_until="networkidle")
        
        sections = await main_page.evaluate("""() => {
            return Array.from(document.querySelectorAll('ul.pagination li a')).map(a => ({
                text: a.innerText.trim(),
                href: a.href
            }));
        }""")
        
        main_pbar = tqdm(total=len(sections), desc="Total Global", unit="section")

        for section in sections:
            letter_text = section['text']
            try:
                await main_page.goto(section['href'], wait_until="domcontentloaded")
                await main_page.wait_for_selector("a.search-result", timeout=10000)

                slugs = await main_page.evaluate("""() => {
                    return Array.from(document.querySelectorAll('a.search-result'))
                                .map(a => a.getAttribute('href')?.split('/').filter(p => p).pop())
                                .filter(s => s);
                }""")
                
                if slugs:
                    sub_pbar = tqdm(total=len(slugs), desc=f" > {letter_text}", unit="nom", leave=False)
                    # Lancement massif des tâches
                    tasks = [scrape_details(context, s, semaphore, sub_pbar) for s in slugs]
                    results = await asyncio.gather(*tasks)
                    sub_pbar.close()

                    flat_data = [item for sublist in results for item in sublist]
                    if flat_data:
                        safe_name = "".join([c for c in letter_text if c.isalnum()])
                        pd.DataFrame(flat_data).to_csv(f"data_{safe_name}.csv", index=False, encoding='utf-8')

            except Exception as e:
                print(f"\nErreur section {letter_text}: {e}")
            
            main_pbar.update(1)

        main_pbar.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())