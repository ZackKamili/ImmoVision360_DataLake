import re
import sys
import logging
import argparse
from pathlib import Path
from datetime import datetime
import pandas as pd
from tqdm import tqdm


class Config:
    BASE_DIR = Path(__file__).parent.parent
    LISTINGS_PATH = BASE_DIR / "data/raw/tabular/listings.csv"
    REVIEWS_PATH = BASE_DIR / "data/raw/tabular/reviews.csv"
    TEXTS_DIR = BASE_DIR / "data/raw/texts"
    LOG_FILE = BASE_DIR / "scripts/ingestion_textes.log"

    TARGET_NEIGHBOURHOOD = "Élysée"
    NEIGHBOURHOOD_COLUMN = "neighbourhood_cleansed"

    LISTING_ID_COL = "listing_id"
    COMMENTS_COL = "comments"
    DATE_COL = "date"
    REVIEWER_COL = "reviewer_name"

    MIN_COMMENT_LENGTH = 10


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(Config.LOG_FILE, encoding="utf-8"),
        ],
    )
    return logging.getLogger(__name__)


logger = setup_logging()


def clean_html(text):
    if pd.isna(text) or not isinstance(text, str):
        return ""

    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)

    html_entities = {
        "&nbsp;": " ",
        "&amp;": "&",
        "&lt;": "<",
        "&gt;": ">",
        "&quot;": '"',
        "&#39;": "'",
        "&apos;": "'",
    }
    for entity, char in html_entities.items():
        text = text.replace(entity, char)

    text = re.sub(r" +", " ", text)
    text = re.sub(r"\n+", "\n", text)

    return text.strip()


def clean_text(text):
    if pd.isna(text) or not isinstance(text, str):
        return ""

    text = clean_html(text)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    return text.strip()


def load_elysee_listings():
    logger.info(f"📂 Chargement : {Config.LISTINGS_PATH}")

    if not Config.LISTINGS_PATH.exists():
        logger.error(f"❌ Fichier non trouvé : {Config.LISTINGS_PATH}")
        sys.exit(1)

    df = pd.read_csv(Config.LISTINGS_PATH)
    logger.info(f"   → {len(df)} annonces totales")

    df_elysee = df[df[Config.NEIGHBOURHOOD_COLUMN] == Config.TARGET_NEIGHBOURHOOD]
    elysee_ids = set(df_elysee["id"].tolist())

    logger.info(f"🎯 Quartier '{Config.TARGET_NEIGHBOURHOOD}' : {len(elysee_ids)} annonces")
    return elysee_ids


def load_reviews(elysee_ids):
    logger.info(f"📂 Chargement : {Config.REVIEWS_PATH}")

    if not Config.REVIEWS_PATH.exists():
        logger.error(f"❌ Fichier non trouvé : {Config.REVIEWS_PATH}")
        sys.exit(1)

    df = pd.read_csv(Config.REVIEWS_PATH)
    logger.info(f"   → {len(df)} reviews totales")

    required_cols = [
        Config.LISTING_ID_COL,
        Config.COMMENTS_COL,
        Config.DATE_COL,
        Config.REVIEWER_COL,
    ]
    if not all(col in df.columns for col in required_cols):
        logger.error(f"❌ Colonnes manquantes dans reviews.csv : {required_cols}")
        sys.exit(1)

    df_filtered = df[df[Config.LISTING_ID_COL].isin(elysee_ids)]
    logger.info(f"🎯 Reviews pour Élysée : {len(df_filtered)}")
    return df_filtered


def group_reviews_by_listing(df_reviews):
    logger.info("📊 Regroupement des reviews par annonce...")
    grouped = {}

    for listing_id in df_reviews[Config.LISTING_ID_COL].unique():
        listing_reviews = df_reviews[df_reviews[Config.LISTING_ID_COL] == listing_id]

        reviews_list = []
        for _, row in listing_reviews.iterrows():
            comment = clean_text(row.get(Config.COMMENTS_COL, ""))
            if len(comment) < Config.MIN_COMMENT_LENGTH:
                continue

            reviews_list.append(
                {
                    "date": str(row.get(Config.DATE_COL, "N/A")),
                    "reviewer": str(row.get(Config.REVIEWER_COL, "Anonyme")),
                    "comment": comment,
                }
            )

        if reviews_list:
            grouped[listing_id] = reviews_list

    logger.info(f"   → {len(grouped)} annonces avec reviews valides")
    return grouped


def write_text_file(listing_id, reviews, overwrite=False):
    output_path = Config.TEXTS_DIR / f"{listing_id}.txt"

    if output_path.exists() and not overwrite:
        return False, "skip"

    try:
        lines = [
            "=" * 60,
            f"Commentaires pour l'annonce {listing_id}",
            f"Nombre de reviews : {len(reviews)}",
            f"Généré le : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 60,
            "",
        ]

        for idx, review in enumerate(reviews, 1):
            lines.extend(
                [
                    f"--- Review #{idx} ---",
                    f"Date : {review['date']}",
                    f"Auteur : {review['reviewer']}",
                    "Commentaire :",
                    f"  • {review['comment']}",
                    "",
                ]
            )

        output_path.write_text("\n".join(lines), encoding="utf-8")
        return True, "ok"

    except Exception as e:
        return False, f"error: {e}"


def run_ingestion(overwrite=False):
    print("\n" + "=" * 60)
    print("📝 IMMOVISION360 - INGESTION DES TEXTES")
    print("=" * 60)

    if overwrite:
        print("⚠️ Mode OVERWRITE activé")

    Config.TEXTS_DIR.mkdir(parents=True, exist_ok=True)

    elysee_ids = load_elysee_listings()
    if not elysee_ids:
        logger.error("❌ Aucune annonce trouvée pour le quartier Élysée")
        return

    df_reviews = load_reviews(elysee_ids)
    if df_reviews.empty:
        logger.warning("⚠️ Aucune review trouvée pour le quartier Élysée")
        return

    grouped_reviews = group_reviews_by_listing(df_reviews)

    stats = {"ok": 0, "skip": 0, "err": 0}
    print("\n" + "-" * 60)
    print("📄 CRÉATION DES FICHIERS TEXTE")
    print("-" * 60 + "\n")

    for listing_id, reviews in tqdm(grouped_reviews.items(), desc="Génération"):
        success, status = write_text_file(listing_id, reviews, overwrite)
        if status == "ok":
            stats["ok"] += 1
        elif status == "skip":
            stats["skip"] += 1
        else:
            stats["err"] += 1
            logger.warning(f"❌ Erreur pour ID {listing_id}: {status}")

    print("\n" + "=" * 60)
    print("📊 RAPPORT FINAL")
    print("=" * 60)
    print(f"Fichiers créés : {stats['ok']}")
    print(f"Ignorés      : {stats['skip']}")
    print(f"Erreurs      : {stats['err']}")
    print(f"Annonces traitées : {len(grouped_reviews)}")
    print(f"Reviews traitées  : {sum(len(v) for v in grouped_reviews.values())}")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Ingestion des textes Airbnb")
    parser.add_argument(
        "--overwrite", action="store_true", help="Écraser les fichiers existants"
    )
    parser.add_argument(
        "--neighbourhood",
        default=Config.TARGET_NEIGHBOURHOOD,
        help="Quartier cible",
    )
    args = parser.parse_args()

    Config.TARGET_NEIGHBOURHOOD = args.neighbourhood

    try:
        run_ingestion(overwrite=args.overwrite)
    except KeyboardInterrupt:
        print("\nInterruption par l'utilisateur.")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Erreur fatale : {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()