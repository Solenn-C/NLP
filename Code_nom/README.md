# Pipeline de Traitement : Noms de Famille

## 🚀 Ordre d'exécution des scripts

### 1. Collecte et Structuration Initiale

* **`scrap_rang_mondial_nom.py`** : Récupère le classement mondial (Forebears).
* **`main_names.py`** : Premier regroupement des noms par origine sémantique.
* **`refine_clusters.py`** : Affine les groupes en fusionnant les variantes (ex: "diminutif de").

### 2. Enrichissement Géographique (Pays)

* **`recup_pays.py`** : Extrait automatiquement les pays depuis les descriptions.
* **`recup_with_ollama.py`** : Utilise l'IA locale (TinyLlama) pour deviner les pays restants.
* **`verif_inconnu_fichier_final.py`** : Contrôle qualité pour lister les données encore inconnues.

### 3. Finalisation des Données

* **`fusion_BDD_rang_nom.py`** : Fusionne les groupes avec les statistiques mondiales.
* **`mise_en_forme_json_final.py`** : Conversion finale au format standard pour l'export.

---

## Outils de Tests & Annexes

* **`test_recherche_noms.py`** : Pour vérifier manuellement un nom dans les clusters.
* **`traitement_nom_famille.py`** : Module de nettoyage et regroupement par ID d'origine.
* **`projet.py`** : Script d'intégration globale et export Excel.

---

Est-ce que ce format plus court est plus simple à copier pour toi ?es trouvées à une "Vérité Terrain" pour c
