## Terminal 1 : Serveur API (FastAPI)
Le backend gère la recherche dans vos bases de données JSON.

commande : python -m uvicorn main:app --reload
L'API sera accessible sur : http://127.0.0.1:8000

## Terminal 2 : Interface Utilisateur (Streamlit)
Le frontend affiche la carte interactive et les détails des noms/prénoms.

commande : streamlit run app.py
L'interface s'ouvrira automatiquement dans votre navigateur sur : http://localhost:8501
