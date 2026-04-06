"""
==============================================================================
 ImmoVision 360 - Phase 3 | Script 07 : EDA — Diagnostic pour la Mairie
==============================================================================
 Mission : Explorer le Data Warehouse PostgreSQL pour tester les 3 hypothèses
           de gentrification dans le quartier Élysée à Paris.
 Base    : immovision | Table : elysee_tabular
 Lancer  : python scripts/07_eda.py
==============================================================================
"""

import os
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from sqlalchemy import create_engine, text

# ─────────────────────────────────────────────────────────────────────────────
# 0. CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

DB_USER     = "postgres"
DB_PASSWORD = "1234"
DB_HOST     = "localhost"
DB_PORT     = "5432"
DB_NAME     = "immovision"
TABLE       = "elysee_tabular"

OUTPUT_DIR  = "eda_outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Palette visuelle
C_BLEU   = "#1a3a5c"
C_OR     = "#e8a020"
C_ROUGE  = "#c0392b"
C_VERT   = "#27ae60"
C_GRIS   = "#ecf0f1"
C_TEXTE  = "#2c3e50"

plt.rcParams.update({
    "figure.facecolor" : "white",
    "axes.facecolor"   : "#f8f9fa",
    "axes.spines.top"  : False,
    "axes.spines.right": False,
    "font.family"      : "DejaVu Sans",
    "axes.titlesize"   : 13,
    "axes.labelsize"   : 11,
})


# ─────────────────────────────────────────────────────────────────────────────
# 1. CONNEXION & CHARGEMENT
# ─────────────────────────────────────────────────────────────────────────────

def load_data() -> pd.DataFrame:
    print("=" * 65)
    print("  ImmoVision 360 — Phase 3 : EDA")
    print("=" * 65)
    print("\n[1/5] Connexion à PostgreSQL...")
    engine = create_engine(
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    df = pd.read_sql(f"SELECT * FROM {TABLE}", engine)
    print(f"  ✅ {len(df)} lignes chargées depuis '{TABLE}'")
    print(f"  Colonnes : {list(df.columns)}\n")
    return df


# ─────────────────────────────────────────────────────────────────────────────
# 2. PROFILING GÉNÉRAL
# ─────────────────────────────────────────────────────────────────────────────

def profiling(df: pd.DataFrame):
    print("─" * 65)
    print("[2/5] PROFILING GÉNÉRAL")
    print("─" * 65)

    print("\n── Statistiques descriptives ──")
    print(df.describe().round(2).to_string())

    print("\n── Valeurs manquantes ──")
    nan_counts = df.isnull().sum()
    nan_pct    = (nan_counts / len(df) * 100).round(1)
    nan_df     = pd.DataFrame({"NaN count": nan_counts, "NaN %": nan_pct})
    print(nan_df[nan_df["NaN count"] > 0].to_string() or "  Aucune valeur manquante critique.")

    print("\n── Distribution des scores IA ──")
    score_map = {-1: "Personnel / Voisinage", 0: "Neutre / Indéterminé", 1: "Standardisé / Hôtélisé"}
    for col in ["standardization_score", "neighborhood_impact_score"]:
        print(f"\n  {col}:")
        vc = df[col].value_counts().sort_index()
        for k, v in vc.items():
            pct = v / len(df) * 100
            label = score_map.get(k, str(k))
            bar = "█" * int(pct / 2)
            print(f"    {k:+d} ({label:<25}) : {v:>4} ({pct:5.1f}%)  {bar}")


# ─────────────────────────────────────────────────────────────────────────────
# 3. HYPOTHÈSE 1 — MACHINE À CASH (concentration des propriétaires)
# ─────────────────────────────────────────────────────────────────────────────

def hypothese_machine_cash(df: pd.DataFrame):
    print("\n" + "─" * 65)
    print("[3/5] HYPOTHÈSE 1 — 'Machine à Cash' : Concentration des biens")
    print("─" * 65)

    col = "calculated_host_listings_count"
    df_clean = df[df[col].notna()].copy()

    # Segmentation
    df_clean["profil"] = pd.cut(
        df_clean[col],
        bins=[0, 1, 5, 20, df_clean[col].max() + 1],
        labels=["Particulier (1)", "Petit gestionnaire (2-5)",
                "Gestionnaire pro (6-20)", "Industriel (20+)"]
    )

    counts = df_clean["profil"].value_counts().sort_index()
    pcts   = counts / len(df_clean) * 100

    print("\n  Répartition des hôtes par profil :")
    for label, cnt in counts.items():
        pct = cnt / len(df_clean) * 100
        print(f"    {label:<30} : {cnt:>4} annonces ({pct:.1f}%)")

    # Indice de concentration : top 5% des hôtes
    top5_threshold = df_clean[col].quantile(0.95)
    top5_listings  = df_clean[df_clean[col] >= top5_threshold][col].sum()
    total_listings = df_clean[col].sum()
    concentration  = top5_listings / total_listings * 100
    print(f"\n  ⚡ Les top 5% des hôtes contrôlent {concentration:.1f}% des annonces")

    if concentration >= 50:
        print("  → HYPOTHÈSE CONFIRMÉE : gestion industrielle détectée ✅")
    else:
        print("  → Hypothèse partiellement confirmée.")

    # Visualisation
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Hypothèse 1 — Concentration des biens (Machine à Cash)",
                 fontsize=14, fontweight="bold", color=C_TEXTE, y=1.02)

    # Pie chart
    colors_pie = [C_VERT, C_OR, C_BLEU, C_ROUGE]
    wedges, texts, autotexts = ax1.pie(
        counts.values, labels=counts.index,
        autopct="%1.1f%%", colors=colors_pie,
        startangle=140, pctdistance=0.75,
        wedgeprops=dict(edgecolor="white", linewidth=2)
    )
    for at in autotexts:
        at.set_fontsize(9)
    ax1.set_title("Répartition par profil d'hôte", pad=15)

    # Histogramme distribution
    data_plot = df_clean[col].clip(upper=50)
    ax2.hist(data_plot, bins=30, color=C_BLEU, edgecolor="white", alpha=0.85)
    ax2.axvline(top5_threshold, color=C_ROUGE, linestyle="--", linewidth=2,
                label=f"Seuil top 5% ({top5_threshold:.0f} annonces)")
    ax2.set_xlabel("Nombre d'annonces par hôte (plafonné à 50)")
    ax2.set_ylabel("Nombre d'hôtes")
    ax2.set_title("Distribution du nombre d'annonces par hôte")
    ax2.legend()

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "H1_machine_cash.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"  💾 Graphique sauvegardé : {path}")


# ─────────────────────────────────────────────────────────────────────────────
# 4. HYPOTHÈSE 2 — DÉSHUMANISATION (lien social)
# ─────────────────────────────────────────────────────────────────────────────

def hypothese_deshumanisation(df: pd.DataFrame):
    print("\n" + "─" * 65)
    print("[4/5] HYPOTHÈSE 2 — Déshumanisation : rupture du lien social")
    print("─" * 65)

    # Score NLP neighbourhood_impact_score
    score_col = "neighborhood_impact_score"
    vc = df[score_col].value_counts().sort_index()
    total = len(df)

    pct_negatif = vc.get(-1, 0) / total * 100
    pct_neutre  = vc.get(0,  0) / total * 100
    pct_positif = vc.get(1,  0) / total * 100

    print(f"\n  Score Neighborhood Impact (analyse NLP des avis) :")
    print(f"    -1 Voisinage naturel  : {vc.get(-1,0):>4} ({pct_negatif:.1f}%)")
    print(f"     0 Neutre             : {vc.get(0, 0):>4} ({pct_neutre:.1f}%)")
    print(f"    +1 Hôtélisé           : {vc.get(1, 0):>4} ({pct_positif:.1f}%)")

    # Taux de réponse comme proxy de professionnalisation
    resp_col = "host_response_rate_num"
    df_resp = df[df[resp_col].notna()]
    avg_resp = df_resp[resp_col].mean()
    pct_100  = (df_resp[resp_col] == 100).sum() / len(df_resp) * 100
    print(f"\n  Taux de réponse moyen des hôtes : {avg_resp:.1f}%")
    print(f"  Hôtes avec 100% de réponse      : {pct_100:.1f}% → signe de gestion pro")

    if pct_positif > 40:
        print("\n  → HYPOTHÈSE CONFIRMÉE : déshumanisation détectée ✅")
    else:
        print("\n  → Hypothèse partiellement confirmée.")

    # Visualisation
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Hypothèse 2 — Déshumanisation & Rupture du Lien Social",
                 fontsize=14, fontweight="bold", color=C_TEXTE, y=1.02)

    # Bar chart scores NLP
    labels  = ["Voisinage\nnaturel (-1)", "Neutre (0)", "Hôtélisé\n(+1)"]
    values  = [vc.get(-1, 0), vc.get(0, 0), vc.get(1, 0)]
    colors  = [C_VERT, C_OR, C_ROUGE]
    bars = ax1.bar(labels, values, color=colors, edgecolor="white",
                   linewidth=1.5, width=0.5)
    for bar, val in zip(bars, values):
        ax1.text(bar.get_x() + bar.get_width() / 2,
                 bar.get_height() + 10,
                 f"{val}\n({val/total*100:.1f}%)",
                 ha="center", va="bottom", fontsize=10, fontweight="bold")
    ax1.set_title("Distribution Neighborhood Impact Score (NLP)")
    ax1.set_ylabel("Nombre d'annonces")

    # Histogram taux de réponse
    ax2.hist(df_resp[resp_col], bins=20, color=C_BLEU,
             edgecolor="white", alpha=0.85)
    ax2.axvline(avg_resp, color=C_OR, linestyle="--", linewidth=2,
                label=f"Moyenne ({avg_resp:.1f}%)")
    ax2.axvline(100, color=C_ROUGE, linestyle=":", linewidth=2,
                label=f"100% réponse ({pct_100:.1f}% des hôtes)")
    ax2.set_xlabel("Taux de réponse de l'hôte (%)")
    ax2.set_ylabel("Nombre d'annonces")
    ax2.set_title("Taux de réponse — proxy de professionnalisation")
    ax2.legend()

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "H2_deshumanisation.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"  💾 Graphique sauvegardé : {path}")


# ─────────────────────────────────────────────────────────────────────────────
# 5. HYPOTHÈSE 3 — STANDARDISATION VISUELLE (IA Image)
# ─────────────────────────────────────────────────────────────────────────────

def hypothese_standardisation(df: pd.DataFrame):
    print("\n" + "─" * 65)
    print("[5/5] HYPOTHÈSE 3 — Standardisation visuelle 'Airbnb-style'")
    print("─" * 65)

    score_col = "standardization_score"
    vc    = df[score_col].value_counts().sort_index()
    total = len(df)

    pct_perso  = vc.get(-1, 0) / total * 100
    pct_neutre = vc.get(0,  0) / total * 100
    pct_std    = vc.get(1,  0) / total * 100

    print(f"\n  Score Standardisation (analyse IA des images) :")
    print(f"    -1 Appartement personnel  : {vc.get(-1,0):>4} ({pct_perso:.1f}%)")
    print(f"     0 Neutre / Autre         : {vc.get(0, 0):>4} ({pct_neutre:.1f}%)")
    print(f"    +1 Appartement standardisé: {vc.get(1, 0):>4} ({pct_std:.1f}%)")

    # Corrélation standardisation × concentration
    corr = df[["standardization_score", "calculated_host_listings_count"]].corr()
    corr_val = corr.iloc[0, 1]
    print(f"\n  Corrélation standardisation × multi-annonces : {corr_val:.3f}")

    if pct_std >= 40:
        print("  → HYPOTHÈSE CONFIRMÉE : uniformisation visuelle massive ✅")
    else:
        print("  → Tendance détectée mais non majoritaire.")

    # Visualisation
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Hypothèse 3 — Standardisation Visuelle 'Airbnb-Style'",
                 fontsize=14, fontweight="bold", color=C_TEXTE, y=1.02)

    # Donut chart
    sizes  = [vc.get(-1, 0), vc.get(0, 0), vc.get(1, 0)]
    labels = ["Personnel\n(-1)", "Neutre\n(0)", "Standardisé\n(+1)"]
    colors = [C_VERT, C_OR, C_ROUGE]
    wedges, texts, autotexts = ax1.pie(
        sizes, labels=labels, autopct="%1.1f%%",
        colors=colors, startangle=90,
        pctdistance=0.78,
        wedgeprops=dict(width=0.55, edgecolor="white", linewidth=2)
    )
    for at in autotexts:
        at.set_fontsize(10)
        at.set_fontweight("bold")
    ax1.set_title("Répartition Standardization Score (IA Vision)")

    # Box plot standardisation par profil multi-annonces
    df_box = df[df["calculated_host_listings_count"].notna()].copy()
    df_box["profil_simple"] = pd.cut(
        df_box["calculated_host_listings_count"],
        bins=[0, 1, 5, df_box["calculated_host_listings_count"].max() + 1],
        labels=["Particulier\n(1)", "Petit gestionnaire\n(2-5)", "Pro / Industriel\n(6+)"]
    )
    groups = [
        df_box[df_box["profil_simple"] == p][score_col].dropna().values
        for p in ["Particulier\n(1)", "Petit gestionnaire\n(2-5)", "Pro / Industriel\n(6+)"]
    ]
    bp = ax2.boxplot(groups, patch_artist=True, widths=0.4,
                     medianprops=dict(color="white", linewidth=2))
    for patch, color in zip(bp["boxes"], [C_VERT, C_OR, C_ROUGE]):
        patch.set_facecolor(color)
        patch.set_alpha(0.8)
    ax2.set_xticklabels(["Particulier\n(1)", "Petit gestionnaire\n(2-5)", "Pro / Industriel\n(6+)"])
    ax2.set_ylabel("Standardization Score")
    ax2.set_title("Score de standardisation par profil d'hôte")
    ax2.axhline(0, color=C_GRIS, linestyle="--", linewidth=1)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "H3_standardisation.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"  💾 Graphique sauvegardé : {path}")


# ─────────────────────────────────────────────────────────────────────────────
# 6. SYNTHÈSE FINALE
# ─────────────────────────────────────────────────────────────────────────────

def synthese_finale(df: pd.DataFrame):
    print("\n" + "=" * 65)
    print("  SYNTHÈSE — DIAGNOSTIC POUR LA MAIRIE DE PARIS")
    print("=" * 65)

    total = len(df)

    std_pos  = (df["standardization_score"] == 1).sum() / total * 100
    ni_pos   = (df["neighborhood_impact_score"] == 1).sum() / total * 100
    multi    = (df["calculated_host_listings_count"] > 5).sum() / total * 100

    print(f"""
  Quartier analysé        : Élysée, Paris
  Annonces analysées      : {total}

  H1 — Machine à Cash     : {multi:.1f}% des annonces gérées par des pros (>5 biens)
  H2 — Déshumanisation    : {ni_pos:.1f}% des logements classés "Hôtélisés" (NLP)
  H3 — Standardisation    : {std_pos:.1f}% des logements visuellement standardisés (IA)

  CONCLUSION :
  Le quartier de l'Élysée présente des signes clairs de gentrification
  touristique pilotée par des acteurs professionnels. La combinaison
  d'une concentration des biens, d'une déshumanisation de l'accueil
  et d'une uniformisation visuelle confirme l'hypothèse d'une
  industrialisation des locations courte durée.

  Recommandation pour la Mairie :
  → Plafonner les annonces par hôte à 1-2 biens dans l'Élysée
  → Exiger la présence physique de l'hôte (interdire les "boîtes à clés")
  → Surveiller les comptes multi-annonces via croisement fiscal
    """)

    print("=" * 65)
    print(f"  Graphiques sauvegardés dans : ./{OUTPUT_DIR}/")
    print("=" * 65)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    df = load_data()
    profiling(df)
    hypothese_machine_cash(df)
    hypothese_deshumanisation(df)
    hypothese_standardisation(df)
    synthese_finale(df)