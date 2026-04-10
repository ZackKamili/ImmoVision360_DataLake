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
NLP_CSV     = BASE_DIR / "data/processed/nlp_scores.csv"

def update_database():
    print("\n" + "="*60)
    print("📤 MISE À JOUR DE LA BASE DE DONNÉES (NLP SCORES)")
    print("="*60)

    if not NLP_CSV.exists():
        print(f"❌ Fichier non trouvé : {NLP_CSV}")
        return

    # Chargement des scores
    df_nlp = pd.read_csv(NLP_CSV)
    print(f"✅ {len(df_nlp)} scores chargés depuis le CSV.")

    # Connexion DB
    engine = create_engine(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    
    try:
        with engine.begin() as conn:
            print(f"🔄 Mise à jour de la table '{TABLE}'...")
            
            # Pour chaque score, on met à jour la ligne correspondante
            # On utilise listing_id du CSV pour matcher id de la table
            for _, row in df_nlp.iterrows():
                query = text(f"""
                    UPDATE {TABLE} 
                    SET neighborhood_impact_score = :score 
                    WHERE id = :id
                """)
                conn.execute(query, {"score": int(row['neighborhood_impact_score']), "id": int(row['listing_id'])})
            
            print("✨ Mise à jour terminée avec succès !")
            
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour : {e}")

if __name__ == "__main__":
    update_database()
