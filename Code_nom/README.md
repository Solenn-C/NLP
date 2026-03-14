Pipeline de Constitution de Base de Données (Noms)

🚀 Ordre d'exécution des scripts
Pour reconstruire la base de données complète, veuillez suivre l'ordre suivant :

1. Collecte des données (Scraping)
scrapping_prenoms.py : Récupère la base source des prénoms (noms, genres, origines) sur Behind the Name.

scrap_rang_mondial.py : Extrait le classement mondial simplifié des prénoms sur Forebears.

frequence_origine.py : Script asynchrone (Turbo) pour récupérer les fréquences détaillées par pays pour chaque prénom.

2. Traitement et Normalisation
traitement_prénom.py : Nettoie les données brutes, calcule les "skeletons" phonétiques et identifie les variantes textuelles (Fuzzy Matching). Calcule également les scores de précision (F1-Score).

pays_corriger.py : Unifie et traduit les origines (ex: "Arabic" -> "Arabie") et nettoie les métadonnées inutiles.

3. Enrichissement et Fusion
colonne_json.py : Ajoute les étiquettes de type (ex: "type": "prenom") pour structurer le JSON final.

fusion_BDD_rang.py : Fusionne la base des prénoms avec les statistiques de rang mondial (incidence et fréquence).

fusion_BDD_rang_nom.py : Fusionne la base des noms de famille avec les statistiques de rang mondial en utilisant une normalisation stricte pour les jointures.

📊 Structure des données finales
Le fichier de sortie final regroupe les informations suivantes par entrée :

Identification : Nom, genre, type.

Expertise : Origines nettoyées et variantes identifiées.

Statistiques : Rang mondial, incidence (nombre de personnes) et fréquence.

⚖️ Évaluation
Le script traitement_prénom.py inclut un module d'évaluation qui compare les variantes trouvées à une "Vérité Terrain" pour calculer la Précision et le Rappel.
