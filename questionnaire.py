# ---------------------------
# 📦 Connexion à Supabase
# ---------------------------

from supabase import create_client, Client
import streamlit as st
import pandas as pd
from datetime import datetime

# Remplace ces deux variables par les tiennes (dans .streamlit/secrets.toml ou Settings)
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------------------
# ✅ Fonctions Supabase
# ---------------------------

def save_response(data):
    try:
        response = supabase.table("questionnaire").insert({
            "nom": data["Nom"],
            "club": data["Club"],
            "date": data["Date"],
            "intensite": data["Intensité"],
            "sommeil": data["Sommeil"],
            "fatigue": data["Fatigue"],
            "stress": data["Stress"],
            "dynamisme": data["Dynamisme"],
            "douleurs": data["Douleurs"],
            "description_douleurs": data["Description des douleurs"]
        }).execute()
        return True, ""
    except Exception as e:
        return False, str(e)

def load_responses(nom=None, club=None, date=None):
    try:
        query = supabase.table("questionnaire").select("*")
        if nom:
            query = query.eq("nom", nom)
        if club:
            query = query.eq("club", club)
        if date:
            query = query.eq("date", date)
        response = query.execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Erreur chargement données : {e}")
        return pd.DataFrame()

def get_preferences(nom):
    try:
        res = supabase.table("preferences").select("*").eq("nom", nom).execute()
        if res.data:
            return res.data[0]
        else:
            return {
                "show_seance": True,
                "show_weekly_intensity": True,
                "show_weekly_parameter": True,
                "show_weekly_score_bien": True,
                "show_weekly_comp": True,
                "show_monthly_intensity": True,
                "show_monthly_parameter": True,
                "show_monthly_score_bien": True,
                "show_monthly_comp": True,
                "show_monthly_zscore": True,
                "show_global_intensity": True,
                "show_global_parameter": True,
                "show_global_score_bien": True,
                "show_global_zscore": True,
                "show_seance_coach": True,
                "show_weekly_intensity_coach": True,
                "show_weekly_parameter_coach": True,
                "show_weekly_score_bien_coach": True,
                "show_weekly_comp_coach": True,
                "show_monthly_intensity_coach": True,
                "show_monthly_parameter_coach": True,
                "show_monthly_score_bien_coach": True,
                "show_monthly_comp_coach": True,
                "show_monthly_zscore_coach": True,
                "show_global_intensity_coach": True,
                "show_global_parameter_coach": True,
                "show_global_score_bien_coach": True,
                "show_global_zscore_coach": True,
                "show_team_intensity_coach": True,
                "show_cadran": True,
                "show_team_bien_etre_coach": True,
                "show_team_douleurs_coach": True,
                "show_team_synthèse_intensity_coach": True,
                "show_cadran_synthèse": True,
                "show_team_synthèse_bien_etre_coach": True,
                "show_seance_team_coach": True
            }
    except Exception as e:
        st.error(f"Erreur chargement préférences : {e}")
        return {}

def save_preferences(nom, prefs):
    try:
        existing = supabase.table("preferences").select("*").eq("nom", nom).execute().data
        data = {"nom": nom, **prefs}
        if existing:
            supabase.table("preferences").update(data).eq("nom", nom).execute()
        else:
            supabase.table("preferences").insert(data).execute()
        return True, ""
    except Exception as e:
        return False, str(e)

def get_mode_questionnaire(nom):
    try:
        res = supabase.table("frequence").select("*").eq("nom", nom).execute()
        if res.data:
            return res.data[0].get("mode_questionnaire", "Tous les jours")
        return "Tous les jours"
    except Exception as e:
        st.error(f"Erreur lecture mode_questionnaire : {e}")
        return "Tous les jours"

def save_mode_questionnaire(nom, mode):
    try:
        existing = supabase.table("frequence").select("*").eq("nom", nom).execute().data
        data = {"nom": nom, "mode_questionnaire": mode}
        if existing:
            supabase.table("frequence").update(data).eq("nom", nom).execute()
        else:
            supabase.table("frequence").insert(data).execute()
        return True, ""
    except Exception as e:
        return False, str(e)
