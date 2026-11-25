
import argparse
import json
import sys
from pathlib import Path

from logiai.predict import Predictor


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="logiai-predict")
    parser.add_argument("fichier", help="fichier JSON d'une livraison")
    args = parser.parse_args(argv)

    chemin = Path(args.fichier)

    if not chemin.exists():
        print(f"Fichier introuvable : {chemin}", file=sys.stderr)
        return 1

    livraison = json.loads(chemin.read_text(encoding="utf-8"))

    resultat = Predictor().predict(livraison)

    pourcentage = round(resultat["probabilite_retard"] * 100)
    statut = "ALERTE" if resultat["alerte"] else "OK"

    print(f"Probabilité de retard : {pourcentage} % ({statut})")

    return 0


if __name__ == "__main__":
    sys.exit(main())
