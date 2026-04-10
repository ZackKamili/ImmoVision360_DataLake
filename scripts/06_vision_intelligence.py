import os
import pandas as pd
from pathlib import Path
from PIL import Image, ImageStat
from tqdm import tqdm

# Configuration
BASE_DIR = Path(__file__).parent.parent
IMAGES_DIR = BASE_DIR / "data/raw/images"
OUTPUT_DIR = BASE_DIR / "data/processed"
OUTPUT_FILE = OUTPUT_DIR / "vision_scores.csv"

def analyze_image(image_path):
    """
    Analyse simplifiée d'une image pour simuler un score de standardisation.
    Score : -1 (Personnel), 0 (Neutre), 1 (Standardisé/Airbnb-style)
    """
    try:
        with Image.open(image_path) as img:
            # On passe l'image en RGB au cas où
            img = img.convert("RGB")
            
            # Analyse de la palette de couleurs (Proxy pour le minimalisme)
            # Les appartements Airbnb sont souvent très clairs (murs blancs/beiges)
            stat = ImageStat.Stat(img)
            brightness = sum(stat.mean) / 3 # Luminosité moyenne (0-255)
            std_dev = sum(stat.stddev) / 3   # Écart-type (si bas = peu de contraste/couleurs variées)
            
            # Logique heuristique :
            # - Très lumineux et peu de variation de couleurs (murs blancs dominants) -> Standardisé
            # - Contrasté avec des couleurs variées (déco perso) -> Personnel
            
            if brightness > 180 and std_dev < 40:
                return 1  # Standardisé (Clair et monotone)
            elif std_dev > 65:
                return -1 # Personnel (Beaucoup de contrastes et détails)
            else:
                return 0  # Neutre
                
    except Exception as e:
        return 0

def process_vision():
    print("\n" + "="*60)
    print("👁️ IMMOVISION360 - INTELLIGENCE VISION (PHASE 2)")
    print("="*60)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    files = list(IMAGES_DIR.glob("*.jpg"))
    if not files:
        print("❌ Aucune image trouvée dans data/raw/images")
        return
        
    results = []
    
    print(f"📊 Analyse de {len(files)} images d'annonces...")
    for file_path in tqdm(files, desc="Analyse Vision IA"):
        listing_id = file_path.stem
        
        score = analyze_image(file_path)
        
        results.append({
            "listing_id": listing_id,
            "standardization_score": score
        })
            
    df_results = pd.DataFrame(results)
    df_results.to_csv(OUTPUT_FILE, index=False)
    
    print("\n" + "="*60)
    print("📊 RÉSULTATS DE L'ANALYSE VISION")
    print("="*60)
    print(f"Scores générés : {len(df_results)}")
    print(f"Fichier sauvegardé : {OUTPUT_FILE}")
    print("\nRépartition des scores :")
    print(df_results["standardization_score"].value_counts().sort_index())
    print("="*60)

if __name__ == "__main__":
    process_vision()
