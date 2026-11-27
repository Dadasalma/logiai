# Compte rendu : TP API LogiAI

**Noms :** SALMA AIT DADA  
**Groupe :** G3

## 1. Environnement et premiers tests

- **Sortie de `python -m pytest` au dÃ©part :** La sortie initiale n'a pas Ã©tÃ© conservÃ©e. AprÃ¨s finalisation du projet, l'exÃ©cution de `python -m pytest -q` donne :

```text
42 passed, 1 warning
```

- **Pourquoi certains tests qui attendent un 422 passent-ils dÃ©jÃ , alors que rien n'est Ã©crit ?**

FastAPI utilise automatiquement Pydantic pour valider les donnÃ©es reÃ§ues par l'API. Les champs obligatoires, les types et les contraintes dÃ©finies dans le schÃ©ma sont vÃ©rifiÃ©s automatiquement. Si les donnÃ©es ne respectent pas ces rÃ¨gles, FastAPI renvoie une erreur HTTP 422 sans qu'il soit nÃ©cessaire d'Ã©crire manuellement chaque contrÃ´le.

## 2. Mon schÃ©ma

Les bornes sont dÃ©finies selon les limites retenues pour notre scÃ©nario de livraison.

| Variable | Min | Max | Pourquoi |
|---|---:|---:|---|
| distance_km | 1 | 1000 | Une livraison doit parcourir au moins 1 km et la distance maximale retenue est de 1000 km. |
| poids_kg | 0.5 | 3000 | Le poids doit Ãªtre positif et respecter la capacitÃ© prÃ©vue pour les vÃ©hicules simulÃ©s. |
| heure_depart | 0 | 23 | L'heure de dÃ©part doit Ãªtre comprise entre 0 h et 23 h. |
| pluie_mm | 0 | 100 | Les prÃ©cipitations ne peuvent pas Ãªtre nÃ©gatives ; 100 mm reprÃ©sente une forte pluie dans notre scÃ©nario. |
| trafic_index | 0 | 10 | L'indice de trafic utilise une Ã©chelle comprise entre 0 et 10. |
| nb_arrets | 0 | 20 | Le nombre d'arrÃªts ne peut pas Ãªtre nÃ©gatif et la limite retenue est de 20. |

Le type de vÃ©hicule est Ã©galement contrÃ´lÃ© : seules les valeurs `moto`, `fourgon` et `camion` sont autorisÃ©es.

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

Cette fonction transforme les caractÃ©ristiques de la livraison en DataFrame, utilise le modÃ¨le entraÃ®nÃ© pour calculer la probabilitÃ© de retard, puis retourne le rÃ©sultat et l'alerte selon le seuil configurÃ©.

## 4. Quatre requÃªtes

| RequÃªte | Code obtenu | Pourquoi |
|---|---:|---|
| Livraison normale | 200 | Les donnÃ©es sont valides et la prÃ©diction est effectuÃ©e. |
| `distance_km = -5` | 422 | La distance est infÃ©rieure Ã  la borne minimale de 1 km. |
| `type_vehicule = "avion"` | 422 | Le type de vÃ©hicule n'appartient pas aux valeurs autorisÃ©es. |
| ModÃ¨le absent | 503 | Le service API fonctionne, mais le modÃ¨le nÃ©cessaire Ã  la prÃ©diction est indisponible. |

Le comportement du modÃ¨le absent est Ã©galement vÃ©rifiÃ© par le test automatisÃ© `test_modele_absent_renvoie_503`.

## 5. Questions de comprÃ©hension

**1. Pourquoi charge-t-on le modÃ¨le au dÃ©marrage et pas Ã  chaque requÃªte ?**

Pour Ã©viter de recharger le fichier du modÃ¨le Ã  chaque demande. Cela rÃ©duit le temps de traitement, Ã©conomise les ressources et amÃ©liore les performances de l'API.

**2. Qui Ã©crit le contrÃ´le Â« pluie <= 100 Â», et oÃ¹ est-il Ã©crit ?**

Le dÃ©veloppeur dÃ©finit cette rÃ¨gle dans `logiai/api/schemas.py`, avec Pydantic :

```python
pluie_mm: float = Field(ge=0, le=100)
```

FastAPI dÃ©clenche automatiquement la validation lorsqu'une requÃªte arrive.

**3. DiffÃ©rence entre 422 et 503 ?**

- HTTP 422 : les donnÃ©es envoyÃ©es par le client ne respectent pas les rÃ¨gles de validation.
- HTTP 503 : le service ne peut temporairement pas effectuer la prÃ©diction, par exemple parce que le modÃ¨le est indisponible.

**4. Pourquoi une route `/v1/predict` plutÃ´t que `/predict` ?**

`v1` signifie version 1 de l'API. La version permet de faire Ã©voluer l'API ultÃ©rieurement sans casser les applications qui utilisent l'ancienne version.

**5. Que se passerait-il si la distance Ã©tait dÃ©clarÃ©e `int` ?**

La distance serait reprÃ©sentÃ©e comme un nombre entier au lieu d'un nombre dÃ©cimal. On perdrait donc la possibilitÃ© de reprÃ©senter prÃ©cisÃ©ment des distances comme 12,5 km. Selon le mode de validation, une valeur dÃ©cimale pourrait Ãªtre convertie ou rejetÃ©e.

## 6. DÃ©cision : modÃ¨le absent

J'ai choisi de retourner une erreur HTTP 503 lorsque le modÃ¨le est absent.

Cette solution permet Ã  l'API de dÃ©marrer et de conserver l'accÃ¨s aux autres fonctionnalitÃ©s, comme `/health`. Seule la prÃ©diction devient indisponible.

L'autre possibilitÃ© serait de refuser le dÃ©marrage de l'API si le modÃ¨le est absent. Cela garantit qu'une API dÃ©marrÃ©e possÃ¨de toujours son modÃ¨le, mais empÃªche Ã©galement d'utiliser les autres endpoints.

J'ai choisi le 503 car il permet de signaler prÃ©cisÃ©ment l'indisponibilitÃ© du modÃ¨le sans arrÃªter complÃ¨tement le service.

## 7. Lien de la pull request

https://github.com/Dadasalma/logiai/pull/1

**Tests finaux :** 42 tests rÃ©ussis, aucune erreur.
