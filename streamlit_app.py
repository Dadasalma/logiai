
import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000/v1/predict"

st.title("LogiAI : risque de retard")
st.write("Évaluez le risque de retard d'une livraison.")

gauche, droite = st.columns(2)

with gauche:
    distance = st.slider("Distance (km)", 1, 800, 120)
    poids = st.slider("Poids (kg)", 0, 3000, 450)
    heure = st.slider("Heure de départ", 0, 23, 17)
    vehicule = st.selectbox(
        "Type de véhicule",
        ["moto", "fourgon", "camion"],
        index=2
    )

with droite:
    pluie = st.slider("Pluie (mm)", 0.0, 60.0, 8.0)
    trafic = st.slider("Trafic (0 à 10)", 0.0, 10.0, 7.5)
    arrets = st.slider("Nombre d'arrêts", 0, 12, 4)

if st.button("Évaluer le risque"):
    livraison = {
        "distance_km": distance,
        "poids_kg": poids,
        "heure_depart": heure,
        "pluie_mm": pluie,
        "trafic_index": trafic,
        "nb_arrets": arrets,
        "type_vehicule": vehicule,
    }

    try:
        reponse = requests.post(
            API_URL,
            json=livraison,
            timeout=5
        )
    except requests.ConnectionError:
        st.error(
            "API injoignable : lancez le serveur FastAPI "
            "dans un autre terminal."
        )
    except requests.Timeout:
        st.error("L'API met trop de temps à répondre.")
    else:
        if reponse.status_code == 200:
            resultat = reponse.json()

            st.metric(
                "Probabilité de retard",
                f"{resultat['probabilite_retard']:.1%}"
            )

            if resultat["alerte"]:
                st.warning("Alerte : livraison à risque.")
            else:
                st.success("Livraison probablement à l'heure.")
        else:
            st.error(f"Erreur HTTP {reponse.status_code}")
            st.json(reponse.json())
