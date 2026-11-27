\# ADR 004 : Docker, modèle et ports



\## Contexte

LogiAI tourne dans deux conteneurs (api FastAPI, web Nginx) lancés par Docker Compose.

Deux choix à faire : où vit le modèle, et quels ports sont publiés.



\## Décision 1 : le modèle est monté en volume

`./models:/app/models` (bind mount), en plus du COPY du Dockerfile.



\*\*Ce que l'autre option ferait perdre (COPY seul) :\*\* à chaque réentraînement

(`python -m logiai.train`), il faudrait reconstruire l'image

(`docker compose up -d --build`) pour que le conteneur voie le nouveau

`model.joblib`. Le modèle et le code seraient liés dans la même image.



\*\*Limite :\*\* l'API charge le modèle au démarrage, donc il faut

`docker compose restart api` après un réentraînement.



\## Décision 2 : ports publiés

Seul 8080 (Nginx) devrait être publié. 8001 est gardé pour l'atelier

(tests directs, /docs).



\*\*Ce que l'autre option ferait perdre (8080 + 8001) :\*\* un visiteur peut

contourner Nginx et joindre directement l'API sur 8001 : il voit /docs

(Swagger) et /health, et peut attaquer /v1/predict (essai de clés)

sans passer par le reverse proxy. Publier seulement 8080 réduit la

surface d'attaque ; l'API devient joignable uniquement via le réseau

Docker.



\*\*Ce que 8080 seul ferait perdre :\*\* l'accès direct à /docs et aux tests

curl sur 8001, pratique pour le débogage.



\## Conséquences

\- Réentraîner = copier le modèle, puis `restart api`, sans rebuild.

\- En production : retirer `8001:8000` du compose.

\- La clé API reste obligatoire : Nginx relaie, il ne protège pas.

