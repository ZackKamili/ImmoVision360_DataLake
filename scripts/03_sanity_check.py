"""
==============================================================================
 ImmoVision 360 - Phase 1 | Script 03 : Sanity Check du Data Lake
==============================================================================
 Auteur  : Data Engineer - Projet ImmoVision 360
 Mission : Auditer la qualité et la complétude du Data Lake Bronze.
           Vérifier la cohérence entre les données attendues (CSV) et
           les fichiers physiquement présents sur le disque.
==============================================================================
"""

import os
import sys
import csv
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# 0. CONFIGURATION — Adaptez ces chemins à votre arborescence locale
# ─────────────────────────────────────────────────────────────────────────────

BASE_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LISTINGS_CSV = os.path.join(BASE_DIR, "data", "raw", "tabular", "listings.csv")
IMAGES_DIR   = os.path.join(BASE_DIR, "data", "raw", "images")
TEXTS_DIR    = os.path.join(BASE_DIR, "data", "raw", "texts")

# Filtre quartier (doit correspondre au filtre appliqué dans les scripts 01 & 02)
TARGET_NEIGHBOURHOOD = "Élysée"

# Nombre d'orphelins à afficher dans le rapport
MAX_ORPHANS_DISPLAY = 5


# ─────────────────────────────────────────────────────────────────────────────
# 1. HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def separator(char="─", width=70):
    print(char * width)

def print_header(title: str):
    separator("═")
    print(f"  {title}")
    separator("═")

def print_section(title: str):
    print(f"\n{'─'*70}")
    print(f"  🔍 {title}")
    separator()


# ─────────────────────────────────────────────────────────────────────────────
# 2. LECTURE DU CATALOGUE (Source de vérité)
# ─────────────────────────────────────────────────────────────────────────────

def load_expected_ids(csv_path: str, neighbourhood_filter: str) -> list[str]:
    """
    Lit listings.csv et retourne la liste des IDs attendus
    pour le quartier cible (même filtre que scripts 01 & 02).
    """
    if not os.path.exists(csv_path):
        print(f"[ERREUR CRITIQUE] Fichier introuvable : {csv_path}")
        sys.exit(1)

    expected_ids = []
    total_rows   = 0
    skipped_rows = 0

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        # Vérification des colonnes obligatoires
        required_cols = {"id", "neighbourhood_cleansed"}
        if not required_cols.issubset(set(reader.fieldnames or [])):
            missing = required_cols - set(reader.fieldnames or [])
            print(f"[ERREUR CRITIQUE] Colonnes manquantes dans le CSV : {missing}")
            sys.exit(1)

        for row in reader:
            total_rows += 1
            try:
                listing_id    = str(row["id"]).strip()
                neighbourhood = row.get("neighbourhood_cleansed", "").strip()

                if not listing_id:
                    skipped_rows += 1
                    continue

                # Filtre géographique (identique aux scripts 01 & 02)
                if neighbourhood_filter and neighbourhood != neighbourhood_filter:
                    continue

                expected_ids.append(listing_id)

            except Exception as e:
                skipped_rows += 1
                print(f"  [WARN] Ligne corrompue ignorée : {e}")

    print(f"  Total lignes lues dans le CSV    : {total_rows:>6}")
    print(f"  Lignes ignorées (corrompues)     : {skipped_rows:>6}")
    print(f"  Annonces ciblées ({neighbourhood_filter:<12})  : {len(expected_ids):>6}")
    return expected_ids


# ─────────────────────────────────────────────────────────────────────────────
# 3. COMPTAGE PHYSIQUE
# ─────────────────────────────────────────────────────────────────────────────

def count_physical_files(directory: str, extension: str) -> set[str]:
    """
    Retourne l'ensemble des stems (noms sans extension) des fichiers
    présents dans le répertoire avec l'extension donnée.
    """
    if not os.path.exists(directory):
        print(f"  [WARN] Dossier inexistant : {directory}")
        return set()

    files = {
        os.path.splitext(f)[0]
        for f in os.listdir(directory)
        if f.lower().endswith(extension)
    }
    return files


# ─────────────────────────────────────────────────────────────────────────────
# 4. ANALYSE DES ORPHELINS
# ─────────────────────────────────────────────────────────────────────────────

def find_orphans(expected_ids: list[str], physical_ids: set[str]) -> list[str]:
    """
    Retourne la liste des IDs attendus mais absents physiquement.
    """
    return [id_ for id_ in expected_ids if id_ not in physical_ids]

def find_phantoms(expected_ids: list[str], physical_ids: set[str]) -> list[str]:
    """
    Retourne les fichiers présents physiquement mais non référencés
    dans le CSV (ex: résidus d'un ancien run ou erreur de nommage).
    """
    expected_set = set(expected_ids)
    return [id_ for id_ in physical_ids if id_ not in expected_set]


# ─────────────────────────────────────────────────────────────────────────────
# 5. RAPPORT TERMINAL
# ─────────────────────────────────────────────────────────────────────────────

def print_report(
    expected_ids : list[str],
    img_ids      : set[str],
    txt_ids      : set[str],
    img_orphans  : list[str],
    txt_orphans  : list[str],
    img_phantoms : list[str],
    txt_phantoms : list[str],
):
    n_expected   = len(expected_ids)
    n_images     = len(img_ids)
    n_texts      = len(txt_ids)

    rate_img = (n_images / n_expected * 100) if n_expected else 0
    rate_txt = (n_texts  / n_expected * 100) if n_expected else 0

    print_header("RAPPORT DE SANITY CHECK — ImmoVision 360 Data Lake")
    print(f"  Généré le : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Quartier  : {TARGET_NEIGHBOURHOOD}")

    # ── Comptages ──────────────────────────────────────────────────────────
    print_section("Comptages")
    print(f"  Total annonces CSV (attendues)   : {n_expected:>6}")
    print(f"  Images .jpg présentes            : {n_images:>6}   ({rate_img:.1f}%)")
    print(f"  Textes  .txt présents            : {n_texts:>6}   ({rate_txt:.1f}%)")

    # ── Statut global ──────────────────────────────────────────────────────
    print_section("Statut Global")
    status_img = "✅ COMPLET" if not img_orphans else f"⚠️  INCOMPLET ({len(img_orphans)} manquants)"
    status_txt = "✅ COMPLET" if not txt_orphans else f"⚠️  INCOMPLET ({len(txt_orphans)} manquants)"
    print(f"  Images : {status_img}")
    print(f"  Textes : {status_txt}")

    # ── Orphelins (IDs attendus mais fichier absent) ───────────────────────
    print_section(f"Orphelins Images (IDs sans .jpg) — {len(img_orphans)} au total")
    if img_orphans:
        for oid in img_orphans[:MAX_ORPHANS_DISPLAY]:
            print(f"    ✗  {oid}.jpg")
        if len(img_orphans) > MAX_ORPHANS_DISPLAY:
            print(f"    ... et {len(img_orphans) - MAX_ORPHANS_DISPLAY} autres.")
    else:
        print("    Aucun orphelin détecté 🎉")

    print_section(f"Orphelins Textes (IDs sans .txt) — {len(txt_orphans)} au total")
    if txt_orphans:
        for oid in txt_orphans[:MAX_ORPHANS_DISPLAY]:
            print(f"    ✗  {oid}.txt")
        if len(txt_orphans) > MAX_ORPHANS_DISPLAY:
            print(f"    ... et {len(txt_orphans) - MAX_ORPHANS_DISPLAY} autres.")
    else:
        print("    Aucun orphelin détecté 🎉")

    # ── Fantômes (fichiers physiques non référencés dans le CSV) ──────────
    print_section(f"Fantômes Images (fichiers sans entrée CSV) — {len(img_phantoms)} au total")
    if img_phantoms:
        for fid in img_phantoms[:MAX_ORPHANS_DISPLAY]:
            print(f"    ⚠  {fid}.jpg")
        if len(img_phantoms) > MAX_ORPHANS_DISPLAY:
            print(f"    ... et {len(img_phantoms) - MAX_ORPHANS_DISPLAY} autres.")
    else:
        print("    Aucun fantôme détecté 🎉")

    # ── Synthèse chiffrée ──────────────────────────────────────────────────
    print_section("Synthèse à copier dans votre README.md")
    separator("─")
    print(f"""
  Quartier ciblé          : {TARGET_NEIGHBOURHOOD}
  Annonces attendues      : {n_expected}

  Images collectées       : {n_images} / {n_expected}  ({rate_img:.1f}%)
  Images manquantes       : {len(img_orphans)}
  Fichiers fantômes       : {len(img_phantoms)}

  Textes collectés        : {n_texts} / {n_expected}  ({rate_txt:.1f}%)
  Textes manquants        : {len(txt_orphans)}
""")
    separator("═")
    print("  Sanity Check terminé. Consultez les résultats ci-dessus.")
    separator("═")


# ─────────────────────────────────────────────────────────────────────────────
# 6. MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print_header("Démarrage du Sanity Check — ImmoVision 360")

    # Étape 1 : Charger les IDs théoriques depuis le CSV
    print_section("Étape 1 — Lecture du catalogue CSV (source de vérité)")
    expected_ids = load_expected_ids(LISTINGS_CSV, TARGET_NEIGHBOURHOOD)

    # Étape 2 : Compter les fichiers physiques
    print_section("Étape 2 — Inventaire physique du Data Lake")
    img_ids = count_physical_files(IMAGES_DIR, ".jpg")
    txt_ids = count_physical_files(TEXTS_DIR,  ".txt")
    print(f"  Fichiers .jpg trouvés dans {IMAGES_DIR} : {len(img_ids)}")
    print(f"  Fichiers .txt trouvés dans {TEXTS_DIR}  : {len(txt_ids)}")

    # Étape 3 : Jointure et détection des écarts
    print_section("Étape 3 — Jointure CSV ↔ Disque")
    img_orphans  = find_orphans (expected_ids, img_ids)
    txt_orphans  = find_orphans (expected_ids, txt_ids)
    img_phantoms = find_phantoms(expected_ids, img_ids)
    txt_phantoms = find_phantoms(expected_ids, txt_ids)

    # Étape 4 : Affichage du rapport complet
    print_report(
        expected_ids, img_ids, txt_ids,
        img_orphans, txt_orphans,
        img_phantoms, txt_phantoms
    )


if __name__ == "__main__":
    main()