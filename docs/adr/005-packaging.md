# ADR 005 — Packaging Python de LogiAI

- **Statut :** accepté
- **Date :** 25 novembre 2026

## Décision

Le projet utilise des dépendances avec versions minimales (`>=`) dans `pyproject.toml`, tandis que `requirements.txt` conserve des versions figées (`==`) pour reproduire l'environnement de développement ou de déploiement.

Le choix `>=` facilite l'installation sur différentes plateformes et laisse pip sélectionner une version compatible récente. En contrepartie, une mise à jour future peut introduire une incompatibilité. Le choix `==` rend l'environnement plus reproductible, mais peut bloquer l'accès aux correctifs et nécessite une mise à jour manuelle régulière.

Le modèle entraîné reste à l'extérieur du package Python, dans `models/`. Le package contient le code réutilisable, tandis que les artefacts du modèle et les données sont fournis séparément. Cela évite d'alourdir la distribution et permet de remplacer le modèle sans reconstruire le package. En contrepartie, l'utilisateur doit fournir le dossier du modèle et configurer `LOGIAI_HOME`.
