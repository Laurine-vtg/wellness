import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime, timedelta
import os

# Configuration de la page
st.set_page_config(page_title="Connexion", layout="wide")

# Connexion à Supabase
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    st.success("✅ Connexion à Supabase réussie")
except Exception as e:
    st.error(f"❌ Erreur de connexion à Supabase : {e}")
    st.stop()

# Chargement du fichier ID.csv pour savoir qui est coach ou joueur
@st.cache_data
def load_ids():
    try:
        df = pd.read_csv("ID.csv")
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement de ID.csv : {e}")
        return pd.DataFrame()

df_ids = load_ids()

# Interface de connexion
with st.form("login_form"):
    nom_utilisateur = st.text_input("Entrez votre nom")
    submit_button = st.form_submit_button("Connexion")

if submit_button:
    if nom_utilisateur in df_ids["Nom"].values:
        st.session_state["nom"] = nom_utilisateur
        role = df_ids[df_ids["Nom"] == nom_utilisateur]["Role"].values[0]
        st.session_state["role"] = role
        st.success(f"Bienvenue {nom_utilisateur} ({role}) 👋")
    else:
        st.error("❌ Nom non reconnu. Vérifiez l'orthographe ou contactez votre coach.")

# Debug visible
if "nom" in st.session_state:
    st.write("Utilisateur connecté :", st.session_state["nom"])
    st.write("Rôle :", st.session_state["role"])
else:
    st.info("Veuillez vous connecter ci-dessus.")
