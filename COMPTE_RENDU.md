# Compte rendu : TP API LogiAI

**Noms :** MOUSSAID HAMZA  
**Groupe :** G3

## 1. Environnement et premiers tests

- **Sortie de `python -m pytest` au départ :** La sortie initiale n'a pas été conservée. Après finalisation du projet, l'exécution de `python -m pytest -q` donne :

```text
42 passed, 1 warning
```

- **Pourquoi certains tests qui attendent un 422 passent-ils déjà, alors que rien n'est écrit ?**

FastAPI utilise automatiquement Pydantic pour valider les données reçues par l'API. Les champs obligatoires, les types et les contraintes définies dans le schéma sont vérifiés automatiquement. Si les données ne respectent pas ces règles, FastAPI renvoie une erreur HTTP 422 sans qu'il soit nécessaire d'écrire manuellement chaque contrôle.

## 2. Mon schéma

Les bornes sont définies selon les limites retenues pour notre scénario de livraison.

| Variable | Min | Max | Pourquoi |
|---|---:|---:|---|
| distance_km | 1 | 1000 | Une livraison doit parcourir au moins 1 km et la distance maximale retenue est de 1000 km. |
| poids_kg | 0.5 | 3000 | Le poids doit être positif et respecter la capacité prévue pour les véhicules simulés. |
| heure_depart | 0 | 23 | L'heure de départ doit être comprise entre 0 h et 23 h. |
| pluie_mm | 0 | 100 | Les précipitations ne peuvent pas être négatives ; 100 mm représente une forte pluie dans notre scénario. |
| trafic_index | 0 | 10 | L'indice de trafic utilise une échelle comprise entre 0 et 10. |
| nb_arrets | 0 | 20 | Le nombre d'arrêts ne peut pas être négatif et la limite retenue est de 20. |

Le type de véhicule est également contrôlé : seules les valeurs `moto`, `fourgon` et `camion` sont autorisées.

## 3. Ma fonction predict()

```python
def predict(self, features: dict) -> dict:
    """features : un dictionnaire avec les 7 variables du contrat."""
    df = pd.DataFrame([features], columns=FEATURES)
    proba = float(self.model.predict_proba(df)[0, 1])

    return {
        "probabilite_retard": round(proba, 4),
        "alerte": proba >= self.threshold,
        "seuil": self.threshold,
        "model_version": self.version,
    }
```

Cette fonction transforme les caractéristiques de la livraison en DataFrame, utilise le modèle entraîné pour calculer la probabilité de retard, puis retourne le résultat et l'alerte selon le seuil configuré.

## 4. Quatre requêtes

| Requête | Code obtenu | Pourquoi |
|---|---:|---|
| Livraison normale | 200 | Les données sont valides et la prédiction est effectuée. |
| `distance_km = -5` | 422 | La distance est inférieure à la borne minimale de 1 km. |
| `type_vehicule = "avion"` | 422 | Le type de véhicule n'appartient pas aux valeurs autorisées. |
| Modèle absent | 503 | Le service API fonctionne, mais le modèle nécessaire à la prédiction est indisponible. |

Le comportement du modèle absent est également vérifié par le test automatisé `test_modele_absent_renvoie_503`.

## 5. Questions de compréhension

**1. Pourquoi charge-t-on le modèle au démarrage et pas à chaque requête ?**

Pour éviter de recharger le fichier du modèle à chaque demande. Cela réduit le temps de traitement, économise les ressources et améliore les performances de l'API.

**2. Qui écrit le contrôle « pluie <= 100 », et où est-il écrit ?**

Le développeur définit cette règle dans `logiai/api/schemas.py`, avec Pydantic :

```python
pluie_mm: float = Field(ge=0, le=100)
```

FastAPI déclenche automatiquement la validation lorsqu'une requête arrive.

**3. Différence entre 422 et 503 ?**

- HTTP 422 : les données envoyées par le client ne respectent pas les règles de validation.
- HTTP 503 : le service ne peut temporairement pas effectuer la prédiction, par exemple parce que le modèle est indisponible.

**4. Pourquoi une route `/v1/predict` plutôt que `/predict` ?**

`v1` signifie version 1 de l'API. La version permet de faire évoluer l'API ultérieurement sans casser les applications qui utilisent l'ancienne version.

**5. Que se passerait-il si la distance était déclarée `int` ?**

La distance serait représentée comme un nombre entier au lieu d'un nombre décimal. On perdrait donc la possibilité de représenter précisément des distances comme 12,5 km. Selon le mode de validation, une valeur décimale pourrait être convertie ou rejetée.

## 6. Décision : modèle absent

J'ai choisi de retourner une erreur HTTP 503 lorsque le modèle est absent.

Cette solution permet à l'API de démarrer et de conserver l'accès aux autres fonctionnalités, comme `/health`. Seule la prédiction devient indisponible.

L'autre possibilité serait de refuser le démarrage de l'API si le modèle est absent. Cela garantit qu'une API démarrée possède toujours son modèle, mais empêche également d'utiliser les autres endpoints.

J'ai choisi le 503 car il permet de signaler précisément l'indisponibilité du modèle sans arrêter complètement le service.

## 7. Lien de la pull request

https://github.com/Dadasalma/logiai/pull/1

**Tests finaux :** 42 tests réussis, aucune erreur.