# ImmoVision 360 — Data Lake Bronze | Phase 1

## Titre et Contexte

Ce dépôt constitue le livrable de la **Phase 1** du projet **ImmoVision 360**, réalisé dans le cadre du cours *Collecte et exploration des données*.

**Mission :** Construire la zone Bronze (Raw Data) du Data Lake destiné à analyser le phénomène de gentrification dans le quartier de l'**Élysée à Paris**, à partir des données publiques de la plateforme **Inside Airbnb**.

**Commanditaire fictif :** Mairie de Paris (Anne Hidalgo)

**Objectif analytique :** Tester trois hypothèses sur la gentrification :
- 🏠 Hypothèse Standardisation — uniformisation visuelle des logements (IA Vision)
- 💬 Hypothèse Déshumanisation — disparition du lien social dans les avis (NLP)
- 💰 Hypothèse Machine à Cash — concentration des revenus (Stats)

---

## Notice d'Exécution

### Prérequis
pip install requests pandas Pillow tqdm

### Étape 1 — Images
python scripts/01_ingestion_images.py

### Étape 2 — Textes
python scripts/02_ingestion_textes.py

### Étape 3 — Sanity Check
python scripts/03_sanity_check.py

---

## Audit des Données — Résultats du Sanity Check

Généré le : 2026-04-06 | Quartier : Élysée

| Source        | Attendues | Collectées | Taux  | Manquants |
|---------------|-----------|------------|-------|-----------|
| Images (.jpg) | 2 625     | 2 492      | 94.9% | 133       |
| Textes (.txt) | 2 625     | 1 958      | 74.6% | 667       |

---

## Analyse des Pertes

**Images (133 manquantes — 5.1%) :** Liens expirés (HTTP 404) ou blocage anti-bot (HTTP 429) côté Airbnb. Taux de 94.9% excellent pour un scraping sans infrastructure dédiée.

**Textes (667 manquants — 25.4%) :** Ces annonces n'ont aucun commentaire dans reviews.csv. Il s'agit de biens récents ou jamais réservés — ce n'est pas une défaillance technique mais une réalité métier.
