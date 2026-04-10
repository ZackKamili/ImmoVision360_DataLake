import os
import re
import pandas as pd
from pathlib import Path
from tqdm import tqdm

# Configuration
BASE_DIR = Path(__file__).parent.parent
TEXTS_DIR = BASE_DIR / "data/raw/texts"
OUTPUT_DIR = BASE_DIR / "data/processed"
OUTPUT_FILE = OUTPUT_DIR / "nlp_scores.csv"

# Mots-clés pour l'analyse de déshumanisation
KEYWORDS_HOTELIZED = [
    r"bo[îi]te [àa] cl[ée]s", r"lockbox", r"conciergerie", r"agence", r"professionnel",
    r"check-in automatique", r"self check-in", r"code", r"instruction", r"management",
    r"entreprise", r"soci[ée]t[ée]", r"automatis[ée]"
]

KEYWORDS_HUMAN = [
    r"merci", r"accueillant", r"chaleureux", r"gentil", r"disponible", r"rencontre",
    r"conseils", r"attentionn[ée]", r"hôte", r"hospitalit[ée]", r"bienveillant"
]

def analyze_text(text):
    """
    Analyse un texte pour déterminer un score de déshumanisation.
    Score : -1 (Humain), 0 (Neutre), 1 (Hôtélisé/Pro)
    """
    text = text.lower()
    
    # Comptage des occurrences
    hotel_hits = sum(1 for kw in KEYWORDS_HOTELIZED if re.search(kw, text))
    human_hits = sum(1 for kw in KEYWORDS_HUMAN if re.search(kw, text))
    
    # Logique de scoring simplifiée
    if hotel_hits > human_hits:
        return 1
    elif human_hits > hotel_hits + 2: # On exige plus de preuves pour le "très humain"
        return -1
    else:
        return 0

def process_nlp():
    print("\n" + "="*60)
    print("🤖 IMMOVISION360 - INTELLIGENCE NLP (PHASE 2)")
    print("="*60)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    files = list(TEXTS_DIR.glob("*.txt"))
    if not files:
        print("❌ Aucun fichier texte trouvé dans data/raw/texts")
        return
        
    results = []
    
    print(f"📊 Analyse de {len(files)} fichiers d'annonces...")
    for file_path in tqdm(files, desc="Analyse NLP"):
        listing_id = file_path.stem
        try:
            content = file_path.read_text(encoding="utf-8")
            
            # Extraction des commentaires uniquement (après la ligne "Commentaire :")
            # Le format du fichier 02_ingestion_textes.py est structuré avec des "Review #X"
            comments_only = " ".join(re.findall(r"Commentaire :\s*• (.*)", content))
            
            score = analyze_text(comments_only)
            
            results.append({
                "listing_id": listing_id,
                "neighborhood_impact_score": score,
                "hotel_keywords_found": sum(1 for kw in KEYWORDS_HOTELIZED if re.search(kw, comments_only.lower())),
                "human_keywords_found": sum(1 for kw in KEYWORDS_HUMAN if re.search(kw, comments_only.lower()))
            })
        except Exception as e:
            print(f"⚠️ Erreur sur le fichier {listing_id}: {e}")
            
    df_results = pd.DataFrame(results)
    df_results.to_csv(OUTPUT_FILE, index=False)
    
    print("\n" + "="*60)
    print("📊 RÉSULTATS DE L'ANALYSE")
    print("="*60)
    print(f"Scores générés : {len(df_results)}")
    print(f"Fichier sauvegardé : {OUTPUT_FILE}")
    print("\nRépartition des scores :")
    print(df_results["neighborhood_impact_score"].value_counts().sort_index())
    print("="*60)

if __name__ == "__main__":
    process_nlp()
