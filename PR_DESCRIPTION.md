## Description

Cette PR finalise le packaging de LogiAI et son intégration avec Docker Compose.

## Modifications
- Configuration du package avec `pyproject.toml`.
- Ajout de la commande CLI `logiai-predict`.
- Gestion des chemins des données et du modèle via `LOGIAI_HOME`.
- Construction et installation du wheel dans un environnement indépendant.
- Ajout des fichiers Docker et de la configuration Docker Compose.
- Installation du package LogiAI dans l'image API sans copier le code source dans `/app`.
- Documentation de conception et ADR du packaging.

## Vérifications
- `python -m pytest -v` : 44 passed, 1 warning.
- Construction du wheel et du sdist réussie.
- Installation du wheel dans un environnement indépendant.
- Prédiction CLI validée avec `LOGIAI_HOME`.
- Test avec `pluie_mm = 500` : alerte déclenchée.
- Import Docker vérifié depuis `site-packages`.
- Données et modèle présents dans `/app`.
- API et interface web testées avec Docker Compose.
