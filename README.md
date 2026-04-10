# ImmoVision 360 — Intelligence Urbaine & Data Lake

## 🏙️ Contexte et Mission
**ImmoVision 360** est une plateforme d'aide à la décision stratégique destinée à la **Mairie de Paris**. L'objectif est de transformer des flux de données hétérogènes (multimodaux) en un diagnostic précis sur le phénomène de **gentrification touristique** dans le quartier de l'Élysée.

### Les 3 Hypothèses de Diagnostic :
- 💰 **Machine à Cash :** Concentration industrielle des biens (Top 5% des hôtes).
- 💬 **Déshumanisation :** Rupture du lien social détectée par analyse **NLP** des avis.
- 🏠 **Standardisation :** Uniformisation visuelle "Airbnb-style" détectée par **IA Vision**.

---

## 🚀 Architecture du Projet
Le projet suit une architecture de Data Lake moderne (Bronze ➔ Silver ➔ Gold) :

1.  **Collecte (Bronze) :** Ingestion massive d'images (.jpg), de témoignages (.txt) et de métriques Airbnb (.csv).
2.  **Intelligence (Silver/Gold) :** 
    - Analyse de sentiment et mots-clés pro via **NLP**.
    - Analyse de luminosité et contraste via **Computer Vision**.
3.  **Warehouse :** Stockage structuré dans **PostgreSQL** pour corréler les scores IA avec les données financières.
4.  **Décision (EDA) :** Génération automatique de diagnostics visuels et recommandations politiques.

---

## 🛠️ Installation et Exécution

### Prérequis
- Python 3.9+
- PostgreSQL (Base `immovision` avec table `elysee_tabular`)
- Bibliothèques : `pip install pandas sqlalchemy psycopg2 pillow tqdm matplotlib`

### Lancer le Pipeline Complet
Pour exécuter l'ensemble de la chaîne de valeur (de l'ingestion au diagnostic final) :
```bash
python scripts/run_all_pipeline.py
```

---

## 📊 Résultats du Diagnostic (Quartier Élysée)
*Les graphiques et analyses détaillées sont générés automatiquement dans le dossier :* `eda_outputs/`

> **Note importante :** Pour comprendre à quelles questions répondent les graphiques (Hypothèses 1, 2 et 3), consultez la [**Synthèse et Explication des Graphiques**](SYNTHESE_GRAPHIQUES.md).

- **Indice de concentration :** 59% des annonces contrôlées par 5% des hôtes.
- **Taux de professionnalisation (NLP) :** 18.6% d'avis typés "hôteliers".
- **Standardisation visuelle :** Tendance détectée sur les appartements à haute rotation.

---

## 📁 Structure du Dépôt
- `data/raw/` : Matière brute (Images, Textes).
- `data/processed/` : Scores générés par l'IA.
- `scripts/` : Pipeline complet (01 à 08 + orchestrateur).
- `eda_outputs/` : Livrables pour la Mairie de Paris.

**Auteur :** Projet ImmoVision 360 - Collecte & Exploration des Données
