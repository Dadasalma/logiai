# Compte rendu — Atelier 6 : Packaging Python de LogiAI

## Étape 1 — Distribution du package

Un collègue peut installer LogiAI avec `pip install logiai` si le package est publié sur un index, ou installer le fichier wheel fourni. Il doit également récupérer les dossiers `models/` et `data/`, puis définir `LOGIAI_HOME` vers le répertoire qui les contient. Le modèle n'est pas embarqué dans le package Python.

## Étape 2 — Configuration du package

Le fichier `pyproject.toml` déclare les métadonnées, les dépendances, les dépendances optionnelles `api` et `dev`, ainsi que la commande `logiai-predict`.

## Étape 3 — Construction et installation

La construction a produit :
- `dist/logiai-0.1.0-py3-none-any.whl`
- `dist/logiai-0.1.0.tar.gz`

Le wheel a été installé dans un environnement virtuel indépendant. L'import `logiai` pointe vers `site-packages/logiai/__init__.py`.

## Étape 4 — Test avec 500 mm

**À compléter :** le test spécifique avec `pluie_mm = 500` n'a pas été exécuté ou son résultat n'a pas été conservé dans les éléments disponibles. Ne pas inventer la prédiction : exécuter le scénario demandé et reporter la sortie réelle.

## Étape 5 — Exécution avec et sans `LOGIAI_HOME`

Le wheel ne contient pas le modèle. Le premier essai sans `LOGIAI_HOME` doit donc être exécuté et sa sortie exacte ajoutée ici.

Le second essai a été réalisé après configuration de `LOGIAI_HOME` vers `C:\dev\logiai`. La commande :

```powershell
logiai-predict livraison_test.json
```

a retourné :

```text
Probabilité de retard : 37 % (OK)
```

Le fichier JSON de test contient notamment `distance_km = 13.6`, `poids_kg = 1253.8`, `heure_depart = 12`, `pluie_mm = 0.0`, `trafic_index = 3.1`, `nb_arrets = 6` et `type_vehicule = camion`.

## Étape 6 — Intégration Docker

**Non validée dans le checkout actuel.** Aucun `Dockerfile` ni fichier `compose` n'est présent dans `C:\dev\logiai`. Il reste à intégrer l'installation du package dans le Dockerfile, lancer `docker compose up -d --build`, puis vérifier le chemin avec :

```powershell
docker compose exec api python -c "import logiai; print(logiai.__file__)"
```

Le chemin attendu doit pointer vers `site-packages/logiai`, et non vers une copie du package dans `/app`.

## Tests automatisés

Commande exécutée :

```powershell
python -m pytest -v
```

Résultat :

```text
44 passed, 1 warning
```

L'avertissement est une dépréciation liée à Starlette/httpx ; les tests sont passés.
