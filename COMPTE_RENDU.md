# Atelier 5 : Conteneuriser et déployer LogiAI avec Docker



## 1. Premier constat : ça ne marche que chez moi



| Ce que le projet suppose | Qui le garantit aujourd'hui |

|---|---|

| Python et bibliothèques compatibles avec model.joblib | moi, avec .venv et requirements.txt |

| Le fichier .env avec les deux clés | moi |

| Un modèle entraîné dans models/ | moi, avec python -m logiai.train |

| Deux terminaux (uvicorn + http.server 5500) | moi |



*\*Si je donne mon dossier à un camarade, il doit\*\* installer la bonne version de Python,

créer son .venv, recréer son .env, entraîner le modèle et lancer deux terminaux.



## 2. Dockerfile de l'API



```dockerfile

FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY pyproject.toml /tmp/build/

COPY logiai/ /tmp/build/logiai/

RUN pip install --no-cache-dir --no-deps /tmp/build \&\& rm -rf /tmp/build

COPY data/ ./data/

COPY models/ ./models/

ENV LOGIAI\_HOME=/app

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD \["uvicorn", "logiai.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

```



## 3. Dockerfile de la page web



```dockerfile

FROM nginx:alpine

COPY web/index.html /usr/share/nginx/html/index.html

COPY nginx/default.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

```



## 4. docker-compose.yml



```yaml

services:

&#x20; api:

&#x20;   build:

&#x20;     context: .

&#x20;     dockerfile: Dockerfile

&#x20;   container\_name: logiai-api

&#x20;   env\_file:

&#x20;     - .env

&#x20;   environment:

&#x20;     LOGIAI\_HOME: /app

&#x20;   ports:

&#x20;     - "8001:8000"

&#x20;   volumes:

&#x20;     - ./models:/app/models

&#x20;     - ./data:/app/data

&#x20;   healthcheck:

&#x20;     test:

&#x20;       - CMD

&#x20;       - python

&#x20;       - -c

&#x20;       - "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)"

&#x20;     interval: 30s

&#x20;     timeout: 5s

&#x20;     retries: 3

&#x20;     start\_period: 10s

&#x20;   restart: unless-stopped



&#x20; web:

&#x20;   build:

&#x20;     context: .

&#x20;     dockerfile: web/Dockerfile

&#x20;   container\_name: logiai-web

&#x20;   depends\_on:

&#x20;     api:

&#x20;       condition: service\_healthy

&#x20;   ports:

&#x20;     - "8080:80"

&#x20;   restart: unless-stopped

```



L'API utilise le fichier `.env` pour récupérer les clés, et les dossiers `models` et `data` sont montés en volumes. Le healthcheck vérifie que l'API répond sur le port 8000. Le service web attend que l'API soit healthy avant de démarrer.

## 5. Trois expériences (activité 1)



| # | Expérience | Prévu | Obtenu | Explication |

|---|---|---|---|---|

| 1 | Sans `--env-file` | 401 même avec la bonne clé | 401 | Le conteneur n'a pas les clés : .env est exclu de l'image et Docker ne le lit pas tout seul. |

| 2 | Sans `-p 8001:8000` | Conteneur Up mais curl échoue | `Failed to connect to localhost:8001` (port 8000/tcp non publié) | EXPOSE documente seulement ; il faut publier avec -p hôte:conteneur. |

| 3 | uvicorn sur 127.0.0.1 | Échec malgré le port publié | `curl: (52) Empty reply from server` | uvicorn n'accepte que les connexions internes au conteneur ; il faut 0.0.0.0. |



## 6. Codes de l'étape 5 (via Nginx, port 8080)



| Requête | Code |

|---|---|

| /api/health | 200 |

| /api/v1/predict sans clé | 401 |

| /api/v1/predict fausse clé | 401 |

| /api/v1/predict bonne clé | 200 (probabilité 0.3658, alerte false, seuil 0.4) |



## 7. Étape 6 : F12 / Network



La requête part vers `http://localhost:8080/api/v1/predict` (même origine que la page).

Une seule ligne `predict` (200, fetch, 13 ms), \*\*pas de requête OPTIONS\*\* : même origine,

donc pas de CORS ni de requête préliminaire.



## 8. Étape 8 : API arrêtée



`docker compose stop api` → `/api/health` renvoie \*\*502 Bad Gateway\*\* (HTML de Nginx).

La page affiche : `Unexpected token '<', "<html>... is not valid JSON"`, car le JavaScript

essaie de lire du HTML comme du JSON. Après `docker compose start api`, l'API

redevient healthy et la page refonctionne.



## 9. docker stats



| Conteneur | CPU | Mémoire | Réseau (I/O) | PIDS |

|---|---|---|---|---|

| logiai-api | 0.16 % | 142 MiB | 12.5 kB / 7.17 kB | 21 |

| logiai-web | 0.00 % | 9 MiB | 24.1 kB / 33.3 kB | 9 |



## 10. Cinq questions de compréhension



1\. \*\*Image vs conteneur ?\*\* Une image est un modèle figé en lecture seule ; un conteneur est une instance en exécution de cette image, avec une fine couche inscriptible éphémère.

2\. \*\*Pourquoi /api/v1/predict et pas api:8000 dans la page ?\*\* Le nom `api` n'existe que dans le réseau Docker, pas sur Windows ; le chemin relatif part vers le même hôte et le même port que la page, et Nginx relaie.

3\. \*\*Pourquoi depends\_on seul ne suffit pas ?\*\* Il garantit l'ordre de démarrage, pas que l'API soit prête. `condition: service\_healthy` attend que le healthcheck réussisse.

4\. \*\*Pourquoi le healthcheck utilise 127.0.0.1:8000 ?\*\* Le healthcheck s'exécute à l'intérieur du conteneur API. `127.0.0.1` désigne donc ce conteneur lui-même. L'API écoute sur `0.0.0.0:8000`, ce qui inclut son interface locale, et `/health` est accessible sans clé API.



5\. \*\*Pourquoi un nouveau model.joblib est vu sans rebuild ?\*\* Grâce au bind mount `./models:/app/models`, le conteneur utilise directement le dossier `models` de la machine hôte. Le nouveau modèle est donc visible sans reconstruire l'image. Cependant, l'API doit être redémarrée pour recharger le modèle. En revanche, le code du dossier `logiai/` est intégré dans l'image : ses modifications nécessitent un rebuild.

&#x20;

## 11. Lien de la pull request

[Pull request #3](https://github.com/Dadasalma/logiai/pull/3)