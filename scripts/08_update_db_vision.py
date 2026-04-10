import pandas as pd
from sqlalchemy import create_engine, text
from pathlib import Path

# Configuration (identique à 07_eda.py)
DB_USER     = "postgres"
DB_PASSWORD = "1234"
DB_HOST     = "localhost"
DB_PORT     = "5432"
DB_NAME     = "immovision"
TABLE       = "elysee_tabular"

BASE_DIR    = Path(__file__).parent.parent
VISION_CSV  = BASE_DIR / "data/processed/vision_scores.csv"

def update_database():
    print("\n" + "="*60)
    print("📤 MISE À JOUR DE LA BASE DE DONNÉES (VISION SCORES)")
    print("="*60)

    if not VISION_CSV.exists():
        print(f"❌ Fichier non trouvé : {VISION_CSV}")
        return

    # Chargement des scores
    df_vision = pd.read_csv(VISION_CSV)
    print(f"✅ {len(df_vision)} scores chargés depuis le CSV.")

    # Connexion DB
    engine = create_engine(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    
    try:
        with engine.begin() as conn:
            print(f"🔄 Mise à jour de la table '{TABLE}'...")
            
            # Mise à jour des scores
            for _, row in df_vision.iterrows():
                query = text(f"""
                    UPDATE {TABLE} 
                    SET standardization_score = :score 
                    WHERE id = :id
                """)
                conn.execute(query, {"score": int(row['standardization_score']), "id": int(row['listing_id'])})
            
            print("✨ Mise à jour terminée avec succès !")
            
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour : {e}")

if __name__ == "__main__":
    update_database()
