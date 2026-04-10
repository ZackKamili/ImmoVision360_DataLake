# 📊 Synthèse et Explication des Graphiques (Diagnostic Mairie)

Ce document détaille la finalité de chaque visualisation générée par le pipeline **ImmoVision 360** afin de répondre aux besoins de diagnostic de la Mairie de Paris.

---

## 💰 Hypothèse 1 — La Machine à Cash
**Objectif :** Mesurer l'accaparement du parc immobilier par des acteurs professionnels.

1.  **Répartition par profil d'hôte (Camembert) :**
    *   **Question traitée :** "Quelle est la structure du marché ?"
    *   **Interprétation :** Si la part des "Industriels (20+ biens)" dépasse 20%, le quartier n'est plus une zone de partage mais une zone d'exploitation commerciale.
2.  **Distribution du nombre d'annonces (Histogramme) :**
    *   **Question traitée :** "Y a-t-il un monopole de fait ?"
    *   **Interprétation :** Le seuil du "Top 5%" permet de quantifier la concentration. Dans l'Élysée, 5% des hôtes contrôlent 59% de l'offre, confirmant une "Machine à Cash".

---

## 💬 Hypothèse 2 — La Déshumanisation
**Objectif :** Évaluer l'érosion du lien social et de l'hospitalité traditionnelle.

1.  **Neighborhood Impact Score (Barres NLP) :**
    *   **Question traitée :** "Comment les voyageurs perçoivent-ils leur accueil ?"
    *   **Interprétation :** Un score de +1 (Hôtélisé) indique des avis mentionnant "boîte à clés" ou "agence", signifiant la disparition de la rencontre humaine.
2.  **Taux de réponse des hôtes (Histogramme) :**
    *   **Question traitée :** "L'accueil est-il professionnalisé ?"
    *   **Interprétation :** Une concentration massive à 100% de réponse avec un délai "en moins d'une heure" est la signature de l'utilisation de gestionnaires de flux (Channel Managers) et non d'une réponse humaine naturelle.

---

## 🏠 Hypothèse 3 — La Standardisation
**Objectif :** Analyser l'impact visuel de la location courte durée sur l'esthétique urbaine.

1.  **Standardization Score (Donut IA Vision) :**
    *   **Question traitée :** "Les intérieurs parisiens sont-ils en train de s'uniformiser ?"
    *   **Interprétation :** Mesure la prédominance du style "Minimaliste/Ikea" (murs blancs, meubles neutres) au détriment du charme historique parisien (bibelots, déco personnelle).
2.  **Score par profil d'hôte (Boxplot) :**
    *   **Question traitée :** "Est-ce que le multi-listing entraîne la standardisation ?"
    *   **Interprétation :** Ce graphique corrèle les données financières et visuelles. Il prouve souvent que plus un hôte possède de biens, plus il les décore de manière identique pour réduire les coûts de maintenance.

---

## 🎯 Conclusion pour le Décideur (Mairie)
Ces graphiques ne sont pas de simples statistiques : ils sont des **preuves de la transformation structurelle du quartier**. Ils permettent de justifier des régulations ciblées, comme le plafonnement des annonces par hôte ou l'interdiction des boîtes à clés en zone tendue.
