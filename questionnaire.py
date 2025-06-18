# Importer les outils utilisés
import streamlit as st
from PIL import Image
from datetime import datetime, timedelta
import pandas as pd
import os
import plotly.graph_objects as go
import plotly.express as px
import locale
import streamlit.components.v1 as components
import numpy as np
import json

# Google Sheets
import gspread
from google.oauth2.service_account import Credentials

# Pour l'accès Google Sheets & Drive
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Charger les credentials depuis la variable d'environnement secrète (Streamlit Secrets)
service_account_info = json.loads(os.getenv("GOOGLE_CREDENTIALS_JSON"))

creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
client = gspread.authorize(creds)
spreadsheet = client.open("wellness_data")  # nom du Google Sheet
sheet_questionnaire = spreadsheet.worksheet("questionnaire")
sheet_preferences = spreadsheet.worksheet("preferences")

# Fonction pour enregistrer réponse au questionnaire

def save_response(data):
    try:
        values = [
            data["Nom"],
            data["Club"],
            data["Date"],
            data["Intensité"],
            data["Sommeil"],
            data["Fatigue"],
            data["Stress"],
            data["Dynamisme"],
            data["Douleurs"],
            data["Description des douleurs"]
        ]
        sheet_questionnaire.append_row(values)
        return True, ""
    except Exception as e:
        return False, str(e)

# Fonction pour récupérer réponses avec filtres optionnels
def load_responses(nom=None, club=None, date=None):
    try:
        records = sheet_questionnaire.get_all_records()
        df = pd.DataFrame(records)

        if nom:
            df = df[df["Nom"] == nom]
        if club:
            df = df[df["Club"] == club]
        if date:
            df = df[df["Date"] == date]

        return df
    except Exception as e:
      pass
      return pd.DataFrame()


# Fonction pour charger les utilisateurs depuis CSV

def load_users_from_csv(path="ID.csv"):
    df = pd.read_csv(path, sep=";")
    users_dict = {
        row["username"]: {
            "password": row["password"],
            "role": row["role"],
            "club": row["club"]
        }
        for _, row in df.iterrows()
    }
    return users_dict

USERS = load_users_from_csv()

def supprimer_reponse(nom, date):
    try:
        sheet = spreadsheet.worksheet("questionnaire")

        data = sheet.get_all_values()
        headers = data[0]

        try:
            col_nom = headers.index("Nom")
            col_date = headers.index("Date")
        except ValueError as e:
            return False, f"Colonne introuvable : {str(e)}"

        row_to_delete = None
        for i, row in enumerate(data[1:], start=2):
            if len(row) > max(col_nom, col_date):
                if row[col_nom] == nom and row[col_date] == date:
                    row_to_delete = i
                    break

        if row_to_delete:
            sheet.delete_rows(row_to_delete)
            return True, ""
        else:
            return False, "Réponse non trouvée"

    except Exception as e:
        return False, str(e)

# Fonction pour récupérer les préférences utilisateur
def get_preferences(nom):
    try:
        records = sheet_preferences.get_all_records()
        for row in records:
            if row["Nom"] == nom:
                return row
        # Valeurs par défaut
        return {
            "mode_questionnaire": "Tous les jours",
            "show_seance": 1,
            "show_weekly_intensity": 1,
            "show_weekly_parameter": 1,
            "show_weekly_score_bien": 1,
            "show_weekly_comp": 1,
            "show_monthly_intensity": 1,
            "show_monthly_parameter": 1,
            "show_monthly_score_bien": 1,
            "show_monthly_comp": 1,
            "show_monthly_zscore":1,
            "show_global_intensity":1,
            "show_global_parameter":1,
            "show_global_score_bien":1,
            "show_global_zscore":1,
            "show_seance_coach": 1,
            "show_weekly_intensity_coach": 1,
            "show_weekly_parameter_coach": 1,
            "show_weekly_score_bien_coach": 1,
            "show_weekly_comp_coach": 1,
            "show_monthly_intensity_coach": 1,
            "show_monthly_parameter_coach": 1,
            "show_monthly_score_bien_coach": 1,
            "show_monthly_comp_coach": 1,
            "show_monthly_zscore_coach":1,
            "show_global_intensity_coach":1,
            "show_global_parameter_coach":1,
            "show_global_score_bien_coach":1,
            "show_global_zscore_coach":1,
            "show_team_intensity_coach":1,
            "show_cadran": 1,
            "show_team_bien_etre_coach":1,
            "show_team_douleurs_coach":1,
            "show_team_synthèse_intensity_coach": 1,
            "show_cadran_synthèse":1,
            "show_team_synthèse_bien_etre_coach":1,
            "show_seance_team_coach":1
        }
    except:
        return {}

# Fonction pour sauvegarder les préférences utilisateur
def save_preferences(nom, prefs):
    try:
        records = sheet_preferences.get_all_records()
        noms = [r["Nom"] for r in records]
        data = [nom] + list(prefs.values())
        headers = sheet_preferences.row_values(1)
        if nom in noms:
            index = noms.index(nom) + 2
            sheet_preferences.update(f"A{index}:{chr(64+len(headers))}{index}", [data])
        else:
            sheet_preferences.append_row(data)
        return True, ""
    except Exception as e:
        return False, str(e)
    
def save_preferences_2(nom, mode_questionnaire):
    try:
        # Ouvrir la feuille 'preferences'
        sheet = spreadsheet.worksheet("preferences")

        # Récupérer toutes les données
        data = sheet.get_all_values()

        # Trouver l’index des colonnes 'Nom' et 'mode_questionnaire'
        headers = data[0]
        try:
            col_nom = headers.index("Nom")
        except ValueError:
            return False, "Colonne 'Nom' introuvable"
        try:
            col_mode = headers.index("mode_questionnaire")
        except ValueError:
            return False, "Colonne 'mode_questionnaire' introuvable"

        # Chercher la ligne où 'Nom' correspond
        row_to_update = None
        for i, row in enumerate(data[1:], start=2):
            if len(row) > col_nom and row[col_nom] == nom:
                row_to_update = i
                break

        if row_to_update:
            # Mettre à jour la cellule
            sheet.update_cell(row_to_update, col_mode + 1, mode_questionnaire)
        else:
            # Ajouter une nouvelle ligne
            new_row = [""] * len(headers)
            new_row[col_nom] = nom
            new_row[col_mode] = mode_questionnaire
            sheet.append_row(new_row)

        return True, ""
    except Exception as e:
        return False, str(e)


# Fonction pour déterminer les couleurs d'arrière-plan

def couleur_plotly(valeur, variable):
    vert = 'background-color: rgba(15, 154, 75, 0.5)'
    jaune = 'background-color: rgba(249, 206, 105, 0.5)'
    rouge = 'background-color: rgba(215, 72, 47, 0.5)'

    if variable in ["Fatigue", "Stress"]:
        if valeur < 4:
            return vert
        elif valeur < 7:
            return jaune
        else:
            return rouge
    elif variable in ["Sommeil", "Dynamisme"]:
        if valeur < 4:
            return rouge
        elif valeur < 7:
            return jaune
        else:
            return vert
    return ""

# Fonction pour appliquer un style aux tableaux

def style_moyennes(df):
    styles = []
    for index, row in df.iterrows():
        style = couleur_plotly(row["Moyenne"], index)
        styles.append([style])
    return pd.DataFrame(styles, index=df.index, columns=["Moyenne"])

# Fonction pour voir les joueurs du club

def load_club_players(club):
    df_id = pd.read_csv("ID.csv", sep=";")
    df_id["club"] = df_id["club"].astype(str).str.strip().str.lower()
    df_id["role"] = df_id["role"].astype(str).str.strip().str.lower()
    club = club.lower().strip()
    df_club_players = df_id[(df_id["club"] == club) & (df_id["role"] == "player")]
    return df_club_players["username"].dropna().unique().tolist()

# Associer coach à un club
def get_coach_for_club(club_name):
    df_ids = pd.read_csv("ID.csv", sep=";")
    df_ids["club"] = df_ids["club"].astype(str).str.strip().str.lower()
    df_ids["role"] = df_ids["role"].astype(str).str.strip().str.lower()

    club_name = club_name.strip().lower()
    coach_row = df_ids[(df_ids["club"] == club_name) & (df_ids["role"] == "coach")]

    if not coach_row.empty:
        return coach_row.iloc[0]["username"]
    return None

# Droits d'accès\
ACCESS_RIGHTS = {
    "coach": [
        "Compte rendu collectif",
        "Compte rendu individuel (coach)",
        "Informations",
        "Réglages", 
        "Données brutes"
    ],
    "player": [
        "Questionnaire de suivi",
        "Compte rendu individuel (joueur)",
        "Réglages"
    ]
}

# Dictionnaire graphique cadran
cadran_colors = {
    ("Dynamisme", "Fatigue"): {
        "bottom_left": "rgba(249, 206, 105, 0.15)",  # jaune
        "bottom_right": "rgba(15, 154, 75, 0.15)",  # vert
        "top_left": "rgba(215, 72, 47, 0.15)",      # rouge
        "top_right": "rgba(249, 206, 105, 0.15)",     # jaune
    },
    ("Dynamisme", "Sommeil"): {
        "bottom_left": "rgba(215, 72, 47, 0.15)",
        "bottom_right": "rgba(249, 206, 105, 0.15)",
        "top_left": "rgba(249, 206, 105, 0.15)",
        "top_right": "rgba(15, 154, 75, 0.15)",
    },
    ("Dynamisme", "Stress"): {
        "bottom_left": "rgba(249, 206, 105, 0.15)",  # jaune
        "bottom_right": "rgba(15, 154, 75, 0.15)",  # vert
        "top_left": "rgba(215, 72, 47, 0.15)",      # rouge
        "top_right": "rgba(249, 206, 105, 0.15)",     # jaune   
    },
    ("Fatigue", "Dynamisme"): {
        "bottom_left": "rgba(249, 206, 105, 0.15)",
        "bottom_right": "rgba(215, 72, 47, 0.15)",
        "top_left": "rgba(15, 154, 75, 0.15)",
        "top_right": "rgba(249, 206, 105, 0.15)",
    },
    ("Fatigue", "Sommeil"): {
        "bottom_left": "rgba(249, 206, 105, 0.15)",
        "bottom_right": "rgba(215, 72, 47, 0.15)",
        "top_left": "rgba(15, 154, 75, 0.15)",
        "top_right": "rgba(249, 206, 105, 0.15)",
    },
    ("Fatigue", "Stress"): {
        "bottom_left": "rgba(15, 154, 75, 0.15)",
        "bottom_right": "rgba(249, 206, 105, 0.15)",
        "top_left": "rgba(249, 206, 105, 0.15)",
        "top_right": "rgba(215, 72, 47, 0.15)",
    },
    ("Sommeil", "Dynamisme"): {
        "bottom_left": "rgba(215, 72, 47, 0.15)",
        "bottom_right": "rgba(249, 206, 105, 0.15)",
        "top_left": "rgba(249, 206, 105, 0.15)",
        "top_right": "rgba(15, 154, 75, 0.15)",
    },
    ("Sommeil", "Fatigue"): {
        "bottom_left": "rgba(249, 206, 105, 0.15)",
        "bottom_right": "rgba(15, 154, 75, 0.15)",
        "top_left": "rgba(215, 72, 47, 0.15)",
        "top_right": "rgba(249, 206, 105, 0.15)",
    },
    ("Sommeil", "Stress"): {
        "bottom_left": "rgba(249, 206, 105, 0.15)",
        "bottom_right": "rgba(15, 154, 75, 0.15)",
        "top_left": "rgba(215, 72, 47, 0.15)",
        "top_right": "rgba(249, 206, 105, 0.15)",
    },
    ("Stress", "Dynamisme"): {
        "bottom_left": "rgba(249, 206, 105, 0.15)",
        "bottom_right": "rgba(215, 72, 47, 0.15)",
        "top_left": "rgba(15, 154, 75, 0.15)",
        "top_right": "rgba(249, 206, 105, 0.15)",
    },
    ("Stress", "Fatigue"): {
        "bottom_left": "rgba(15, 154, 75, 0.15)",
        "bottom_right": "rgba(249, 206, 105, 0.15)",
        "top_left": "rgba(249, 206, 105, 0.15)",
        "top_right": "rgba(215, 72, 47, 0.15)",
    },
    ("Stress", "Sommeil"): {
        "bottom_left": "rgba(249, 206, 105, 0.15)",
        "bottom_right": "rgba(215, 72, 47, 0.15)",
        "top_left": "rgba(15, 154, 75, 0.15)",
        "top_right": "rgba(249, 206, 105, 0.15)",
    },
}

# ===================================================== Page de connexion =====================================================

# Fonction pour créer un formulaire de connexion (titre, sélection du club, saisie de ID, bouton se connecter, afficher logo)
def login():
    st.title("🔐Connexion requise")
    
    clubs_disponibles = list(set(user["club"] for user in USERS.values()))
    club = st.selectbox("🏟️Sélectionnes ton équipe", clubs_disponibles)

    username = st.text_input("👤Identifiant")
    password = st.text_input("🔒Mot de passe", type="password")

    if st.button("Se connecter"):
        if not username.strip() or not password.strip():
            st.error("❌Merci de remplir identifiant et mot de passe.")
        elif username in USERS:
            user = USERS[username]
            if password == user["password"] and club == user["club"]:
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.session_state["role"] = user["role"]
                st.session_state["club"] = user["club"]
                st.success("✅Connexion réussie ! Recliques sur le bouton 'Se connecter' pour accéder à l'application.")
            else:
                st.error("❌Mot de passe ou équipe incorrect")
        else:
            st.error("❌Identifiant incorrect")

    # Affichage du logo
    col1, col2 = st.columns([2, 1])
    with col2:
        logo = Image.open("logo.jpg")
        st.image(logo, width=250)

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login()
    st.stop()  

# =================================================== Début de l'application ===================================================
st.title("📋SUIVI WELLNESS")

# Filtrer les pages accessibles.
role = st.session_state.get("role", "")
club = st.session_state.get("club", "")
allowed_pages = ACCESS_RIGHTS.get(role, [])

# Recupérer les paramètres présents dans l'URL.
query_params = st.query_params

# Déterminer la page à afficher par défaut.
default_page_list = query_params.get("page")
if default_page_list and default_page_list[0] in allowed_pages:
    default_page = default_page_list[0]
else:
    default_page = allowed_pages[0] if allowed_pages else "Questionnaire de suivi"

# Sidebar pour pouvoir changer de page.
selected_page = st.sidebar.radio("Navigation", allowed_pages, index=allowed_pages.index(default_page))

# Bouton de déconnexion.
if st.sidebar.button("Déconnexion"):
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""
    st.query_params = {}
    st.rerun()

# Recharger l'application pour changer de page.
if selected_page != default_page:
    st.query_params = {"page": [selected_page]}
    st.rerun()
page = selected_page

# ======================================================== Page questionnaire =======================================================
# Sélectionner le nom automatiquement, choisir la date, slider pour répondre aux questions et envoyer réponses.
if page == "Questionnaire de suivi":
    st.title("Questionnaire de suivi")
    club = st.session_state.get("club", "")  # le club du joueur
    coach_nom = get_coach_for_club(club)

    if coach_nom:
     prefs = get_preferences(coach_nom)
     mode = prefs.get("mode_questionnaire", "Tous les jours")

     if mode == "Seulement les jours de séance ou de match":
        st.subheader("Remplis ce questionnaire après chaque séance/match.")
     else:
        st.subheader("Remplis ce questionnaire tous les jours.")
    
# Nom
    username = st.session_state.get("username", "")
    role = st.session_state.get("role", "")
    club = st.session_state.get("club","")

    default_nom = username if role == "player" else ""

    nom = st.session_state.get("username", "")
    st.write(f"Identifiant : {nom}")

    # Afficher la dernière date de réponse
    df_user = load_responses(nom=nom)
    if not df_user.empty:
        df_user['Date_dt'] = df_user['Date'].apply(lambda d: datetime.strptime(d, "%d/%m/%Y"))
        derniere_date = df_user['Date_dt'].max()
        st.info(f"📅 Dernière réponse enregistrée le : {derniere_date.strftime('%d/%m/%Y')}")
    else:
        st.info("📅 Aucune réponse enregistrée pour le moment.")
        
# Date
    aujourd_hui = datetime.today().date()

    date_choisie = st.date_input(
        "Séléctionne la bonne date.",
        value=aujourd_hui,
        max_value=aujourd_hui,
        format="DD/MM/YYYY"
    )

# ------------------------------------------------------------ Questions -----------------------------------------------------------
    # Récupération du club du joueur et du coach associé
    club = st.session_state.get("club", "")
    coach_nom = get_coach_for_club(club)

# On charge les préférences du coach
    if coach_nom:
     prefs = get_preferences(coach_nom)
     mode = prefs.get("mode_questionnaire", "Tous les jours")
    else:
     mode = "Tous les jours"  # valeur par défaut

# En fonction du mode de réponse choisi par le coach
    if mode == "Tous les jours":
     seance = st.radio(
        "🎯 As-tu fait une séance ou un match à cette date ?",
        ["Oui", "Non"]
     )

     if seance == "Oui":
        st.subheader("🔥 Intensité")
        intensite = st.slider(
            "Évalue l'intensité de la séance/du match.",
            min_value=1,
            max_value=10,
            value=5,
            help="1 = aucune intensité, 10 = intensité maximale"
        )
     else:
        intensite = None  # ou 0 si tu préfères enregistrer une valeur numérique

    elif mode == "Seulement les jours de séance ou de match":
     st.subheader("🔥 Intensité")
     intensite = st.slider(
        "Évalue l'intensité de la séance/du match.",
        min_value=1,
        max_value=10,
        value=5,
        help="1 = aucune intensité, 10 = intensité maximale"
     )

    st.subheader("💤Sommeil")
    sommeil = st.slider(
        "Évalue la qualité de ton dernier sommeil.",
        min_value=1,
        max_value=10,
        value=5,
        help="1 = très mal dormi, 10 = très bien dormi"
    )

    st.subheader("🥱Fatigue")
    fatigue = st.slider(
        "Évalue ton niveau de fatigue.",
        min_value=1,
        max_value=10,
        value=5,
        help="1 = aucune fatigue, 10 = exténué"
    )

    st.subheader("😟Stress")
    stress = st.slider(
        "Évalue ton stress actuel.",
        min_value=1,
        max_value=10,
        value=5,
        help="1 = aucun stress, 10 = très stressé"
    )

    st.subheader("⚡Dynamisme")
    dynamisme = st.slider(
        "Évalue ton dynamisme actuel.",
        min_value=1,
        max_value=10,
        value=5,
        help="1 = très peu dynamique, 10 = très dynamique"
    )

    st.subheader("🤕Douleurs")
    douleurs = st.radio("As-tu des douleurs et/ou des courbatures ?", ("Non", "Oui"))
    description_douleurs = ""
    if douleurs == "Oui":
        description_douleurs = st.text_area("Où sont les douleurs ? Précise les informations.")

# --------------------------------------------------------- Envoyer réponses --------------------------------------------------------
    if st.button("Envoyer"):
     if not nom or nom.strip() == "":
        st.error("Penses à mettre ton nom avant d'envoyer.")
     else:
        nouvelle_reponse = {
            "Nom": nom,
            "Club": club,
            "Date": date_choisie.strftime("%d/%m/%Y"),
            "Intensité": intensite,
            "Sommeil": sommeil,
            "Fatigue": fatigue,
            "Stress": stress,
            "Dynamisme": dynamisme,
            "Douleurs": douleurs,
            "Description des douleurs": description_douleurs
        }

        success, error_msg = save_response(nouvelle_reponse)
        if success:
            st.success("Réponses enregistrées ! (Tu peux corriger une saisie en remplissant à nouveau pour la même date)")
        else:
            st.error(f"Erreur lors de l'enregistrement : {error_msg}")

# ================================================== Compte rendu individuel joueur ==================================================
elif page == "Compte rendu individuel (joueur)":
    st.title("Compte rendu individuel")

    # ------------------------------------------------------- Séance/match -----------------------------------------------------
    st.subheader("📍Suivi séance/match unique")

    username = st.session_state.get("username", "")

    df_user = load_responses(nom=username)
    prefs = get_preferences(username)

    if df_user.empty:
        st.info("Aucune donnée enregistrée.")
    else:
        # 🔁 Conversion des dates texte vers date Python
        df_user["Date_obj"] = df_user["Date"].apply(lambda x: datetime.strptime(x, "%d/%m/%Y").date())

# 📅 Sélection avec calendrier
        selected_date = st.date_input(
         "Sélectionne une date dans le calendrier :",
         value=max(df_user["Date_obj"]),  # Par défaut : dernière date
         format="DD/MM/YYYY"
        )

# 🔍 Filtrer la ligne correspondant à cette date
        df_date = df_user[df_user["Date_obj"] == selected_date]


        if prefs["show_seance"]:
         if not df_date.empty:
            data_selectionnee = df_date.iloc[0]

            def plot_gauge_in_col(col, title, value, inverse_colors=False):
                if inverse_colors:
                    steps = [
                        {'range': [1, 4], 'color': 'rgba(15, 154, 75, 0.65)'},
                        {'range': [4, 7], 'color': 'rgba(249, 206, 105, 0.69)'},
                        {'range': [7, 10], 'color': 'rgba(215, 72, 47, 0.68)'}
                    ]
                else:
                    steps = [
                        {'range': [1, 4], 'color': 'rgba(215, 72, 47, 0.68)'},
                        {'range': [4, 7], 'color': 'rgba(249, 206, 105, 0.69)'},
                        {'range': [7, 10], 'color': 'rgba(15, 154, 75, 0.65)'}
                    ]

                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=value,
                    number={'font': {'size': 23, 'color': "#2a3f5f"}},
                    title={'text': title, 'font': {'size': 18, 'color': "#2a3f5f"}},
                    gauge={
                        'axis': {'range': [1, 10], 'tickfont': {'size': 10}},
                        'bar': {'color': 'rgba(0,0,0,0)', 'thickness': 0},
                        'steps': steps,
                        'threshold': {
                            'line': {'color': "#2a3f5f", 'width': 5},
                            'thickness': 1,
                            'value': value
                        }
                    }
                ))
                fig.update_layout(height=200, margin=dict(l=20, r=20, t=30, b=0))
                col.plotly_chart(fig, use_container_width=True)

            cols1 = st.columns(3)
            cols2 = st.columns(3)

            
            plot_gauge_in_col(cols1[0], "Intensité", data_selectionnee['Intensite'], inverse_colors=True)
            plot_gauge_in_col(cols1[1], "Sommeil", data_selectionnee['Sommeil'])
            plot_gauge_in_col(cols1[2], "Fatigue", data_selectionnee['Fatigue'], inverse_colors=True)

            plot_gauge_in_col(cols2[0], "Stress", data_selectionnee['Stress'], inverse_colors=True)
            plot_gauge_in_col(cols2[1], "Dynamisme", data_selectionnee['Dynamisme'])

            
            if data_selectionnee['Douleurs'] == "Oui":
                st.write(f"Description des douleurs : {data_selectionnee['DescriptionDouleurs']}")
            else:
                st.write("Pas de douleurs signalées.")
         else:
            st.info("Aucune donnée enregistrée pour cette date.")

    # ---------------------------------------------------------- Semaine --------------------------------------------------------
    st.subheader("📆Suivi hebdomadaire")

    df_user = load_responses(nom=username)
    df_user["Date"] = pd.to_datetime(df_user["Date"], format="%d/%m/%Y")

    if df_user.empty:
     st.info("Aucune donnée enregistrée.")
     
    # Afficher graphique intensité, autres paramètres, score bien-être et comparaison avec semaine précédente.
    else:
     prefs = get_preferences(username)

     df_user["Semaine_lundi"] = df_user["Date"].apply(lambda d: d - timedelta(days=d.weekday()))
     semaines_unique = sorted(df_user["Semaine_lundi"].unique(), reverse=True)

     semaines_str = [
        f"Semaine du {s.strftime('%d/%m/%Y')} au {(s + timedelta(days=6)).strftime('%d/%m/%Y')}"
        for s in semaines_unique
     ]

     semaine_selectionnee_str = st.selectbox(
        "Pour consulter une autre semaine, sélectionne-la dans la liste déroulante :", semaines_str
     )

     index_semaine = semaines_str.index(semaine_selectionnee_str)
     semaine_selectionnee = semaines_unique[index_semaine]

     debut_semaine = semaine_selectionnee
     fin_semaine = semaine_selectionnee + timedelta(days=6)
     df_semaine = df_user[(df_user["Date"] >= debut_semaine) & (df_user["Date"] <= fin_semaine)]

     try:
        locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')  
     except:
        try:
            locale.setlocale(locale.LC_TIME, 'French')  
        except:
            st.warning("Impossible d'afficher les jours en français (paramètre régional manquant)")

    # -------------------------------------------------- Graphique intensité -----------------------------------------------------
     if prefs["show_weekly_intensity"] and not df_semaine.empty:
        jours_semaine = [debut_semaine + timedelta(days=i) for i in range(7)]
        df_jours = pd.DataFrame({"Date": jours_semaine})
        jours_ordonnes = [(debut_semaine + timedelta(days=i)).strftime("%A %d/%m").capitalize() for i in range(7)]

        df_merge = pd.merge(df_jours, df_semaine[["Date", "Intensite"]], on="Date", how="left")
        df_merge["Jour"] = df_merge["Date"].dt.strftime("%A %d/%m").str.capitalize()
        df_merge["Jour"] = pd.Categorical(df_merge["Jour"], categories=jours_ordonnes, ordered=True)

        def couleur_intensite(val):
            if pd.isna(val):
                return 'grey'
            elif val < 4:
                return 'green'
            elif val < 7:
                return 'yellow'
            else:
                return 'red'

        df_merge['Couleur'] = df_merge['Intensite'].apply(couleur_intensite)

        fig = px.bar(
            df_merge,
            x="Jour",
            y="Intensite",
            color='Couleur',
            color_discrete_map={
                'green': 'rgba(15, 154, 75, 0.8)',
                'yellow': 'rgba(249, 206, 105, 0.8)',
                'red': 'rgba(215, 72, 47, 0.8)',
                'grey': 'lightgrey'
            },
            labels={"Jour": "", "Intensité": "Intensité de la séance"},
            title="Intensité des séances par jour de la semaine"
        )

        fig.update_layout(
            xaxis_title="",
            yaxis_title="Intensité",
            yaxis_range=[0, 10],
            title_x=0.3,
            showlegend=False
        )
        fig.update_xaxes(categoryorder='array', categoryarray=jours_ordonnes)

        moyenne_intensite = df_merge["Intensite"].mean()
        fig.add_hline(
            y=moyenne_intensite,
            line_dash="dash",
            line_color='rgba(100,100,100,0.9)',
            annotation_text=f"Moyenne: {moyenne_intensite:.1f}",
            annotation_position="top left",
            annotation_font_color='rgba(100,100,100,0.9)'
        )

        st.plotly_chart(fig, use_container_width=True)

    # ----------------------------------- Graphique radar (sommeil, stress, fatigue, dynamisme) ----------------------------------
     colonnes_parametres = ["Sommeil", "Stress", "Fatigue", "Dynamisme"]
     moyennes = df_semaine[colonnes_parametres].mean()
     
     if prefs["show_weekly_parameter"] and not df_semaine.empty:
        def couleur_param(param, val):
            if pd.isna(val):
                return 'lightgrey'
            if param in ["Sommeil", "Dynamisme"]:
                if val < 4:
                    return 'rgba(215, 72, 47, 0.8)'
                elif val < 7:
                    return 'rgba(249, 206, 105, 0.8)'
                else:
                    return 'rgba(15, 154, 75, 0.8)'
            else:
                if val < 4:
                    return 'rgba(15, 154, 75, 0.8)'
                elif val < 7:
                    return 'rgba(249, 206, 105, 0.8)'
                else:
                    return 'rgba(215, 72, 47, 0.8)'

        df_radar = pd.DataFrame({
            "Paramètre": colonnes_parametres,
            "Valeur moyenne": [moyennes[p] for p in colonnes_parametres]
        })
        df_radar["Couleur"] = [
            couleur_param(param, val)
            for param, val in zip(df_radar["Paramètre"], df_radar["Valeur moyenne"])
        ]
        df_radar = pd.concat([df_radar, df_radar.iloc[[0]]], ignore_index=True)

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=df_radar["Valeur moyenne"],
            theta=df_radar["Paramètre"],
            mode='lines+markers',
            fill='toself',
            marker=dict(color='black', size=6),
            line=dict(color='rgba(150,150,150,0.4)', width=1),
            hoverinfo='skip'
        ))

        for i in range(len(df_radar) - 1):
            fig_radar.add_trace(go.Scatterpolar(
                r=[df_radar["Valeur moyenne"][i]],
                theta=[df_radar["Paramètre"][i]],
                mode='markers',
                marker=dict(
                    color=df_radar["Couleur"][i],
                    size=16,
                    line=dict(color='rgba(100,100,100,0.4)', width=1)
                ),
                text=[f"{df_radar['Paramètre'][i]}: {df_radar['Valeur moyenne'][i]:.2f}"],
                hoverinfo='text',
                showlegend=False
            ))

        fig_radar.update_layout(
            title="Moyenne hebdomadaire",
            title_x=0.38,
            polar=dict(
                bgcolor='rgba(200, 200, 200, 0.2)',
                radialaxis=dict(
                    visible=True,
                    range=[0, 10]
                )
            ),
            showlegend=False
        )

        st.plotly_chart(fig_radar, use_container_width=True)

    # ------------------------------------------------ Graphique score bien-être ------------------------------------------------
    
    # Calcul moyennes semaine.
     colonnes_parametres = ["Sommeil", "Stress", "Fatigue", "Dynamisme"]
     moyennes = df_semaine[colonnes_parametres].mean()
    
    # Calcul score bien-être.
     score_bien_etre = (
        moyennes["Sommeil"] +
        moyennes["Dynamisme"] +
        (10 - moyennes["Stress"]) +
        (10 - moyennes["Fatigue"])
     ) / 4

    # Calcul  moyennes semaine précédente.
     semaine_precedente = debut_semaine - timedelta(days=7)
     fin_semaine_precedente = semaine_precedente + timedelta(days=6)

     df_semaine_prec = df_user[
        (df_user["Date"] >= semaine_precedente) &
        (df_user["Date"] <= fin_semaine_precedente)
     ]

    # Score bien-être semaine précédente
     if not df_semaine_prec.empty:
        moyennes_prec = df_semaine_prec[colonnes_parametres].mean()
        score_bien_etre_prec = (
            moyennes_prec["Sommeil"] +
            moyennes_prec["Dynamisme"] +
            (10 - moyennes_prec["Stress"]) +
            (10 - moyennes_prec["Fatigue"])
        ) / 4
     else:
        score_bien_etre_prec = None

     # Afficher graphique score bien-être semaine et semaine précédente.
     if prefs["show_weekly_score_bien"] and score_bien_etre is not None:
    # Valeurs à afficher
      valeurs = [score_bien_etre]
      labels = ['Semaine en cours']

      if score_bien_etre_prec is not None:
        valeurs.append(score_bien_etre_prec)
        labels.append('Semaine précédente')

    # Couleurs : foncé pour actuelle, clair pour précédente
      couleurs = ['rgba(0, 0, 0, 0.9)']
      if score_bien_etre_prec is not None:
        couleurs.append('rgba(0, 0, 0, 0.4)')

    # Jauge Plotly horizontale
      fig_jauge = go.Figure()

      fig_jauge.add_trace(go.Bar(
        x=[4, 3, 3],
        y=['Score Bien-être']*3,
        orientation='h',
        marker=dict(color=[
            'rgba(215, 72, 47, 0.3)',    # Rouge
            'rgba(249, 206, 105, 0.3)',  # Jaune
            'rgba(15, 154, 75, 0.3)'     # Vert
        ]),
        showlegend=False,
        hoverinfo='none'
      ))

      fig_jauge.add_trace(go.Scatter(
        x=valeurs,
        y=['Score Bien-être'] * len(valeurs),
        mode='markers',
        marker=dict(color=couleurs, size=20),
        text=[f"{label}: {valeur:.2f}" for label, valeur in zip(labels, valeurs)],
        hoverinfo='text',
        showlegend=False
      ))

      fig_jauge.update_layout(
        xaxis=dict(range=[1, 10], title='Score (1 à 10)'),
        yaxis=dict(showticklabels=False),
        height=150,
        margin=dict(l=40, r=40, t=40, b=40),
        title="Score Bien-être (semaine en cours vs semaine précédente)",
        title_x=0.2,
      )

      st.plotly_chart(fig_jauge, use_container_width=True)

     # -------------------------------------------- Comparaison avec la semaine précédente ------------------------------------------
     if prefs["show_weekly_comp"]:
        st.markdown("<h5>Par rapport à la semaine précédente :</h5>", unsafe_allow_html=True)
        
        if df_semaine_prec.empty:
             st.info("Aucune donnée pour la semaine précédente.")
        else:     
         for param in colonnes_parametres:
            val_prec = moyennes_prec[param]
            val_actuelle = moyennes[param]
            variation = val_actuelle - val_prec

            alerte = ""
            if param in ["Stress", "Fatigue"]:
                if variation > 1:
                    pastille = "🔺"
                    alerte = "⚠️ "
                elif variation < -1:
                    pastille = "🔻"
                    alerte = "✅ "
                else:
                    pastille = "➖"
            else:
                if variation > 1:
                    pastille = "🔺"
                    alerte = "✅ "
                elif variation < -1:
                    pastille = "🔻"
                    alerte = "⚠️ "
                else:
                    pastille = "➖"

            st.write(f"**{alerte}{param}** : {val_prec:.2f} → {val_actuelle:.2f} {pastille}")

    # -------------------------------------------------------------- Mois -----------------------------------------------------------
    st.subheader("📅Suivi mensuel")
    
    df_user = load_responses(nom=username)
    prefs = get_preferences(username)

    df_user["Date"] = pd.to_datetime(df_user["Date"], format="%d/%m/%Y")

    if df_user.empty:
        st.info("Aucune donnée enregistrée.")
        
    # Afficher graphique intensité, autres paramètres, score bien-être, zcore et comparaison avec mois précédent.   
    else:
        # Préparer la liste déroulante par mois.
        df_user["Année_Mois"] = df_user["Date"].dt.to_period("M")
        mois_unique = sorted(df_user["Année_Mois"].unique(), reverse=True)
        mois_str = [mois.strftime("%B %Y") for mois in mois_unique]  
        mois_selectionne_str = st.selectbox(
            "Pour consulter un autre mois, sélectionne-le dans la liste déroulante :", mois_str
        )

        # Récupérer l'index sélectionné.
        index_mois = mois_str.index(mois_selectionne_str)
        mois_selectionne = mois_unique[index_mois]

        # Filtrer le dataframe pour le mois sélectionné.
        df_mois = df_user[df_user["Année_Mois"] == mois_selectionne]

        # Début et fin du mois sélectionné.
        debut_mois = mois_selectionne.to_timestamp()
        fin_mois = (mois_selectionne + 1).to_timestamp() - timedelta(seconds=1)

        # Étendre la plage de dates pour inclure les semaines complètes.
        df_mois_etendu = df_user[
            (df_user["Date"] >= (debut_mois - timedelta(days=6))) &
            (df_user["Date"] <= (fin_mois + timedelta(days=6)))
        ].copy()

        # Calcul du lundi de chaque semaine.
        df_mois_etendu["Semaine_lundi"] = df_mois_etendu["Date"].apply(lambda d: d - timedelta(days=d.weekday()))
        semaines = sorted(df_mois_etendu["Semaine_lundi"].unique())

# --------------------------------------------------- Graphique ligne intensité ------------------------------------------------------
        if prefs["show_monthly_intensity"] and not df_mois.empty:
         df_mois_sorted = df_mois.sort_values(by="Date")

         moyenne_intensite = df_mois_sorted["Intensite"].mean()

         # Mettre les couleur sur les graphiques.
         shapes = [
       # Vert entre 1 et 4
          dict(type="rect", xref="paper", yref="y", x0=0, x1=1, y0=1, y1=4,
            fillcolor='rgba(15, 154, 75, 0.5)', opacity=0.2, layer="below", line_width=0),
       # Jaune entre 4 et 7
          dict(type="rect", xref="paper", yref="y", x0=0, x1=1, y0=4, y1=7,
            fillcolor='rgba(249, 206, 105, 0.5)', opacity=0.2, layer="below", line_width=0),
       # Rouge entre 7 et 10
          dict(type="rect", xref="paper", yref="y", x0=0, x1=1, y0=7, y1=10,
            fillcolor='rgba(215, 72, 47, 0.5)', opacity=0.2, layer="below", line_width=0),
       # Ligne moyenne en pointillés
          dict(type="line", xref="paper", yref="y", x0=0, x1=1,
            y0=moyenne_intensite, y1=moyenne_intensite,
            line=dict(color='rgba(100, 100, 100, 0.9)', dash='dash', width=2))
        ]

    # Annotation pour la moyenne
         annotations = [dict(
          xref="paper", yref="y",
          x=0.01, y=moyenne_intensite,
          text=f"Moyenne : {moyenne_intensite:.2f}",
          showarrow=False,
          font=dict(color='rgba(100, 100, 100, 0.9)'),
          bgcolor='rgba(255,255,255,0.7)'
         )]

         fig = px.line(
          df_mois_sorted,
          x="Date",
          y="Intensite",  
          title=f"Intensité pour {mois_selectionne.strftime('%B %Y')}",
          labels={"Date": "Date", "Intensite": "Intensité"},
          color_discrete_sequence=['rgba(100,100,100,0.9)']
         )

         fig.update_layout(
          title_x=0.4,
          yaxis=dict(range=[1, 10]),
          xaxis=dict(tickformat='%d/%m'),
          shapes=shapes,
          annotations=annotations
         )
         
         fig.update_traces(connectgaps=True)

         st.plotly_chart(fig)

# ----------------------------------------------- Graphique ligne autres paramètres --------------------------------------------------
        if prefs["show_monthly_parameter"] and not df_mois.empty:
                df_long = df_mois.melt(
                   id_vars=["Date"], 
                   value_vars=["Stress", "Fatigue", "Sommeil", "Dynamisme"], 
                   var_name="Mesures", 
                   value_name="Valeurs"
                )

                fig = px.line(
                    df_long,
                    x="Date",
                    y="Valeurs", 
                    color="Mesures" ,
                    title=f"Stress, Fatigue, Sommeil et Dynamisme pour {mois_selectionne.strftime('%B %Y')}",
                    labels={"Date": "Date", "Valeurs": "Valeurs"},
                    color_discrete_sequence=['rgba(255,0,0,0.6)',       # Stress
                    'rgba(255,165,0,0.6)',     # Fatigue
                    'rgba(0,128,0,0.6)',       # Sommeil
                    'rgba(0,0,255,0.6)']      # Dynamisme]
                )

                fig.update_layout(
                    title_x=0.25,               
                    yaxis=dict(range=[1, 10]),
                    xaxis=dict(
                    tickformat='%d/%m'),
                )
                st.plotly_chart(fig)
                st.text("Tu peux cliquer sur les légendes pour masquer certaines variables.")
                
                # Calcul des moyennes mensuelles
                moyennes = df_mois[["Stress", "Fatigue", "Sommeil", "Dynamisme"]].mean().round(2)

                # Mise en forme en DataFrame pour affichage clair
                df_moyennes = moyennes.reset_index()
                df_moyennes.columns = ["Variable", "Moyenne"]

                # Affichage du tableau
                st.markdown("<h5>Moyennes mensuelles</h5>", unsafe_allow_html=True)

                df_moyennes = moyennes.reset_index()
                df_moyennes.columns = ["Variable", "Moyenne"]
                df_moyennes.set_index("Variable", inplace=True)

                styled_df = df_moyennes.style.apply(lambda x: style_moyennes(df_moyennes), axis=None)

                st.dataframe(styled_df, use_container_width=True)

# ------------------------------------------------------- Graphique zscore -----------------------------------------------------------
        if prefs["show_monthly_zscore"] and not df_mois.empty:
        # Calcul du Z-score par paramètre (colonne)
          colonnes = ["Stress", "Fatigue", "Sommeil", "Dynamisme"]
          df_zscore = df_mois.copy()
          # Calcul manuel du Z-score pour chaque colonne
          for col in colonnes:
            moyenne = df_mois[col].mean()
            ecart_type = df_mois[col].std()
            df_zscore[col] = (df_mois[col] - moyenne) / ecart_type

    # Transformation en format long pour tracé Plotly
          df_long = df_zscore.melt(
             id_vars=["Date"], 
             value_vars=colonnes, 
             var_name="Mesures", 
             value_name="Z-score"
          )

    # Graphique en ligne
          fig = px.line(
             df_long,
             x="Date",
             y="Z-score", 
             color="Mesures",
             title=f"Z-Score des paramètres pour {mois_selectionne.strftime('%B %Y')}",
             labels={"Date": "Date", "Z-score": "Z-score"},
             color_discrete_sequence=[
              'rgba(255,0,0,0.6)',     # Stress
              'rgba(255,165,0,0.6)',   # Fatigue
              'rgba(0,128,0,0.6)',     # Sommeil
              'rgba(0,0,255,0.6)'      # Dynamisme
             ]
          )

          fig.update_layout(
              title_x=0.25,
              yaxis=dict(title="Z-Score", range=[-3, 3], zeroline=True),
              xaxis=dict(tickformat='%d/%m'),
              shapes=[
                dict(
                  type="rect",
                  xref="paper",
                  yref="y",
                  x0=0,
                  x1=1,
                  y0=-2,
                  y1=2,
                  fillcolor="rgba(200, 200, 200, 0.2)",
                  layer="below",
                  line_width=0,
                )
              ]
          )


          st.plotly_chart(fig, use_container_width=True)
          st.text("Tu peux cliquer sur les légendes pour masquer certaines variables.")

# ------------------------------------------------- Graphique baton score bien etre --------------------------------------------------
        if prefs["show_monthly_score_bien"] and not df_mois.empty:
              
              # Calcul score bien-être moyen mensuel
              moyennes_mensuelles = df_mois_etendu[["Sommeil", "Dynamisme", "Stress", "Fatigue"]].mean()
              score_bien_etre_moyen_mois = (
                     moyennes_mensuelles["Sommeil"] + 
                     moyennes_mensuelles["Dynamisme"] + 
                     (10 - moyennes_mensuelles["Stress"]) + 
                     (10 - moyennes_mensuelles["Fatigue"])) / 4
              
              # Calcul du lundi de chaque date pour regrouper par semaine
              df_mois_etendu["Semaine_lundi"] = df_mois_etendu["Date"].apply(lambda d: d - timedelta(days=d.weekday()))
              semaines = sorted(df_mois_etendu["Semaine_lundi"].unique())

              scores = []
              labels = []

              for semaine in semaines:
                  debut_semaine = semaine
                  fin_semaine = semaine + timedelta(days=6)
                  df_semaine = df_mois_etendu[(df_mois_etendu["Date"] >= debut_semaine) & (df_mois_etendu["Date"] <= fin_semaine)]
                  # Conserver uniquement les semaines qui touchent le mois sélectionné
                  if fin_semaine >= debut_mois and debut_semaine <= fin_mois:

                   if not df_semaine.empty:
                      moyennes = df_semaine[["Sommeil", "Dynamisme", "Stress", "Fatigue"]].mean()
                      score = (moyennes["Sommeil"] + moyennes["Dynamisme"] + (10 - moyennes["Stress"]) + (10 - moyennes["Fatigue"])) / 4
                      scores.append(score)
                      labels.append(f"Semaine du {debut_semaine.strftime('%d/%m')}")
                   else:
                      scores.append(None)
                      labels.append(f"Semaine du {debut_semaine.strftime('%d/%m')}")

              colors = []
              for score in scores:
                  if score is None:
                      colors.append('rgba(200,200,200,0.3)')  # gris clair pour les valeurs manquantes
                  elif score < 4:
                      colors.append('rgba(215, 72, 47, 0.8)')  # rouge
                  elif score < 7:
                      colors.append('rgba(249, 206, 105, 0.8)')  # jaune
                  else:
                      colors.append('rgba(15, 154, 75, 0.8)')  # vert


              fig_bar = go.Figure(go.Bar(
                  x=labels,
                  y=scores,
                  marker_color=colors
              ))

              fig_bar.update_layout(
                   title=dict(text=f"Score Bien-être moyen par semaine - {mois_selectionne.strftime('%B %Y')}", x=0.5, xanchor='center'),
                   xaxis_title="Semaine",
                   yaxis_title="Score Bien-être",
                   yaxis=dict(range=[0, 10]),
                   margin=dict(t=50, b=100),
                   height=400
              )

              fig_bar.add_hline(
                 y=score_bien_etre_moyen_mois,
                 line_dash="dash",
                 line_color='rgba(100, 100, 100, 0.9)',
                 annotation_text=f"Moyenne mensuelle : {score_bien_etre_moyen_mois:.2f}",
                 annotation_position="top left",
                 annotation_font_color='rgba(100, 100, 100, 0.9)'
              )

              st.plotly_chart(fig_bar, use_container_width=True)
        
# ------------------------------------------------ Comparaison avec le mois précédent ------------------------------------------------
        index_mois_prec = index_mois + 1  

        if index_mois_prec < len(mois_unique):
              mois_precedent = mois_unique[index_mois_prec]
              df_mois_prec = df_user[df_user["Année_Mois"] == mois_precedent]
        else:
              df_mois_prec = pd.DataFrame()  

        colonnes_parametres = ["Stress", "Fatigue", "Sommeil", "Dynamisme"]

        if not df_mois.empty:
             moyennes = df_mois[colonnes_parametres].mean()
        else:
             moyennes = pd.Series([None]*len(colonnes_parametres), index=colonnes_parametres)

        if not df_mois_prec.empty:
             moyennes_prec = df_mois_prec[colonnes_parametres].mean()
        else:
             moyennes_prec = pd.Series([None]*len(colonnes_parametres), index=colonnes_parametres)

        if prefs["show_monthly_comp"]:
         st.markdown("<h5>Par rapport au mois précédent :</h5>", unsafe_allow_html=True)

         if df_mois_prec.empty:
             st.info("Aucune donnée pour le mois précédent.")
         else:
             for param in colonnes_parametres:
                 val_prec = moyennes_prec[param]
                 val_actuelle = moyennes[param]
                 variation = val_actuelle - val_prec
        
                 alerte = "" 

                 # Détection de la variation (positive, négative, neutre)
                 if param in ["Stress", "Fatigue"]:
                    if variation > 1:
                        pastille = "🔺"   # augmentation = négatif  
                        alerte = "⚠️ "
                    elif variation < -1:
                        pastille = "🔻"  # diminution = positif
                        alerte = "✅ "
                    else:
                        pastille = "➖"  # stable
                 else:  # Sommeil, Dynamisme
                    if variation > 1:
                       pastille = "🔺" 
                       alerte = "✅ " 
                    elif variation < -1:
                       pastille = "🔻" 
                       alerte = "⚠️ " 
                    else:
                       pastille = "➖"

                 st.write(f"**{alerte}{param}** : {val_prec:.2f} → {val_actuelle:.2f} {pastille}")

    # --------------------------------------------------------- Synthèse -----------------------------------------------------------
    st.subheader("📊Synthèse")

    df_user = load_responses(nom=username)
    prefs = get_preferences(username)


    if df_user.empty:
            st.info("Aucune donnée enregistrée.")
            
    # Afficher graphique intensité, autres paramètres, score bien-être et zcore global.       
    else:
     dates_disponibles = sorted(
                df_user["Date"].unique(),
                key=lambda d: datetime.strptime(d, "%d/%m/%Y"),
                reverse=True
            )
     df_user['Date'] = pd.to_datetime(df_user['Date'], format="%d/%m/%Y")

            # Trier les dates uniques
     dates = sorted(df_user['Date'].dt.date.unique())

            # Formatter les dates pour affichage (jj/mm/aaaa)
     formatted_dates = [d.strftime("%d/%m/%Y") for d in dates]
     format_to_date = {d.strftime("%d/%m/%Y"): d for d in dates}

     if len(formatted_dates) < 2:
              st.warning("Pas assez de données pour sélectionner une plage de dates.")
              st.dataframe(df_user.reset_index(drop=True))
     else:
              start_fmt, end_fmt = st.select_slider(
                "Sélectionne la plage de dates",
                options=formatted_dates,
                value=(formatted_dates[0], formatted_dates[-1])
              )

              start_date = format_to_date[start_fmt]
              end_date = format_to_date[end_fmt]

              mask = (df_user['Date'].dt.date >= start_date) & (df_user['Date'].dt.date <= end_date)
              df_filtered = df_user.loc[mask]

# ----------------------------------------------------- Graphique intensité -----------------------------------------------------------
     if prefs["show_global_intensity"] and not df_filtered.empty:
      df_filtered_sorted = df_filtered.sort_values(by="Date")

      fig = px.line(
        df_filtered_sorted,
        x="Date",
        y="Intensite",  
        title=f"Intensité des séances entre {start_date.strftime('%d/%m/%Y')} et {end_date.strftime('%d/%m/%Y')}",
        labels={"Date": "Date", "Intensite": "Intensité"},
        color_discrete_sequence=['rgba(100,100,100,0.9)']
      )

      fig.update_traces(connectgaps=True)

    # Générer des bandes verticales à partir de la vraie première date
      shapes = []
      dates = df_filtered_sorted["Date"].dt.floor("D").unique()
      min_date = min(dates)
      max_date = max(dates)

      current = min_date
      toggle = True
      while current < max_date:
        next_cut = current + timedelta(days=7)
        shapes.append(dict(
            type="rect",
            xref="x", yref="paper",
            x0=current, x1=min(next_cut, max_date),  
            y0=0, y1=1,
            fillcolor='rgba(180, 180, 180, 0.2)' if toggle else 'rgba(120, 120, 120, 0.2)',
            line_width=0,
            layer="below"
        ))
        current = next_cut
        toggle = not toggle

      # Calcul de la moyenne d'intensité
      moyenne_intensite = df_filtered_sorted["Intensite"].mean()

# Ajouter la ligne de moyenne dans la liste des shapes
      shapes.append(dict(
        type="line",
        xref="paper", yref="y",
        x0=0, x1=1,
        y0=moyenne_intensite, y1=moyenne_intensite,
        line=dict(
         color='rgba(100, 100, 100, 0.9)',
         dash='dash',
         width=2
        )
      ))

# Ajouter l'annotation de la ligne
      annotations = [dict(
        xref="paper", yref="y",
        x=0.01, y=moyenne_intensite,
        text=f"Moyenne : {moyenne_intensite:.2f}",
        showarrow=False,
        font=dict(color='rgba(100, 100, 100, 0.9)'),
        bgcolor='rgba(255,255,255,0.7)'
      )]



      fig.update_layout(
       title_x=0.25,
       yaxis=dict(range=[1, 10]),
       xaxis=dict(tickformat='%d/%m'),
       shapes=shapes,
       annotations=annotations
      )


      st.plotly_chart(fig)

#--------------------------------------------------- Graphique autres paramètres ------------------------------------------------------
     if prefs["show_global_parameter"] and not df_filtered.empty:
    # Réorganisation des données pour un graphique long format
      df_long = df_filtered.melt(
        id_vars=["Date"], 
        value_vars=["Stress", "Fatigue", "Sommeil", "Dynamisme"], 
        var_name="Mesures", 
        value_name="Valeurs"
      )
      df_long = df_long.sort_values(by="Date")

    # Création du graphique
      fig = px.line(
        df_long,
        x="Date",
        y="Valeurs", 
        color="Mesures",
        title=f"Stress, Fatigue, Sommeil et Dynamisme du {start_date.strftime('%d/%m/%Y')} au {end_date.strftime('%d/%m/%Y')}",
        labels={"Date": "Date", "Valeurs": "Valeurs"},
        color_discrete_sequence=[
            'rgba(255,0,0,0.6)',       # Stress
            'rgba(255,165,0,0.6)',     # Fatigue
            'rgba(0,128,0,0.6)',       # Sommeil
            'rgba(0,0,255,0.6)'        # Dynamisme
        ]
      )

      fig.update_layout(
        title_x=0.17,
        yaxis=dict(range=[1, 10]),
        xaxis=dict(tickformat='%d/%m'),
      )

      st.plotly_chart(fig)
      st.text("Tu peux cliquer sur les légendes pour masquer certaines variables.")

    # Calcul des moyennes sur la plage sélectionnée
      moyennes = df_filtered[["Stress", "Fatigue", "Sommeil", "Dynamisme"]].mean().round(2)

    # Mise en forme pour affichage
      df_moyennes = moyennes.reset_index()
      df_moyennes.columns = ["Variable", "Moyenne"]

      st.markdown("<h5>Moyennes sur la période sélectionnée</h5>", unsafe_allow_html=True)

# Supposons que df_moyennes est calculé sur la période sélectionnée et a les colonnes Variable et Moyenne
      df_moyennes.set_index("Variable", inplace=True)

# Appliquer le style avec la fonction que tu as définie
      styled_df = df_moyennes.style.apply(lambda x: style_moyennes(df_moyennes), axis=None)

      st.dataframe(styled_df, use_container_width=True)

#-------------------------------------------------------- Graphique z-score -----------------------------------------------------------
     if prefs["show_global_zscore"] and not df_filtered.empty:
    # Calcul du Z-score sur les données filtrées par le slider
      colonnes = ["Stress", "Fatigue", "Sommeil", "Dynamisme"]
      df_zscore = df_filtered.copy()

    # Calcul manuel du Z-score pour chaque paramètre
      for col in colonnes:
        moyenne = df_filtered[col].mean()
        ecart_type = df_filtered[col].std()
        df_zscore[col] = (df_filtered[col] - moyenne) / ecart_type

    # Transformation en format long pour tracé Plotly
      df_long = df_zscore.melt(
        id_vars=["Date"], 
        value_vars=colonnes, 
        var_name="Mesures", 
        value_name="Z-score"
      )

      df_long = df_long.sort_values(by="Date")

    # Graphique en ligne
      fig = px.line(
        df_long,
        x="Date",
        y="Z-score", 
        color="Mesures",
        title=f"Z-Score des paramètres du {start_date.strftime('%d/%m/%Y')} au {end_date.strftime('%d/%m/%Y')}",
        labels={"Date": "Date", "Z-score": "Z-score"},
        color_discrete_sequence=[
            'rgba(255,0,0,0.6)',     # Stress
            'rgba(255,165,0,0.6)',   # Fatigue
            'rgba(0,128,0,0.6)',     # Sommeil
            'rgba(0,0,255,0.6)'      # Dynamisme
        ]
      )

    # Supprimer les points et ajuster les axes
      for trace in fig.data:
        trace.mode = "lines"

      fig.update_layout(
        title_x=0.23,
        yaxis=dict(title="Z-Score", range=[-3, 3], zeroline=True),
        xaxis=dict(tickformat='%d/%m'),
        shapes=[
            dict(
                type="rect",
                xref="paper",
                yref="y",
                x0=0,
                x1=1,
                y0=-2,
                y1=2,
                fillcolor="rgba(200, 200, 200, 0.2)",
                layer="below",
                line_width=0,
            )
        ]
      )

      st.plotly_chart(fig, use_container_width=True)
      st.text("Tu peux cliquer sur les légendes pour masquer certaines variables.")

#--------------------------------------------------- Graphique score bien etre --------------------------------------------------------
     if prefs["show_global_score_bien"] and not df_filtered.empty:
    # Calcul du score bien-être ligne par ligne
      df_filtered = df_filtered.copy()
      df_filtered["Score bien-être"] = (
        df_filtered["Sommeil"] +
        df_filtered["Dynamisme"] +
        (10 - df_filtered["Stress"]) +
        (10 - df_filtered["Fatigue"])
      ) / 4

    # Tri par date
      df_filtered = df_filtered.sort_values(by="Date")

    # Calcul de la moyenne du score bien-être
      moyenne_score = df_filtered["Score bien-être"].mean()

    # Préparation des zones colorées + ligne moyenne
      shapes = [
        # rouge entre 1 et 4
        dict(type="rect", xref="paper", yref="y", x0=0, x1=1, y0=1, y1=4,
             fillcolor='rgba(215, 72, 47, 0.5)', opacity=0.2, layer="below", line_width=0),
        # jaune entre 4 et 7
        dict(type="rect", xref="paper", yref="y", x0=0, x1=1, y0=4, y1=7,
             fillcolor='rgba(249, 206, 105, 0.5)', opacity=0.2, layer="below", line_width=0),
        # vert entre 7 et 10
        dict(type="rect", xref="paper", yref="y", x0=0, x1=1, y0=7, y1=10,
             fillcolor='rgba(15, 154, 75, 0.5)', opacity=0.2, layer="below", line_width=0),
        # Ligne moyenne en pointillés
        dict(type="line", xref="paper", yref="y", x0=0, x1=1,
             y0=moyenne_score, y1=moyenne_score,
             line=dict(color='rgba(100, 100, 100, 0.9)', dash='dash', width=2))
      ]

    # Annotation pour la moyenne
      annotations = [dict(
        xref="paper", yref="y",
        x=0.01, y=moyenne_score,
        text=f"Moyenne : {moyenne_score:.2f}",
        showarrow=False,
        font=dict(color='rgba(100, 100, 100, 0.9)'),
        bgcolor='rgba(255,255,255,0.7)'
      )]

    # Création du graphique avec le même style que les autres
      fig = px.line(
        df_filtered,
        x="Date",
        y="Score bien-être",
        title=f"Score bien-être du {start_date.strftime('%d/%m/%Y')} au {end_date.strftime('%d/%m/%Y')}",
        labels={"Date": "Date", "Score bien-être": "Score bien-être"},
        markers=False,
        color_discrete_sequence=['rgba(100,100,100,0.9)']
      )

      fig.update_layout(
        title_x=0.3,
        yaxis=dict(range=[1, 10]),
        xaxis=dict(
            tickformat='%d/%m',
            range=[df_filtered["Date"].min(), df_filtered["Date"].max()]),
        shapes=shapes,
        annotations=annotations
      )

      st.plotly_chart(fig)

# ================================================== Compte rendu individuel coach ===================================================
elif page == "Compte rendu individuel (coach)":
    st.title("Compte rendu individuel")

    df = load_responses()

    club = st.session_state.get("club", "").strip().lower()

        # On filtre df pour ne garder que le club
    df["Club"] = df["Club"].str.strip().str.lower()
    df_club = df[df["Club"] == club]

        # Extraire tous les joueurs du club depuis USERS (pas juste ceux avec données)
        # Extraire uniquement les joueurs (role == "player") du club
    joueurs_club = sorted([
        username for username, info in USERS.items()
        if info["club"].strip().lower() == club and info["role"].strip().lower() == "player"
    ])

    joueur_selectionne = st.selectbox("Sélectionne un joueur de l'équipe :", joueurs_club)

        # df_user correspond aux réponses de ce joueur (s'il y en a)
    df_user = df_club[df_club["Nom"] == joueur_selectionne]

    prefs = get_preferences(joueur_selectionne)  

    if df_user.empty:
            st.info("Aucune donnée enregistrée pour ce joueur.")
    else:
            # On simule que c'est ce joueur qui est connecté
            username = joueur_selectionne

# ----------------------------------------------------- Suivi quotidien ----------------------------------------------------------
            st.subheader("📍Suivi quotidien")
            
            coach_username = st.session_state.get("username")
            prefs = get_preferences(coach_username)        

            #st.dataframe(df_user)

            if df_user.empty:
                st.info("Aucune donnée enregistrée.")
            else:
                # 🔁 Conversion des dates texte vers date Python
                df_user["Date_obj"] = df_user["Date"].apply(lambda x: datetime.strptime(x, "%d/%m/%Y").date())

# 📅 Sélection avec calendrier
                selected_date = st.date_input(
                 "Sélectionne une date dans le calendrier :",
                 value=max(df_user["Date_obj"]),  # Par défaut : dernière date
                 format="DD/MM/YYYY"
                )



# 🔍 Filtrer la ligne correspondant à cette date
                df_date = df_user[df_user["Date_obj"] == selected_date]


                if prefs["show_seance_coach"]:
                 if not df_date.empty:
                    data_selectionnee = df_date.iloc[0]

                    def plot_gauge_in_col(col, title, value, inverse_colors=False):
                        if inverse_colors:
                            steps = [
                                {'range': [1, 4], 'color': 'rgba(15, 154, 75, 0.65)'},
                                {'range': [4, 7], 'color': 'rgba(249, 206, 105, 0.69)'},
                                {'range': [7, 10], 'color': 'rgba(215, 72, 47, 0.68)'}
                            ]
                        else:
                            steps = [
                                {'range': [1, 4], 'color': 'rgba(215, 72, 47, 0.68)'},
                                {'range': [4, 7], 'color': 'rgba(249, 206, 105, 0.69)'},
                                {'range': [7, 10], 'color': 'rgba(15, 154, 75, 0.65)'}
                            ]

                        fig = go.Figure(go.Indicator(
                            mode="gauge+number",
                            value=value,
                            number={'font': {'size': 23, 'color': "#2a3f5f"}},
                            title={'text': title, 'font': {'size': 18, 'color': "#2a3f5f"}},
                            gauge={
                                'axis': {'range': [1, 10], 'tickfont': {'size': 10}},
                                'bar': {'color': 'rgba(0,0,0,0)', 'thickness': 0},
                                'steps': steps,
                                'threshold': {
                                    'line': {'color': "#2a3f5f", 'width': 5},
                                    'thickness': 1,
                                    'value': value
                                }
                            }
                        ))
                        fig.update_layout(height=200, margin=dict(l=20, r=20, t=30, b=0))
                        col.plotly_chart(fig, use_container_width=True)

                    cols1 = st.columns(3)
                    cols2 = st.columns(3)

                    
                    plot_gauge_in_col(cols1[0], "Intensité", data_selectionnee['Intensite'], inverse_colors=True)
                    plot_gauge_in_col(cols1[1], "Sommeil", data_selectionnee['Sommeil'])
                    plot_gauge_in_col(cols1[2], "Fatigue", data_selectionnee['Fatigue'], inverse_colors=True)

                    plot_gauge_in_col(cols2[0], "Stress", data_selectionnee['Stress'], inverse_colors=True)
                    plot_gauge_in_col(cols2[1], "Dynamisme", data_selectionnee['Dynamisme'])

                    
                    if data_selectionnee['Douleurs'] == "Oui":
                        st.write(f"Description des douleurs : {data_selectionnee['DescriptionDouleurs']}")
                    else:
                        st.write("Pas de douleurs signalées.")
                 else:
                    st.info("Aucune donnée enregistrée pour cette date.")

            # ------------------------------------------------------- Semaine --------------------------------------------------------
            st.subheader("📆Suivi hebdomadaire")

            coach_username = st.session_state.get("username")
            df_user["Date"] = pd.to_datetime(df_user["Date"], format="%d/%m/%Y")

            if df_user.empty:
             st.info("Aucune donnée enregistrée.")
             
            # Afficher les graphiques pour la semaine 
            else:
             prefs = get_preferences(coach_username)

             df_user["Semaine_lundi"] = df_user["Date"].apply(lambda d: d - timedelta(days=d.weekday()))
             semaines_unique = sorted(df_user["Semaine_lundi"].unique(), reverse=True)

             semaines_str = [
                f"Semaine du {s.strftime('%d/%m/%Y')} au {(s + timedelta(days=6)).strftime('%d/%m/%Y')}"
                for s in semaines_unique
             ]

             semaine_selectionnee_str = st.selectbox(
                "Pour consulter une autre semaine, sélectionne-la dans la liste déroulante :", semaines_str
             )

             index_semaine = semaines_str.index(semaine_selectionnee_str)
             semaine_selectionnee = semaines_unique[index_semaine]

             debut_semaine = semaine_selectionnee
             fin_semaine = semaine_selectionnee + timedelta(days=6)
             df_semaine = df_user[(df_user["Date"] >= debut_semaine) & (df_user["Date"] <= fin_semaine)]

             try:
                locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')  
             except:
                try:
                    locale.setlocale(locale.LC_TIME, 'French')  
                except:
                    st.warning("Impossible d'afficher les jours en français (paramètre régional manquant)")

            # ------------------------------------------------- Graphique intensité ----------------------------------------------------
             if prefs["show_weekly_intensity_coach"] and not df_semaine.empty:
                jours_semaine = [debut_semaine + timedelta(days=i) for i in range(7)]
                df_jours = pd.DataFrame({"Date": jours_semaine})
                jours_ordonnes = [(debut_semaine + timedelta(days=i)).strftime("%A %d/%m").capitalize() for i in range(7)]

                df_merge = pd.merge(df_jours, df_semaine[["Date", "Intensite"]], on="Date", how="left")
                df_merge["Jour"] = df_merge["Date"].dt.strftime("%A %d/%m").str.capitalize()
                df_merge["Jour"] = pd.Categorical(df_merge["Jour"], categories=jours_ordonnes, ordered=True)

                def couleur_intensite(val):
                    if pd.isna(val):
                        return 'grey'
                    elif val < 4:
                        return 'green'
                    elif val < 7:
                        return 'yellow'
                    else:
                        return 'red'

                df_merge['Couleur'] = df_merge['Intensite'].apply(couleur_intensite)

                fig = px.bar(
                    df_merge,
                    x="Jour",
                    y="Intensite",
                    color='Couleur',
                    color_discrete_map={
                        'green': 'rgba(15, 154, 75, 0.8)',
                        'yellow': 'rgba(249, 206, 105, 0.8)',
                        'red': 'rgba(215, 72, 47, 0.8)',
                        'grey': 'lightgrey'
                    },
                    labels={"Jour": "", "Intensité": "Intensité de la séance"},
                    title="Intensité par jour de la semaine"
                )

                fig.update_layout(
                    xaxis_title="",
                    yaxis_title="Intensité",
                    yaxis_range=[0, 10],
                    title_x=0.3,
                    showlegend=False
                )
            
                fig.update_xaxes(categoryorder='array', categoryarray=jours_ordonnes)

                moyenne_intensite = df_merge["Intensite"].mean()
                fig.add_hline(
                    y=moyenne_intensite,
                    line_dash="dash",
                    line_color='rgba(100,100,100,0.9)',
                    annotation_text=f"Moyenne: {moyenne_intensite:.1f}",
                    annotation_position="top left",
                    annotation_font_color='rgba(100,100,100,0.9)'
                )

                st.plotly_chart(fig, use_container_width=True)

            # --------------------------------------------- Graphique autres paramètres ------------------------------------------------
             colonnes_parametres = ["Sommeil", "Stress", "Fatigue", "Dynamisme"]
             moyennes = df_semaine[colonnes_parametres].mean()
            
             if prefs["show_weekly_parameter_coach"] and not df_semaine.empty:
                def couleur_param(param, val):
                    if pd.isna(val):
                        return 'lightgrey'
                    if param in ["Sommeil", "Dynamisme"]:
                        if val < 4:
                            return 'rgba(215, 72, 47, 0.8)'
                        elif val < 7:
                            return 'rgba(249, 206, 105, 0.8)'
                        else:
                            return 'rgba(15, 154, 75, 0.8)'
                    else:
                        if val < 4:
                            return 'rgba(15, 154, 75, 0.8)'
                        elif val < 7:
                            return 'rgba(249, 206, 105, 0.8)'
                        else:
                            return 'rgba(215, 72, 47, 0.8)'

                df_radar = pd.DataFrame({
                    "Paramètre": colonnes_parametres,
                    "Valeur moyenne": [moyennes[p] for p in colonnes_parametres]
                })
                df_radar["Couleur"] = [
                    couleur_param(param, val)
                    for param, val in zip(df_radar["Paramètre"], df_radar["Valeur moyenne"])
                ]
                df_radar = pd.concat([df_radar, df_radar.iloc[[0]]], ignore_index=True)

                fig_radar = go.Figure()
                fig_radar.add_trace(go.Scatterpolar(
                    r=df_radar["Valeur moyenne"],
                    theta=df_radar["Paramètre"],
                    mode='lines+markers',
                    fill='toself',
                    marker=dict(color='black', size=6),
                    line=dict(color='rgba(150,150,150,0.4)', width=1),
                    hoverinfo='skip'
                ))

                for i in range(len(df_radar) - 1):
                    fig_radar.add_trace(go.Scatterpolar(
                        r=[df_radar["Valeur moyenne"][i]],
                        theta=[df_radar["Paramètre"][i]],
                        mode='markers',
                        marker=dict(
                            color=df_radar["Couleur"][i],
                            size=16,
                            line=dict(color='rgba(100,100,100,0.4)', width=1)
                        ),
                        text=[f"{df_radar['Paramètre'][i]}: {df_radar['Valeur moyenne'][i]:.2f}"],
                        hoverinfo='text',
                        showlegend=False
                    ))

                fig_radar.update_layout(
                    title="Moyenne hebdomadaire",
                    title_x=0.38,
                    polar=dict(
                        bgcolor='rgba(200, 200, 200, 0.2)',
                        radialaxis=dict(
                            visible=True,
                            range=[0, 10]
                        )
                    ),
                    showlegend=False
                )

                st.plotly_chart(fig_radar, use_container_width=True)

            # --------------------------------------------------- Score bien etre ------------------------------------------------------
             colonnes_parametres = ["Sommeil", "Stress", "Fatigue", "Dynamisme"]
             moyennes = df_semaine[colonnes_parametres].mean()

             score_bien_etre = (
                moyennes["Sommeil"] +
                moyennes["Dynamisme"] +
                (10 - moyennes["Stress"]) +
                (10 - moyennes["Fatigue"])
             ) / 4

            # Calcul des moyennes de la semaine précédente
             semaine_precedente = debut_semaine - timedelta(days=7)
             fin_semaine_precedente = semaine_precedente + timedelta(days=6)

             df_semaine_prec = df_user[
                (df_user["Date"] >= semaine_precedente) &
                (df_user["Date"] <= fin_semaine_precedente)
             ]

            # Score bien-être semaine précédente
             if not df_semaine_prec.empty:
                moyennes_prec = df_semaine_prec[colonnes_parametres].mean()
                score_bien_etre_prec = (
                    moyennes_prec["Sommeil"] +
                    moyennes_prec["Dynamisme"] +
                    (10 - moyennes_prec["Stress"]) +
                    (10 - moyennes_prec["Fatigue"])
                ) / 4
             else:
                score_bien_etre_prec = None

             if prefs["show_weekly_score_bien_coach"] and score_bien_etre is not None:
              valeurs = [score_bien_etre]
              labels = ['Semaine en cours']

              if score_bien_etre_prec is not None:
                valeurs.append(score_bien_etre_prec)
                labels.append('Semaine précédente')

            # Couleurs : foncé pour actuelle, clair pour précédente
              couleurs = ['rgba(0, 0, 0, 0.9)']
              if score_bien_etre_prec is not None:
                couleurs.append('rgba(0, 0, 0, 0.4)')

            # Jauge Plotly horizontale
              fig_jauge = go.Figure()

              fig_jauge.add_trace(go.Bar(
                x=[4, 3, 3],
                y=['Score Bien-être']*3,
                orientation='h',
                marker=dict(color=[
                    'rgba(215, 72, 47, 0.3)',    # Rouge
                    'rgba(249, 206, 105, 0.3)',  # Jaune
                    'rgba(15, 154, 75, 0.3)'     # Vert
                ]),
                showlegend=False,
                hoverinfo='none'
              ))

              fig_jauge.add_trace(go.Scatter(
                x=valeurs,
                y=['Score Bien-être'] * len(valeurs),
                mode='markers',
                marker=dict(color=couleurs, size=20),
                text=[f"{label}: {valeur:.2f}" for label, valeur in zip(labels, valeurs)],
                hoverinfo='text',
                showlegend=False
              ))

              fig_jauge.update_layout(
                xaxis=dict(range=[1, 10], title='Score (1 à 10)'),
                yaxis=dict(showticklabels=False),
                height=150,
                margin=dict(l=40, r=40, t=40, b=40),
                title="Score Bien-être (semaine en cours vs semaine précédente)",
                title_x=0.2,
              )

              st.plotly_chart(fig_jauge, use_container_width=True)

            # ------------------------------------ Comparaison avec la semaine précédente ---------------------------------------------
             if prefs["show_weekly_comp_coach"]:
                st.markdown("<h5>Par rapport à la semaine précédente :</h5>", unsafe_allow_html=True)
                
                if df_semaine_prec.empty:
                    st.info("Aucune donnée pour la semaine précédente.")
                else:     
                 for param in colonnes_parametres:
                    val_prec = moyennes_prec[param]
                    val_actuelle = moyennes[param]
                    variation = val_actuelle - val_prec

                    alerte = ""
                    if param in ["Stress", "Fatigue"]:
                        if variation > 1:
                            pastille = "🔺"
                            alerte = "⚠️ "
                        elif variation < -1:
                            pastille = "🔻"
                            alerte = "✅ "
                        else:
                            pastille = "➖"
                    else:
                        if variation > 1:
                            pastille = "🔺"
                            alerte = "✅ "
                        elif variation < -1:
                            pastille = "🔻"
                            alerte = "⚠️ "
                        else:
                            pastille = "➖"

                    st.write(f"**{alerte}{param}** : {val_prec:.2f} → {val_actuelle:.2f} {pastille}")

            # --------------------------------------------------------- Mois ----------------------------------------------------------
            st.subheader("📅Suivi mensuel")
            
            coach_username = st.session_state.get("username")
            prefs = get_preferences(coach_username)

            df_user["Date"] = pd.to_datetime(df_user["Date"], format="%d/%m/%Y")

            if df_user.empty:
                st.info("Aucune donnée enregistrée.")
                
            # Afficher graphiques du mois.
            else:
                # Extraire l'année et le mois de chaque date
                df_user["Année_Mois"] = df_user["Date"].dt.to_period("M")

                # Trier les périodes mois-année de façon décroissante
                mois_unique = sorted(df_user["Année_Mois"].unique(), reverse=True)

                # Convertir les périodes en chaînes lisibles pour l'utilisateur
                mois_str = [mois.strftime("%B %Y") for mois in mois_unique]  # ex: "Mars 2025"

                # Sélection dans la liste déroulante
                mois_selectionne_str = st.selectbox(
                    "Pour consulter un autre mois, sélectionne-le dans la liste déroulante :", mois_str
                )

                # Récupérer l'index sélectionné
                index_mois = mois_str.index(mois_selectionne_str)
                mois_selectionne = mois_unique[index_mois]

                # Filtrer le dataframe pour le mois sélectionné
                df_mois = df_user[df_user["Année_Mois"] == mois_selectionne]

                # Début et fin du mois sélectionné
                debut_mois = mois_selectionne.to_timestamp()
                fin_mois = (mois_selectionne + 1).to_timestamp() - timedelta(seconds=1)

                # Étendre la plage de dates pour inclure les semaines complètes
                df_mois_etendu = df_user[
                    (df_user["Date"] >= (debut_mois - timedelta(days=6))) &
                    (df_user["Date"] <= (fin_mois + timedelta(days=6)))
                ].copy()

        # Calcul du lundi de chaque semaine
                df_mois_etendu["Semaine_lundi"] = df_mois_etendu["Date"].apply(lambda d: d - timedelta(days=d.weekday()))
                semaines = sorted(df_mois_etendu["Semaine_lundi"].unique())

        # -------------------------------------------------- Graphique ligne intensité ------------------------------------------------
                if prefs["show_monthly_intensity_coach"] and not df_mois.empty:
                 df_mois_sorted = df_mois.sort_values(by="Date")

                 moyenne_intensite = df_mois_sorted["Intensite"].mean()

            # Définir les rectangles de couleur + ligne moyenne dans une liste shapes
                 shapes = [
            # Vert entre 1 et 4
                 dict(type="rect", xref="paper", yref="y", x0=0, x1=1, y0=1, y1=4,
                    fillcolor='rgba(15, 154, 75, 0.5)', opacity=0.2, layer="below", line_width=0),
            # Jaune entre 4 et 7
                 dict(type="rect", xref="paper", yref="y", x0=0, x1=1, y0=4, y1=7,
                    fillcolor='rgba(249, 206, 105, 0.5)', opacity=0.2, layer="below", line_width=0),
            # Rouge entre 7 et 10
                 dict(type="rect", xref="paper", yref="y", x0=0, x1=1, y0=7, y1=10,
                    fillcolor='rgba(215, 72, 47, 0.5)', opacity=0.2, layer="below", line_width=0),
            # Ligne moyenne en pointillés
                 dict(type="line", xref="paper", yref="y", x0=0, x1=1,
                    y0=moyenne_intensite, y1=moyenne_intensite,
                    line=dict(color='rgba(100, 100, 100, 0.9)', dash='dash', width=2))
                 ]

            # Annotation pour la moyenne
                 annotations = [dict(
                 xref="paper", yref="y",
                 x=0.01, y=moyenne_intensite,
                 text=f"Moyenne : {moyenne_intensite:.2f}",
                 showarrow=False,
                 font=dict(color='rgba(100, 100, 100, 0.9)'),
                 bgcolor='rgba(255,255,255,0.7)'
                 )]

                 fig = px.line(
                 df_mois_sorted,
                 x="Date",
                 y="Intensite",  
                 title=f"Intensité pour {mois_selectionne.strftime('%B %Y')}",
                 labels={"Date": "Date", "Intensite": "Intensité"},
                 color_discrete_sequence=['rgba(100,100,100,0.9)']
                 )

                 fig.update_layout(
                 title_x=0.4,
                 yaxis=dict(range=[1, 10]),
                 xaxis=dict(tickformat='%d/%m'),
                 shapes=shapes,
                 annotations=annotations
                 )

                 fig.update_traces(connectgaps=True)
                 st.plotly_chart(fig)

        # ---------------------------------------------- Graphique ligne autres paramètres --------------------------------------------
                if prefs["show_monthly_parameter_coach"] and not df_mois.empty:
                        df_long = df_mois.melt(
                        id_vars=["Date"], 
                        value_vars=["Stress", "Fatigue", "Sommeil", "Dynamisme"], 
                        var_name="Mesures", 
                        value_name="Valeurs"
                        )

                        fig = px.line(
                            df_long,
                            x="Date",
                            y="Valeurs", 
                            color="Mesures" ,
                            title=f"Stress, Fatigue, Sommeil et Dynamisme pour {mois_selectionne.strftime('%B %Y')}",
                            labels={"Date": "Date", "Valeurs": "Valeurs"},
                            color_discrete_sequence=['rgba(255,0,0,0.6)',       # Stress
                            'rgba(255,165,0,0.6)',     # Fatigue
                            'rgba(0,128,0,0.6)',       # Sommeil
                            'rgba(0,0,255,0.6)']      # Dynamisme]
                        )

                        fig.update_layout(
                            title_x=0.25,               
                            yaxis=dict(range=[1, 10]),
                            xaxis=dict(
                            tickformat='%d/%m'),
                        )
                        st.plotly_chart(fig)
                        st.text("Tu peux cliquer sur les légendes pour masquer certaines variables.")
                        
                        # Calcul des moyennes mensuelles
                        moyennes = df_mois[["Stress", "Fatigue", "Sommeil", "Dynamisme"]].mean().round(2)

                        # Mise en forme en DataFrame pour affichage clair
                        df_moyennes = moyennes.reset_index()
                        df_moyennes.columns = ["Variable", "Moyenne"]

                        # Affichage du tableau
                        st.markdown("<h5>Moyennes mensuelles</h5>", unsafe_allow_html=True)

                        df_moyennes = moyennes.reset_index()
                        df_moyennes.columns = ["Variable", "Moyenne"]
                        df_moyennes.set_index("Variable", inplace=True)

                        styled_df = df_moyennes.style.apply(lambda x: style_moyennes(df_moyennes), axis=None)

                        st.dataframe(styled_df, use_container_width=True)

        # -------------------------------------------------- Graphique zscore ---------------------------------------------------------
                if prefs["show_monthly_zscore_coach"] and not df_mois.empty:
            # Calcul du Z-score par paramètre (colonne)
                 colonnes = ["Stress", "Fatigue", "Sommeil", "Dynamisme"]
                 df_zscore = df_mois.copy()
                # Calcul manuel du Z-score pour chaque colonne
                 for col in colonnes:
                    moyenne = df_mois[col].mean()
                    ecart_type = df_mois[col].std()
                    df_zscore[col] = (df_mois[col] - moyenne) / ecart_type

            # Transformation en format long pour tracé Plotly
                 df_long = df_zscore.melt(
                    id_vars=["Date"], 
                    value_vars=colonnes, 
                    var_name="Mesures", 
                    value_name="Z-score"
                 )

            # Graphique en ligne
                 fig = px.line(
                    df_long,
                    x="Date",
                    y="Z-score", 
                    color="Mesures",
                    title=f"Z-Score des paramètres pour {mois_selectionne.strftime('%B %Y')}",
                    labels={"Date": "Date", "Z-score": "Z-score"},
                    color_discrete_sequence=[
                    'rgba(255,0,0,0.6)',     # Stress
                    'rgba(255,165,0,0.6)',   # Fatigue
                    'rgba(0,128,0,0.6)',     # Sommeil
                    'rgba(0,0,255,0.6)'      # Dynamisme
                    ]
                 )

                 fig.update_layout(
                    title_x=0.25,
                    yaxis=dict(title="Z-Score", range=[-3, 3], zeroline=True),
                    xaxis=dict(tickformat='%d/%m'),
                    shapes=[
                        dict(
                        type="rect",
                        xref="paper",
                        yref="y",
                        x0=0,
                        x1=1,
                        y0=-2,
                        y1=2,
                        fillcolor="rgba(200, 200, 200, 0.2)",
                        layer="below",
                        line_width=0,
                        )
                    ]
                 )

                 st.plotly_chart(fig, use_container_width=True)
                 st.text("Tu peux cliquer sur les légendes pour masquer certaines variables.")

        # --------------------------------------------- Graphique baton score bien etre -----------------------------------------------
                if prefs["show_monthly_score_bien_coach"] and not df_mois.empty:
                    
                    # Calcul score bien-être moyen mensuel
                    moyennes_mensuelles = df_mois_etendu[["Sommeil", "Dynamisme", "Stress", "Fatigue"]].mean()
                    score_bien_etre_moyen_mois = (
                            moyennes_mensuelles["Sommeil"] + 
                            moyennes_mensuelles["Dynamisme"] + 
                            (10 - moyennes_mensuelles["Stress"]) + 
                            (10 - moyennes_mensuelles["Fatigue"])) / 4
                    
                    # Calcul du lundi de chaque date pour regrouper par semaine
                    df_mois_etendu["Semaine_lundi"] = df_mois_etendu["Date"].apply(lambda d: d - timedelta(days=d.weekday()))
                    semaines = sorted(df_mois_etendu["Semaine_lundi"].unique())

                    scores = []
                    labels = []

                    for semaine in semaines:
                        debut_semaine = semaine
                        fin_semaine = semaine + timedelta(days=6)
                        df_semaine = df_mois_etendu[(df_mois_etendu["Date"] >= debut_semaine) & (df_mois_etendu["Date"] <= fin_semaine)]
                        # Conserver uniquement les semaines qui touchent le mois sélectionné
                        if fin_semaine >= debut_mois and debut_semaine <= fin_mois:

                         if not df_semaine.empty:
                            moyennes = df_semaine[["Sommeil", "Dynamisme", "Stress", "Fatigue"]].mean()
                            score = (moyennes["Sommeil"] + moyennes["Dynamisme"] + (10 - moyennes["Stress"]) + (10 - moyennes["Fatigue"])) / 4
                            scores.append(score)
                            labels.append(f"Semaine du {debut_semaine.strftime('%d/%m')}")
                         else:
                            scores.append(None)
                            labels.append(f"Semaine du {debut_semaine.strftime('%d/%m')}")

                    colors = []
                    for score in scores:
                        if score is None:
                            colors.append('rgba(200,200,200,0.3)')  # gris clair pour les valeurs manquantes
                        elif score < 4:
                            colors.append('rgba(215, 72, 47, 0.8)')  # rouge
                        elif score < 7:
                            colors.append('rgba(249, 206, 105, 0.8)')  # jaune
                        else:
                            colors.append('rgba(15, 154, 75, 0.8)')  # vert


                    fig_bar = go.Figure(go.Bar(
                        x=labels,
                        y=scores,
                        marker_color=colors
                    ))

                    fig_bar.update_layout(
                        title=dict(text=f"Score Bien-être moyen par semaine - {mois_selectionne.strftime('%B %Y')}", x=0.5, xanchor='center'),
                        xaxis_title="Semaine",
                        yaxis_title="Score Bien-être",
                        yaxis=dict(range=[0, 10]),
                        margin=dict(t=50, b=100),
                        height=400
                    )

                    fig_bar.add_hline(
                        y=score_bien_etre_moyen_mois,
                        line_dash="dash",
                        line_color='rgba(100, 100, 100, 0.9)',
                        annotation_text=f"Moyenne mensuelle : {score_bien_etre_moyen_mois:.2f}",
                        annotation_position="top left",
                        annotation_font_color='rgba(100, 100, 100, 0.9)'
                    )

                    st.plotly_chart(fig_bar, use_container_width=True)
                
        # ----------------------------------------- Comparaison avec le mois précédent ------------------------------------------------
                index_mois_prec = index_mois + 1  # +1 car mois_unique est trié décroissant

                if index_mois_prec < len(mois_unique):
                    mois_precedent = mois_unique[index_mois_prec]
                    df_mois_prec = df_user[df_user["Année_Mois"] == mois_precedent]
                else:
                    df_mois_prec = pd.DataFrame()  # vide si pas de mois précédent

                colonnes_parametres = ["Stress", "Fatigue", "Sommeil", "Dynamisme"]

                if not df_mois.empty:
                    moyennes = df_mois[colonnes_parametres].mean()
                else:
                    moyennes = pd.Series([None]*len(colonnes_parametres), index=colonnes_parametres)

                if not df_mois_prec.empty:
                    moyennes_prec = df_mois_prec[colonnes_parametres].mean()
                else:
                    moyennes_prec = pd.Series([None]*len(colonnes_parametres), index=colonnes_parametres)

                if prefs["show_monthly_comp_coach"]:
                 st.markdown("<h5>Par rapport au mois précédent :</h5>", unsafe_allow_html=True)

                 if df_mois_prec.empty:
                    st.info("Aucune donnée pour le mois précédent.")
                 else:
                    for param in colonnes_parametres:
                        val_prec = moyennes_prec[param]
                        val_actuelle = moyennes[param]
                        variation = val_actuelle - val_prec
                
                        alerte = "" 

                        # Détection de la variation (positive, négative, neutre)
                        if param in ["Stress", "Fatigue"]:
                            if variation > 1:
                                pastille = "🔺"   # augmentation = négatif  
                                alerte = "⚠️ "
                            elif variation < -1:
                                pastille = "🔻"  # diminution = positif
                                alerte = "✅ "
                            else:
                                pastille = "➖"  # stable
                        else:  # Sommeil, Dynamisme
                            if variation > 1:
                             pastille = "🔺" 
                             alerte = "✅ " 
                            elif variation < -1:
                             pastille = "🔻" 
                             alerte = "⚠️ " 
                            else:
                             pastille = "➖"

                        st.write(f"**{alerte}{param}** : {val_prec:.2f} → {val_actuelle:.2f} {pastille}")

            # ------------------------------------------------------- Synthèse ---------------------------------------------------------
            st.subheader("📊Synthèse")

            df_user = load_responses(nom=joueur_selectionne)
            prefs = get_preferences(coach_username)
            
            if df_user.empty:
                    st.info("Aucune donnée enregistrée.")
                    
            # Afficher graphiques synthèse.        
            else:
             dates_disponibles = sorted(
                        df_user["Date"].unique(),
                        key=lambda d: datetime.strptime(d, "%d/%m/%Y"),
                        reverse=True
                    )
             df_user['Date'] = pd.to_datetime(df_user['Date'], format="%d/%m/%Y")

                    # Trier les dates uniques
             dates = sorted(df_user['Date'].dt.date.unique())

                    # Formatter les dates pour affichage (jj/mm/aaaa)
             formatted_dates = [d.strftime("%d/%m/%Y") for d in dates]
             format_to_date = {d.strftime("%d/%m/%Y"): d for d in dates}

             if len(formatted_dates) < 2:
                    st.warning("Pas assez de données pour sélectionner une plage de dates.")
                    st.dataframe(df_user.reset_index(drop=True))
             else:
                    start_fmt, end_fmt = st.select_slider(
                        "Sélectionne la plage de dates",
                        options=formatted_dates,
                        value=(formatted_dates[0], formatted_dates[-1])
                    )

                    start_date = format_to_date[start_fmt]
                    end_date = format_to_date[end_fmt]

                    mask = (df_user['Date'].dt.date >= start_date) & (df_user['Date'].dt.date <= end_date)
                    df_filtered = df_user.loc[mask]

        # ------------------------------------------------- Graphique intensité --------------------------------------------------------
             if prefs["show_global_intensity_coach"] and not df_filtered.empty:
              df_filtered_sorted = df_filtered.sort_values(by="Date")

              fig = px.line(
                df_filtered_sorted,
                x="Date",
                y="Intensite",  
                title=f"Intensité entre {start_date.strftime('%d/%m/%Y')} et {end_date.strftime('%d/%m/%Y')}",
                labels={"Date": "Date", "Intensite": "Intensité"},
                color_discrete_sequence=['rgba(100,100,100,0.9)']
              )

        

            # Générer des bandes verticales à partir de la vraie première date
              shapes = []
              dates = df_filtered_sorted["Date"].dt.floor("D").unique()
              min_date = min(dates)
              max_date = max(dates)

              current = min_date
              toggle = True
              while current < max_date:
                next_cut = current + timedelta(days=7)
                shapes.append(dict(
                    type="rect",
                    xref="x", yref="paper",
                    x0=current, x1=min(next_cut, max_date),  
                    y0=0, y1=1,
                    fillcolor='rgba(180, 180, 180, 0.2)' if toggle else 'rgba(120, 120, 120, 0.2)',
                    line_width=0,
                    layer="below"
                ))
                current = next_cut
                toggle = not toggle

            # Calcul de la moyenne d'intensité
              moyenne_intensite = df_filtered_sorted["Intensite"].mean()

        # Ajouter la ligne de moyenne dans la liste des shapes
              shapes.append(dict(
                type="line",
                xref="paper", yref="y",
                x0=0, x1=1,
                y0=moyenne_intensite, y1=moyenne_intensite,
                line=dict(
                color='rgba(100, 100, 100, 0.9)',
                dash='dash',
                width=2
                )
              ))

        # Ajouter l'annotation de la ligne
              annotations = [dict(
                xref="paper", yref="y",
                x=0.01, y=moyenne_intensite,
                text=f"Moyenne : {moyenne_intensite:.2f}",
                showarrow=False,
                font=dict(color='rgba(100, 100, 100, 0.9)'),
                bgcolor='rgba(255,255,255,0.7)'
              )]

              fig.update_layout(
               title_x=0.25,
               yaxis=dict(range=[1, 10]),
               xaxis=dict(tickformat='%d/%m'),
               shapes=shapes,
               annotations=annotations
              )
 
              fig.update_traces(connectgaps=True)
              st.plotly_chart(fig)

        # --------------------------------------------- Graphique autres paramètres ----------------------------------------------------
             if prefs["show_global_parameter_coach"] and not df_filtered.empty:
            # Réorganisation des données pour un graphique long format
              df_long = df_filtered.melt(
                id_vars=["Date"], 
                value_vars=["Stress", "Fatigue", "Sommeil", "Dynamisme"], 
                var_name="Mesures", 
                value_name="Valeurs"
              )
              df_long = df_long.sort_values(by="Date")

            # Création du graphique
              fig = px.line(
                df_long,
                x="Date",
                y="Valeurs", 
                color="Mesures",
                title=f"Stress, Fatigue, Sommeil et Dynamisme du {start_date.strftime('%d/%m/%Y')} au {end_date.strftime('%d/%m/%Y')}",
                labels={"Date": "Date", "Valeurs": "Valeurs"},
                color_discrete_sequence=[
                    'rgba(255,0,0,0.6)',       # Stress
                    'rgba(255,165,0,0.6)',     # Fatigue
                    'rgba(0,128,0,0.6)',       # Sommeil
                    'rgba(0,0,255,0.6)'        # Dynamisme
                ]
              )

              fig.update_layout(
                title_x=0.17,
                yaxis=dict(range=[1, 10]),
                xaxis=dict(tickformat='%d/%m'),
              )

              st.plotly_chart(fig)
              st.text("Tu peux cliquer sur les légendes pour masquer certaines variables.")

            # Calcul des moyennes sur la plage sélectionnée
              moyennes = df_filtered[["Stress", "Fatigue", "Sommeil", "Dynamisme"]].mean().round(2)

            # Mise en forme pour affichage
              df_moyennes = moyennes.reset_index()
              df_moyennes.columns = ["Variable", "Moyenne"]

              st.markdown("<h5>Moyennes sur la période sélectionnée</h5>", unsafe_allow_html=True)

        # Supposons que df_moyennes est calculé sur la période sélectionnée et a les colonnes Variable et Moyenne
              df_moyennes.set_index("Variable", inplace=True)

        # Appliquer le style avec la fonction que tu as définie
              styled_df = df_moyennes.style.apply(lambda x: style_moyennes(df_moyennes), axis=None)

              st.dataframe(styled_df, use_container_width=True)

        # ---------------------------------------------------- Graphique z-score -------------------------------------------------------
             if prefs["show_global_zscore_coach"] and not df_filtered.empty:
            # Calcul du Z-score sur les données filtrées par le slider
              colonnes = ["Stress", "Fatigue", "Sommeil", "Dynamisme"]
              df_zscore = df_filtered.copy()

            # Calcul manuel du Z-score pour chaque paramètre
              for col in colonnes:
                moyenne = df_filtered[col].mean()
                ecart_type = df_filtered[col].std()
                df_zscore[col] = (df_filtered[col] - moyenne) / ecart_type

            # Transformation en format long pour tracé Plotly
              df_long = df_zscore.melt(
                id_vars=["Date"], 
                value_vars=colonnes, 
                var_name="Mesures", 
                value_name="Z-score"
              )

              df_long = df_long.sort_values(by="Date")

            # Graphique en ligne
              fig = px.line(
                df_long,
                x="Date",
                y="Z-score", 
                color="Mesures",
                title=f"Z-Score des paramètres du {start_date.strftime('%d/%m/%Y')} au {end_date.strftime('%d/%m/%Y')}",
                labels={"Date": "Date", "Z-score": "Z-score"},
                color_discrete_sequence=[
                    'rgba(255,0,0,0.6)',     # Stress
                    'rgba(255,165,0,0.6)',   # Fatigue
                    'rgba(0,128,0,0.6)',     # Sommeil
                    'rgba(0,0,255,0.6)'      # Dynamisme
                ]
              )

            # Supprimer les points et ajuster les axes
              for trace in fig.data:
                trace.mode = "lines"

              fig.update_layout(
                title_x=0.23,
                yaxis=dict(title="Z-Score", range=[-3, 3], zeroline=True),
                xaxis=dict(tickformat='%d/%m'),
                shapes=[
                    dict(
                        type="rect",
                        xref="paper",
                        yref="y",
                        x0=0,
                        x1=1,
                        y0=-2,
                        y1=2,
                        fillcolor="rgba(200, 200, 200, 0.2)",
                        layer="below",
                        line_width=0,
                    )
                ]
              )

              st.plotly_chart(fig, use_container_width=True)
              st.text("Tu peux cliquer sur les légendes pour masquer certaines variables.")

        # ----------------------------------------------- Graphique score bien etre ----------------------------------------------------
             if prefs["show_global_score_bien_coach"] and not df_filtered.empty:
            # Calcul du score bien-être ligne par ligne
              df_filtered = df_filtered.copy()
              df_filtered["Score bien-être"] = (
                df_filtered["Sommeil"] +
                df_filtered["Dynamisme"] +
                (10 - df_filtered["Stress"]) +
                (10 - df_filtered["Fatigue"])
              ) / 4

            # Tri par date
              df_filtered = df_filtered.sort_values(by="Date")

            # Calcul de la moyenne du score bien-être
              moyenne_score = df_filtered["Score bien-être"].mean()

            # Préparation des zones colorées + ligne moyenne
              shapes = [
                # rouge entre 1 et 4
                dict(type="rect", xref="paper", yref="y", x0=0, x1=1, y0=1, y1=4,
                    fillcolor='rgba(215, 72, 47, 0.5)', opacity=0.2, layer="below", line_width=0),
                # jaune entre 4 et 7
                dict(type="rect", xref="paper", yref="y", x0=0, x1=1, y0=4, y1=7,
                    fillcolor='rgba(249, 206, 105, 0.5)', opacity=0.2, layer="below", line_width=0),
                # vert entre 7 et 10
                dict(type="rect", xref="paper", yref="y", x0=0, x1=1, y0=7, y1=10,
                    fillcolor='rgba(15, 154, 75, 0.5)', opacity=0.2, layer="below", line_width=0),
                # Ligne moyenne en pointillés
                dict(type="line", xref="paper", yref="y", x0=0, x1=1,
                    y0=moyenne_score, y1=moyenne_score,
                    line=dict(color='rgba(100, 100, 100, 0.9)', dash='dash', width=2))
              ]

            # Annotation pour la moyenne
              annotations = [dict(
                xref="paper", yref="y",
                x=0.01, y=moyenne_score,
                text=f"Moyenne : {moyenne_score:.2f}",
                showarrow=False,
                font=dict(color='rgba(100, 100, 100, 0.9)'),
                bgcolor='rgba(255,255,255,0.7)'
              )]

            # Création du graphique avec le même style que les autres
              fig = px.line(
                df_filtered,
                x="Date",
                y="Score bien-être",
                title=f"Score bien-être du {start_date.strftime('%d/%m/%Y')} au {end_date.strftime('%d/%m/%Y')}",
                labels={"Date": "Date", "Score bien-être": "Score bien-être"},
                markers=False,
                color_discrete_sequence=['rgba(100,100,100,0.9)']
              )

              fig.update_layout(
                title_x=0.3,
                yaxis=dict(range=[1, 10]),
                xaxis=dict(
                    tickformat='%d/%m',
                    range=[df_filtered["Date"].min(), df_filtered["Date"].max()]),
                shapes=shapes,
                annotations=annotations
              )

              st.plotly_chart(fig)

# =================================================== Compte rendu collectif coach =====================================================
elif page == "Compte rendu collectif":
    st.title("Compte rendu collectif")
    st.subheader("📍Suivi quotidien")

    username = st.session_state.get("username", "")
    df = load_responses() # ta DataFrame des réponses
    prefs = get_preferences(username)

    if not df.empty:
        club = st.session_state.get("club", "").strip().lower()

        df["Club"] = df["Club"].astype(str).str.strip().str.lower()

        # On filtre uniquement sur le club (pas sur role ici)
        df_club = df[df["Club"] == club]

        if df_club.empty:
            st.info("Aucune réponse pour ce club.")
        else:
            df_club["Date"] = pd.to_datetime(df_club["Date"], dayfirst=True, errors="coerce").dt.date
            dates_disponibles = sorted(df_club["Date"].dropna().unique())

            if len(dates_disponibles) > 0:
                min_date = min(dates_disponibles)
                max_date = max(dates_disponibles)

                date_selectionnee = st.date_input(
                    "Sélectionne une date :",
                    value=max_date,
                    format="DD/MM/YYYY"
                )

                if date_selectionnee not in dates_disponibles:
                    joueurs_club = load_club_players(club)
                    joueurs_repondu = []  # Aucun joueur n’a répondu
                    joueurs_non_repondu = joueurs_club  # Tous les joueurs n’ont pas répondu

                    st.markdown(f"**✅ Joueurs ayant répondu :** {len(joueurs_repondu)}")
                    with st.expander("Voir les joueurs ayant répondu"):
                       st.write("Aucun joueur n’a encore répondu pour cette date.")
        
                    st.markdown(f"**❌ Joueurs n'ayant pas répondu :** {len(joueurs_non_repondu)}")
                    with st.expander("Voir les joueurs n'ayant pas répondu"):
                      for joueur in joueurs_non_repondu:
                          st.write(f"- {joueur}")
                else:
                    df_date = df_club[df_club["Date"] == date_selectionnee]

                    joueurs_club = load_club_players(club)
                    joueurs_repondu = df_date["Nom"].dropna().unique().tolist()
                    joueurs_non_repondu = [j for j in joueurs_club if j not in joueurs_repondu]

                    st.markdown(f"**✅ Joueurs ayant répondu :** {len(joueurs_repondu)}")
                    with st.expander("Voir les joueurs ayant répondu"):
                        for joueur in joueurs_repondu:
                            st.write(f"- {joueur}")
                    
                    st.markdown(f"**❌ Joueurs n'ayant pas répondu :** {len(joueurs_non_repondu)}")
                    with st.expander("Voir les joueurs n'ayant pas répondu"):
                        for joueur in joueurs_non_repondu:
                            st.write(f"- {joueur}")
                    
                    if prefs["show_seance_team_coach"]:
                        if not df_date.empty:
                            data_moyenne = df_date[["Intensite", "Sommeil", "Fatigue", "Stress", "Dynamisme"]].mean()

                            def plot_gauge_in_col(col, title, value, inverse_colors=False):
                                if inverse_colors:
                                    steps = [
                                        {'range': [1, 4], 'color': 'rgba(15, 154, 75, 0.65)'},
                                        {'range': [4, 7], 'color': 'rgba(249, 206, 105, 0.69)'},
                                        {'range': [7, 10], 'color': 'rgba(215, 72, 47, 0.68)'}
                                    ]
                                else:
                                    steps = [
                                        {'range': [1, 4], 'color': 'rgba(215, 72, 47, 0.68)'},
                                        {'range': [4, 7], 'color': 'rgba(249, 206, 105, 0.69)'},
                                        {'range': [7, 10], 'color': 'rgba(15, 154, 75, 0.65)'}
                                    ]

                                fig = go.Figure(go.Indicator(
                                    mode="gauge+number",
                                    value=value,
                                    number={'font': {'size': 23, 'color': "#2a3f5f"}},
                                    title={'text': title, 'font': {'size': 18, 'color': "#2a3f5f"}},
                                    gauge={
                                        'axis': {'range': [1, 10], 'tickfont': {'size': 10}},
                                        'bar': {'color': 'rgba(0,0,0,0)', 'thickness': 0},
                                        'steps': steps,
                                        'threshold': {
                                            'line': {'color': "#2a3f5f", 'width': 5},
                                            'thickness': 1,
                                            'value': value
                                        }
                                    }
                                ))
                                fig.update_layout(height=200, margin=dict(l=20, r=20, t=30, b=0))
                                col.plotly_chart(fig, use_container_width=True)

                                # Affichage en deux lignes de 3 jauges
                            cols1 = st.columns(3)
                            cols2 = st.columns(3)

                            plot_gauge_in_col(cols1[0], "Intensité", data_moyenne["Intensite"], inverse_colors=True)
                            plot_gauge_in_col(cols1[1], "Sommeil", data_moyenne["Sommeil"])
                            plot_gauge_in_col(cols1[2], "Fatigue", data_moyenne["Fatigue"], inverse_colors=True)

                            plot_gauge_in_col(cols2[0], "Stress", data_moyenne["Stress"], inverse_colors=True)
                            plot_gauge_in_col(cols2[1], "Dynamisme", data_moyenne["Dynamisme"])

                        else:
                            st.info("Aucune donnée pour cette date.") 
                    
                    if prefs["show_team_intensity_coach"]:
                     if "Intensite" in df_date.columns:
                        intensites = df_date[["Nom", "Intensite"]].dropna()

                        if not intensites.empty:
                            moyenne = intensites["Intensite"].mean()

                            def couleur_intensite(val):
                                if pd.isna(val):
                                    return 'grey'
                                elif val < 4:
                                    return 'green'
                                elif val < 7:
                                    return 'yellow'
                                else:
                                    return 'red'

                            intensites["Couleur"] = intensites["Intensite"].apply(couleur_intensite)

                            fig = px.bar(
                                intensites,
                                x="Nom",
                                y="Intensite",
                                color="Couleur",
                                color_discrete_map={
                                    'green': 'rgba(15, 154, 75, 0.8)',
                                    'yellow': 'rgba(249, 206, 105, 0.8)',
                                    'red': 'rgba(215, 72, 47, 0.8)',
                                    'grey': 'lightgrey'
                                },
                                labels={"Nom": "Joueur", "Intensite": "Intensité"},
                                title=f"Intensité des joueurs le {date_selectionnee.strftime('%d/%m/%Y')}"
                            )

                            fig.update_layout(
                                title_x=0.33,
                                yaxis_title="Intensité",
                                xaxis_title="Joueur",
                                showlegend=False,
                                yaxis_range=[0, 10]
                            )

                            fig.add_hline(
                                y=moyenne,
                                line_dash="dash",
                                line_color='rgba(100,100,100,0.9)',
                                annotation_text=f"Moyenne : {moyenne:.1f}",
                                annotation_position="top left",
                                annotation_font_color='rgba(100,100,100,0.9)'
                            )

                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("Aucune donnée d'intensité pour cette date.")
                     else:
                        st.warning("La colonne 'Intensite' n'existe pas dans les données.")

                    # Choix des paramètres pour le cadran
                    if prefs["show_cadran"]:
                     st.write("Sélection des paramètres du graphique cadran :")
                     parametres_possibles = ["Dynamisme", "Fatigue", "Sommeil", "Stress"]

                     colx, coly = st.columns(2)
                     param_x = colx.selectbox("Axe X", parametres_possibles, index=parametres_possibles.index("Dynamisme"))
                     param_y = coly.selectbox("Axe Y", parametres_possibles, index=parametres_possibles.index("Fatigue"))


                     if param_x == param_y:
                        st.warning("⚠️ Veuillez sélectionner deux paramètres différents pour les axes X et Y.")
                     else:
                        # Vérifie que les colonnes sont dans le DataFrame
                        if param_x in df_date.columns and param_y in df_date.columns:
                             df_scatter = df_date[["Nom", param_x, param_y]].dropna()

                             if not df_scatter.empty:
                                # Moyennes des deux axes
                                moyenne_x = df_scatter[param_x].mean()
                                moyenne_y = df_scatter[param_y].mean()
                                
                                # Choisir les couleurs des zones du cadran
                                colors = cadran_colors.get((param_x, param_y), {
                                  "bottom_left": "rgba(240,240,240,0.2)",
                                  "bottom_right": "rgba(240,240,240,0.2)",
                                  "top_left": "rgba(240,240,240,0.2)",
                                  "top_right": "rgba(240,240,240,0.2)",
                                })

                                fig_scatter = px.scatter(
                                    df_scatter,
                                    x=param_x,
                                    y=param_y,
                                    text="Nom",
                                    title=f"{param_y} en fonction de {param_x} ({date_selectionnee.strftime('%d/%m/%Y')})",
                                    labels={param_x: param_x, param_y: param_y},
                                )

                                # Zone en bas à gauche
                                fig_scatter.add_shape(type="rect",
                                  x0=1, x1=moyenne_x,
                                  y0=1, y1=moyenne_y,
                                  fillcolor=colors["bottom_left"], line=dict(width=0))

                                # Bas à droite
                                fig_scatter.add_shape(type="rect",
                                   x0=moyenne_x, x1=10,
                                   y0=1, y1=moyenne_y,
                                   fillcolor=colors["bottom_right"], line=dict(width=0))
                                
                                # Haut à gauche
                                fig_scatter.add_shape(type="rect",
                                     x0=1, x1=moyenne_x,
                                     y0=moyenne_y, y1=10,
                                     fillcolor=colors["top_left"], line=dict(width=0))

                                # Haut à droite
                                fig_scatter.add_shape(type="rect",
                                     x0=moyenne_x, x1=10,
                                     y0=moyenne_y, y1=10,
                                     fillcolor=colors["top_right"], line=dict(width=0))
                                
                                fig_scatter.update_traces(textposition='top center', marker=dict(size=12, opacity=0.8))

                                # Ajouter les lignes des moyennes pour créer un cadran
                                fig_scatter.add_shape(
                                      type="line",
                                      x0=moyenne_x, x1=moyenne_x,
                                      y0=1, y1=10,
                                      line=dict(color="gray", width=2, dash="dash")
                                )
                                fig_scatter.add_shape(
                                      type="line",
                                      x0=1, x1=10,
                                      y0=moyenne_y, y1=moyenne_y,
                                      line=dict(color="gray", width=2, dash="dash")
                                )

                                fig_scatter.update_layout(
                                     title_x=0.3,
                                     xaxis=dict(range=[1, 10]),
                                     yaxis=dict(range=[1, 10]),
                                     height=500
                                )

                                st.plotly_chart(fig_scatter, use_container_width=True)
                             else:
                                 st.info("Pas de données disponibles pour afficher ce graphique.")
                        else:
                             st.warning("Les paramètres sélectionnés ne sont pas disponibles.")
                        
                    # Vérifie que toutes les colonnes nécessaires sont présentes
                    if prefs["show_team_bien_etre_coach"]:
                     cols_bien_etre = ["Nom", "Sommeil", "Dynamisme", "Fatigue", "Stress"]
                     if all(col in df_date.columns for col in cols_bien_etre):
                        df_bien_etre = df_date[cols_bien_etre].dropna()

                        if not df_bien_etre.empty:
                            # Calcul du score bien-être
                            df_bien_etre["ScoreBienEtre"] = (
                                df_bien_etre["Sommeil"] +
                                df_bien_etre["Dynamisme"] +
                                (10 - df_bien_etre["Fatigue"]) +
                                (10 - df_bien_etre["Stress"])
                            ) / 4

                            moyenne_bien_etre = df_bien_etre["ScoreBienEtre"].mean()

                            def couleur_score(val):
                                if val < 4:
                                    return 'red'
                                elif val < 7:
                                    return 'yellow'
                                else:
                                    return 'green'

                            df_bien_etre["Couleur"] = df_bien_etre["ScoreBienEtre"].apply(couleur_score)

                            fig_bien_etre = px.bar(
                                df_bien_etre,
                                x="Nom",
                                y="ScoreBienEtre",
                                color="Couleur",
                                color_discrete_map={
                                    'green': 'rgba(15, 154, 75, 0.8)',
                                    'yellow': 'rgba(249, 206, 105, 0.8)',
                                    'red': 'rgba(215, 72, 47, 0.8)'
                                },
                                labels={"Nom": "Joueur", "ScoreBienEtre": "Score bien-être"},
                                title=f"Score bien-être des joueurs le {date_selectionnee.strftime('%d/%m/%Y')}"
                            )

                            fig_bien_etre.update_layout(
                                title_x=0.3,
                                yaxis_title="Score bien-être",
                                xaxis_title="Joueur",
                                showlegend=False,
                                yaxis_range=[0, 10]
                            )

                            fig_bien_etre.add_hline(
                                y=moyenne_bien_etre,
                                line_dash="dash",
                                line_color='rgba(100,100,100,0.9)',
                                annotation_text=f"Moyenne : {moyenne_bien_etre:.1f}",
                                annotation_position="top left",
                                annotation_font_color='rgba(100,100,100,0.9)'
                            )

                            st.plotly_chart(fig_bien_etre, use_container_width=True)
                        else:
                            st.info("Aucune donnée suffisante pour calculer le score bien-être.")
                     else:
                        st.warning("Certaines colonnes nécessaires pour le score bien-être sont manquantes.")
                        
                    # 🔎 Filtrer les joueurs ayant répondu "Oui" à la colonne Douleurs
                    if prefs["show_team_douleurs_coach"]:
                     joueurs_douleurs = df_date[df_date["Douleurs"].str.lower() == "oui"]

                     if not joueurs_douleurs.empty:
                      st.subheader("🤕 Douleurs signalées")

                      for _, row in joueurs_douleurs.iterrows():
                       nom = row["Nom"]
                       description = row.get("DescriptionDouleurs", "").strip()
                       if description:
                           st.markdown(f"**{nom}** : {description}")
                       else:
                           st.markdown(f"**{nom}** : _(Pas de description fournie)_")
                     else:
                        st.info("Aucun joueur n’a signalé de douleurs pour cette date.")
    else :
        st.info("Aucune donnée enregistrée.")
 # --------------------------------------------------------Synthèse pour une période donnée (collectif) -------------------------------                           
    st.subheader("📊Synthèse sur une période donnée")
    # --- Selection de la plage de dates ---
    df_club = df[df["Club"] == club]  # Défini toujours

    if df_club.empty:
     st.info("Aucune donnée enregistrée.")
    else:
     df_club["Date"] = pd.to_datetime(df_club["Date"], format="%d/%m/%Y", errors="coerce")


     dates = sorted(df_club["Date"].dt.date.dropna().unique())

     formatted_dates = [d.strftime("%d/%m/%Y") for d in dates]
     format_to_date = {d.strftime("%d/%m/%Y"): d for d in dates}

     if len(formatted_dates) < 2:
                st.warning("Pas assez de données pour afficher les graphiques.")
     else:
                start_fmt, end_fmt = st.select_slider(
                    "Sélectionne la plage de dates",
                    options=formatted_dates,
                    value=(formatted_dates[0], formatted_dates[-1])
                )

                start_date = format_to_date[start_fmt]
                end_date = format_to_date[end_fmt]

                mask = (df_club['Date'].dt.date >= start_date) & (df_club['Date'].dt.date <= end_date)
                df_filtered = df_club.loc[mask]

                if df_filtered.empty:
                    st.warning("Aucune donnée disponible dans cette plage de dates.")
                else:
                    # --- Moyenne par joueur ---
                    df_avg = df_filtered.groupby("Nom")[["Intensite", "Sommeil", "Dynamisme", "Fatigue", "Stress"]].mean().reset_index()

                    df_avg["ScoreBienEtre"] = (
                        df_avg["Sommeil"] + df_avg["Dynamisme"] + (10 - df_avg["Fatigue"]) + (10 - df_avg["Stress"])
                    ) / 4

                    # --- Graphique Intensité ---
                    if prefs["show_team_synthèse_intensity_coach"]:
                        if "Intensite" in df_filtered.columns:
        # Pivot table avec index joueurs, colonnes dates, valeurs intensité
                            df_pivot = df_filtered.pivot(index="Nom", columns="Date", values="Intensite")
                            df_pivot.columns = [d.strftime("%d/%m/%Y") for d in df_pivot.columns]

        # Prépare la matrice en remplaçant les NaN par une valeur hors échelle (ex: -1)
                            z = df_pivot.values.copy()
                            z_masked = np.where(np.isnan(z), -1, z)  # -1 pour les NaN

        # Définition du colorscale avec blanc pour -1 (NaN) et tes couleurs
                            colorscale = [
                                [0.0, "white"],  # Pour -1 (NaN)
                                [0.0001, "rgba(15, 154, 75, 0.5)"],   # Vert (bas)
                                [0.35, "rgba(15, 154, 75, 0.5)"],     # Fin du vert
                                [0.6, "rgba(249, 206, 105, 0.5)"],    # Jaune dominant
                                [0.8, "rgba(215, 72, 47, 0.5)"],      # Début du rouge
                                [1.0, "rgba(215, 72, 47, 0.5)"]       # Rouge (haut)
                            ]



                            fig = go.Figure(data=go.Heatmap(
                                z=z_masked,
                                x=df_pivot.columns,
                                y=df_pivot.index,
                                colorscale=colorscale,
                                zmin=-1,  # min à -1 pour inclure NaN coloré en blanc
                                zmax=10,
                                colorbar=dict(title="Intensité"),
                                hoverongaps=False
                            ))

                            fig.update_layout(
                                title=f"Heatmap de l'intensité du {start_fmt} au {end_fmt}",
                                title_x=0.3,
                                xaxis_title="Date",
                                yaxis_title="Joueur"
                            )
                            
                            fig.add_annotation(
                                text="⬜ = pas de séance",
                                xref="paper", yref="paper",
                                x=-0.1, y=-0.25,
                                showarrow=False,
                                font=dict(size=12),
                                align="left"
                            )


                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.warning("La colonne 'Intensite' n'existe pas dans les données.")

                    # --- Graphique Cadran ---
                    if prefs["show_cadran_synthèse"]:
                     st.write("Sélection des paramètres du graphique cadran :")
                     parametres_possibles = ["Dynamisme", "Fatigue", "Sommeil", "Stress"]
                     colx, coly = st.columns(2)
                     param_x = colx.selectbox("Axe X", parametres_possibles, index=parametres_possibles.index("Dynamisme"), key='param_x')
                     param_y = coly.selectbox("Axe Y", parametres_possibles, index=parametres_possibles.index("Fatigue"),key='param_y')

                     if param_x == param_y:
                        st.warning("⚠️ Veuillez sélectionner deux paramètres différents pour les axes X et Y.")
                     else:
                        moyenne_x = df_avg[param_x].mean()
                        moyenne_y = df_avg[param_y].mean()

                        colors = cadran_colors.get((param_x, param_y), {
                            "bottom_left": "rgba(240,240,240,0.2)",
                            "bottom_right": "rgba(240,240,240,0.2)",
                            "top_left": "rgba(240,240,240,0.2)",
                            "top_right": "rgba(240,240,240,0.2)",
                        })

                        fig_scatter = px.scatter(
                            df_avg, x=param_x, y=param_y, text="Nom",
                            title=f"{param_y} vs {param_x} ({start_fmt} au {end_fmt})"
                        )
                        fig_scatter.update_traces(textposition='top center', marker=dict(size=12, opacity=0.8))

                        fig_scatter.add_shape(type="rect", x0=1, x1=moyenne_x, y0=1, y1=moyenne_y, fillcolor=colors["bottom_left"], line=dict(width=0))
                        fig_scatter.add_shape(type="rect", x0=moyenne_x, x1=10, y0=1, y1=moyenne_y, fillcolor=colors["bottom_right"], line=dict(width=0))
                        fig_scatter.add_shape(type="rect", x0=1, x1=moyenne_x, y0=moyenne_y, y1=10, fillcolor=colors["top_left"], line=dict(width=0))
                        fig_scatter.add_shape(type="rect", x0=moyenne_x, x1=10, y0=moyenne_y, y1=10, fillcolor=colors["top_right"], line=dict(width=0))

                        fig_scatter.add_shape(type="line", x0=moyenne_x, x1=moyenne_x, y0=1, y1=10, line=dict(color="gray", width=2, dash="dash"))
                        fig_scatter.add_shape(type="line", x0=1, x1=10, y0=moyenne_y, y1=moyenne_y, line=dict(color="gray", width=2, dash="dash"))

                        fig_scatter.update_layout(title_x=0.3, xaxis_range=[1, 10], yaxis_range=[1, 10], height=500)
                        st.plotly_chart(fig_scatter, use_container_width=True)

                    # --- Score bien-être ---
                    if prefs["show_team_synthèse_bien_etre_coach"]:
                     moyenne_bien_etre = df_avg["ScoreBienEtre"].mean()

                     def couleur_score(val):
                        if val < 4: return 'red'
                        elif val < 7: return 'yellow'
                        else: return 'green'

                     df_avg["CouleurBE"] = df_avg["ScoreBienEtre"].apply(couleur_score)

                     fig_be = px.bar(
                        df_avg,
                        x="Nom",
                        y="ScoreBienEtre",
                        color="CouleurBE",
                        color_discrete_map={
                            'green': 'rgba(15, 154, 75, 0.8)',
                            'yellow': 'rgba(249, 206, 105, 0.8)',
                            'red': 'rgba(215, 72, 47, 0.8)'
                        },
                        title=f"Score bien-être moyen du {start_fmt} au {end_fmt}"
                     )

                     fig_be.update_layout(title_x=0.3, yaxis_range=[0, 10], showlegend=False)
                     fig_be.add_hline(y=moyenne_bien_etre, line_dash="dash", annotation_text=f"Moyenne : {moyenne_bien_etre:.1f}")
                     st.plotly_chart(fig_be, use_container_width=True)
                    
# ========================================================== Page données brutes =======================================================
elif page == "Données brutes":
    st.title("Données brutes")

    df = load_responses()

    if not df.empty:
        # Nettoyage : doublons sur Nom + Date
        df = df.drop_duplicates(subset=["Nom", "Date"], keep="last").reset_index(drop=True)

        # Filtrage par club
        club = st.session_state.get("club", "").strip().lower()
        df["Club"] = df["Club"].astype(str).str.strip().str.lower()
        df = df[df["Club"] == club]

        st.dataframe(df)
                
        # Bouton d'export CSV
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Exporter les données en CSV",
            data=csv,
            file_name=f'donnees_{club}.csv',
            mime='text/csv'
        )

        st.subheader("🗑️ Supprimer une réponse")

        st.markdown("""
         Utilise cet outil pour supprimer une réponse.
         
         ---

         ✅ **Pas besoin de supprimer** si un joueur a simplement fait une erreur dans ses réponses :  
          il peut **re-remplir le questionnaire pour la même date**, sa réponse sera **automatiquement mise à jour**.

         ❌ Utilise cet outil **seulement si le joueur s'est trompé de date** en répondant au questionnaire.

         """)

        if not df.empty:
            lignes = [f"{i} - {row['Nom']} - {row['Date']}" for i, row in df.iterrows()]
            ligne_a_supprimer = st.selectbox("👉 Sélectionne la ligne à supprimer, puis clique sur le bouton pour confirmer.", lignes)

            if st.button("Supprimer la ligne sélectionnée"):
                index = int(ligne_a_supprimer.split(" ")[0])
                ligne = df.iloc[index]
                supprimer_reponse(ligne["Nom"], ligne["Date"])
                st.success(f"Ligne supprimée : {ligne['Nom']} - {ligne['Date']}")
                st.rerun()
    else:
        st.info("Aucune donnée enregistrée.")

# ============================================================= Page réglages ==========================================================
elif page == "Réglages":
    nom = st.session_state.get("username", "")

    prefs = get_preferences(nom)

    username = st.session_state.get("username")
    role = USERS[username]["role"]

# Page réglage joueur.
    if role == "player":
     st.subheader("⚙️ Réglages d’affichage")   
     with st.form("form_prefs"):
        st.write("Coche les éléments que tu veux afficher sur ta page compte rendu individuel et enregistres :")

        # Quotidien
        st.markdown("#### 📍Suivi quotidien")
        updated_prefs = {
            "show_seance": st.checkbox("Graphique quotidien - Intensité/Stress/Fatigue/Sommeil/Dynamisme", prefs["show_seance"]),
        }

        # Hebdomadaire
        st.markdown("#### 📆Suivi hebdomadaire")
        updated_prefs.update({
            "show_weekly_intensity": st.checkbox("Graphique semaine - Intensité ", prefs["show_weekly_intensity"]),
            "show_weekly_parameter": st.checkbox("Graphique semaine - Stress/Fatigue/Sommeil/Dynamisme", prefs["show_weekly_parameter"]),
            "show_weekly_score_bien": st.checkbox("Graphique semaine - Score bien-être", prefs["show_weekly_score_bien"]),
            "show_weekly_comp": st.checkbox("Comparaison semaine précédente", prefs["show_weekly_comp"]),
        })

        # Mensuel
        st.markdown("#### 📅Suivi mensuel")
        updated_prefs.update({
            "show_monthly_intensity": st.checkbox("Graphique mois - Intensité", prefs["show_monthly_intensity"]),
            "show_monthly_parameter": st.checkbox("Graphique mois - Stress/Fatigue/Sommeil/Dynamisme", prefs["show_monthly_parameter"]),
            "show_monthly_zscore": st.checkbox("Graphique mois - Z-Score", prefs["show_monthly_zscore"]),
            "show_monthly_score_bien":st.checkbox("Graphique mois - Score bien-être", prefs["show_monthly_score_bien"]),
            "show_monthly_comp": st.checkbox("Comparaison mois précédent", prefs["show_monthly_comp"]),
        })

        # Synthèse
        st.markdown("#### 📊Synthèse")
        updated_prefs.update({
            "show_global_intensity": st.checkbox("Graphique général - Intensité", prefs["show_global_intensity"]),
            "show_global_parameter": st.checkbox("Graphique général - Stress/Fatigue/Sommeil/Dynamisme", prefs["show_global_parameter"]),
            "show_global_zscore": st.checkbox("Graphique général - Z-Score", prefs["show_global_zscore"]),
            "show_global_score_bien": st.checkbox("Graphique général - Score bien-être", prefs["show_global_score_bien"]),
        })

        submitted = st.form_submit_button("Enregistrer")
        if submitted:
            save_preferences(username, updated_prefs)
            st.success("Préférences mises à jour.")
     
# Page réglage coach.            
    if role == "coach":
     st.subheader("⚙️ Réglages de fréquence des réponses")

     with st.form("form_frequence"):
        frequence_options = ["Tous les jours", "Seulement les jours de séance ou de match"]
        current_freq = prefs.get("mode_questionnaire", "Tous les jours")
        default_index = frequence_options.index(current_freq) if current_freq in frequence_options else 0

        frequence_questionnaire = st.radio(
            "À quelle fréquence les joueurs doivent-ils répondre au questionnaire ?",
            frequence_options,
            index=default_index
        )
        submitted_freq = st.form_submit_button("Enregistrer")
        if submitted_freq:
            save_preferences_2(username, frequence_questionnaire)
            st.session_state["mode_questionnaire"] = frequence_questionnaire
            st.success("Préférence enregistrée ✅")
       
     st.subheader("⚙️ Réglages d’affichage")
     with st.form("form_prefs"):
        st.subheader("Page compte rendu individuel")
        st.write("Coche les éléments que tu veux afficher sur ta page compte rendu individuel et enregistres :")

        # Quotidien 
        st.markdown("#### 📍Suivi quotidien")
        updated_prefs = {
            "show_seance_coach": st.checkbox("Graphique quotidien - Intensité/Stress/Fatigue/Sommeil/Dynamisme", prefs["show_seance_coach"]),
        }

        # Hebdomadaire
        st.markdown("#### 📆Suivi hebdomadaire")
        updated_prefs.update({
            "show_weekly_intensity_coach": st.checkbox("Graphique semaine - Intensité ", prefs["show_weekly_intensity_coach"]),
            "show_weekly_parameter_coach": st.checkbox("Graphique semaine - Stress/Fatigue/Sommeil/Dynamisme", prefs["show_weekly_parameter_coach"]),
            "show_weekly_score_bien_coach": st.checkbox("Graphique semaine - Score bien-être", prefs["show_weekly_score_bien_coach"]),
            "show_weekly_comp_coach": st.checkbox("Comparaison semaine précédente", prefs["show_weekly_comp_coach"]),
        })

        # Mensuel
        st.markdown("#### 📅Suivi mensuel")
        updated_prefs.update({
            "show_monthly_intensity_coach": st.checkbox("Graphique mois - Intensité", prefs["show_monthly_intensity_coach"]),
            "show_monthly_parameter_coach": st.checkbox("Graphique mois - Stress/Fatigue/Sommeil/Dynamisme", prefs["show_monthly_parameter_coach"]),
            "show_monthly_zscore_coach": st.checkbox("Graphique mois - Z-Score", prefs["show_monthly_zscore_coach"]),
            "show_monthly_score_bien_coach":st.checkbox("Graphique mois - Score bien-être", prefs["show_monthly_score_bien_coach"]),
            "show_monthly_comp_coach": st.checkbox("Comparaison mois précédent", prefs["show_monthly_comp_coach"]),
        })

        # Synthèse
        st.markdown("#### 📊Synthèse")
        updated_prefs.update({
            "show_global_intensity_coach": st.checkbox("Graphique général - Intensité", prefs["show_global_intensity_coach"]),
            "show_global_parameter_coach": st.checkbox("Graphique général - Stress/Fatigue/Sommeil/Dynamisme", prefs["show_global_parameter_coach"]),
            "show_global_zscore_coach": st.checkbox("Graphique général - Z-Score", prefs["show_global_zscore_coach"]),
            "show_global_score_bien_coach": st.checkbox("Graphique général - Score bien-être", prefs["show_global_score_bien_coach"]),
        })
        
        st.subheader("Page compte rendu collectif")
        st.write("Coche les éléments que tu veux afficher sur ta page compte rendu collectif et enregistres :")
        st.markdown("#### 📍Suivi quotidien")
        updated_prefs.update({
            "show_seance_team_coach":st.checkbox("Graphique collectif quotidien - Intensité/Stress/Fatigue/Sommeil/Dynamisme", prefs["show_seance_team_coach"]),
            "show_team_intensity_coach": st.checkbox("Graphique collectif quotidien - Intensité", prefs["show_team_intensity_coach"]),
            "show_cadran": st.checkbox("Graphique collectif quotidien - Stress/Fatigue/Sommeil/Dynamisme", prefs["show_cadran"]),
            "show_team_bien_etre_coach": st.checkbox("Graphique collectif quotidien - Score bien-être", prefs["show_team_bien_etre_coach"]),
            "show_team_douleurs_coach": st.checkbox("Graphique collectif quotidien - Douleurs", prefs["show_team_douleurs_coach"]),
    
        })
        st.markdown("#### 📊Synthèse sur une période donnée")
        updated_prefs.update({
            "show_team_synthèse_intensity_coach": st.checkbox("Graphique collectif général - Intensité", prefs["show_team_synthèse_intensity_coach"]),
            "show_cadran_synthèse": st.checkbox("Graphique collectif général - Stress/Fatigue/Sommeil/Dynamisme", prefs["show_cadran_synthèse"]),
            "show_team_synthèse_bien_etre_coach": st.checkbox("Graphique collectif général - Score bien-être", prefs["show_team_synthèse_bien_etre_coach"]),
        })
        submitted = st.form_submit_button("Enregistrer")
        if submitted:
            save_preferences(username, updated_prefs)
            st.success("Préférences mises à jour.") 

# ========================================================= Page informations =========================================================
elif page == "Informations":
    st.title ("Informations questionnaire")
    st.write("Voici le questionnaire auxquel les joueurs répondent :")
    
    prefs = get_preferences(st.session_state.get("username", ""))
    frequence = prefs.get("mode_questionnaire", "Tous les jours")
    
    if frequence == "Tous les jours":
     st.subheader("🏃‍♂️Activité du jour")   
     st.write("As-tu fait une séance ou un match à cette date ? Si oui, affichage de la question sur l'intensité.")   
     st.subheader("🔥Intensité")
     st.write("Évalue entre 1 et 10 l'intensité de la séance/du match (1 = aucune intensité, 10 = intensité maximale).")
     st.subheader("💤Sommeil")
     st.write("Évalue entre 1 et 10 la qualité de ton dernier sommeil (1 = très mal dormi, 10 = très bien dormi).")
     st.subheader("🥱Fatigue")
     st.write("Évalue entre 1 et 10 ton niveau de fatigue (1 = aucune fatigue, 10 = exténué).")
     st.subheader("😟Stress")
     st.write("Évalue entre 1 et 10 ton stress actuel (1 = aucun stress, 10 = très stressé).")
     st.subheader("⚡Dynamisme")
     st.write("Évalue entre 1 et 10 ton dynamisme actuel (1 = très peu dynamique, 10 = très dynamique).")
     st.subheader("🤕Douleurs")
     st.write("As-tu des douleurs et/ou des courbatures ? Si oui, où sont les douleurs ? Précises les informations.")
    else :   
     st.subheader("🔥Intensité")
     st.write("Évalue entre 1 et 10 l'intensité de la séance/du match (1 = aucune intensité, 10 = intensité maximale).")    
     st.subheader("💤Sommeil")
     st.write("Évalue entre 1 et 10 la qualité de ton dernier sommeil (1 = très mal dormi, 10 = très bien dormi).")
     st.subheader("🥱Fatigue")
     st.write("Évalue entre 1 et 10 ton niveau de fatigue (1 = aucune fatigue, 10 = exténué).")
     st.subheader("😟Stress")
     st.write("Évalue entre 1 et 10 ton stress actuel (1 = aucun stress, 10 = très stressé).")
     st.subheader("⚡Dynamisme")
     st.write("Évalue entre 1 et 10 ton dynamisme actuel (1 = très peu dynamique, 10 = très dynamique).")
     st.subheader("🤕Douleurs")
     st.write("As-tu des douleurs et/ou des courbatures ? Si oui, où sont les douleurs ? Précises les informations.")
    
    
    
