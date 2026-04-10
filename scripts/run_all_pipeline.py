import subprocess
import sys
import time
from pathlib import Path

def run_script(script_path):
    """Exécute un script python et gère le retour."""
    print(f"\n🚀 Lancement de : {script_path.name}...")
    start_time = time.time()
    
    # On s'assure d'être à la racine du projet pour l'exécution
    result = subprocess.run([sys.executable, str(script_path)], capture_output=False)
    
    if result.returncode == 0:
        duration = time.time() - start_time
        print(f"✅ {script_path.name} terminé avec succès en {duration:.1f}s")
        return True
    else:
        print(f"❌ Erreur critique dans {script_path.name}")
        return False

def main():
    scripts_dir = Path(__file__).parent
    
    pipeline = [
        # Phase 1: Ingestion
        scripts_dir / "01_ingestion_images.py",
        scripts_dir / "02_ingestion_textes.py",
        scripts_dir / "03_sanity_check.py",
        
        # Phase 2: Intelligence IA
        scripts_dir / "04_nlp_intelligence.py",
        scripts_dir / "06_vision_intelligence.py",
        
        # Phase 3: Mise à jour DB
        scripts_dir / "05_update_db_nlp.py",
        scripts_dir / "08_update_db_vision.py",
        
        # Phase 4: Diagnostic Final
        scripts_dir / "07_eda.py"
    ]

    print("="*70)
    print("      🌟 IMMOVISION 360 : PIPELINE DE DONNÉES END-TO-END 🌟")
    print("          (De la Matière Brute à l'Aide à la Décision)")
    print("="*70)
    
    start_global = time.time()
    
    for script in pipeline:
        if not script.exists():
            print(f"⚠️ Script manquant : {script}")
            continue
            
        if not run_script(script):
            print("\n🛑 Arrêt du pipeline suite à une erreur.")
            sys.exit(1)

    total_duration = time.time() - start_global
    print("\n" + "="*70)
    print(f"🎉 PIPELINE TERMINÉ AVEC SUCCÈS EN {total_duration/60:.1f} MINUTES")
    print("📂 Résultats disponibles dans : eda_outputs/")
    print("="*70)

if __name__ == "__main__":
    main()
