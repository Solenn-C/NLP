import streamlit as st
import requests
import plotly.express as px
import pandas as pd
import urllib.parse

st.set_page_config(layout="wide", page_title="NomenGlobe Explorer", page_icon="🌍")

@st.cache_data
def get_country_mappings():
    try:
        df_countries = pd.read_csv("countries_fr.csv")
        # Dictionnaire ISO -> Nom
        iso_to_name = dict(zip(df_countries['iso_alpha'], df_countries['origin_fr']))
        # Dictionnaire Nom -> ISO (pour la recherche par origines)
        name_to_iso = dict(zip(df_countries['origin_fr'], df_countries['iso_alpha']))
        return iso_to_name, name_to_iso
    except Exception as e:
        st.error(f"Erreur chargement référentiel pays : {e}")
        return {}, {}

iso_to_name, name_to_iso = get_country_mappings()

if "input_p" not in st.session_state: st.session_state.input_p = ""
if "input_n" not in st.session_state: st.session_state.input_n = ""

# --- DESIGN CSS ---
st.markdown("""
    <style>
    .main { background-color: transparent !important; }
    .stApp { background-color: transparent !important; }
    
    /* CASE DÉTAIL BLANCHE */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: white !important;
        border-radius: 20px !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1) !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: white !important;
    }
    
    /* CARTES STATS */
    .stat-card {
        background-color: #f8fafc;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        border: 1px solid #e2e8f0;
    }
    .stat-val { color: #6366f1; font-weight: 800; font-size: 1.3rem; display: block; }
    .stat-label { color: #64748b; font-size: 0.75rem; text-transform: uppercase; font-weight: 600; }

    .gender-pill {
        background-color: #6366f1; color: white; padding: 4px 16px;
        border-radius: 12px; font-size: 0.85rem; font-weight: bold;
        display: inline-block; margin-bottom: 15px;
    }

    /* BOUTONS BLEUS */
    div.stButton > button {
        background-color: #6366f1 !important;
        color: white !important;
        border-radius: 20px;
        border: none;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover { background-color: #4f46e5 !important; transform: translateY(-2px); }
    </style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("🌐 NomenGlobe")
search_prenom = st.sidebar.text_input("Rechercher un Prénom :", value=st.session_state.input_p, key="search_p")
search_nom = st.sidebar.text_input("Rechercher un Nom :", value=st.session_state.input_n, key="search_n")

query = search_prenom if search_prenom else (search_nom if search_nom else None)
search_type = "prenom" if search_prenom else "nom"

if query:
    try:
        response = requests.get(f"http://127.0.0.1:8000/api/search/{search_type}/{urllib.parse.quote(query)}")
        if response.status_code == 200:
            res = response.json()
            col_map, col_details = st.columns([1, 1])
            
            with col_map:
                st.subheader("Origines Géographiques")
                origins_raw = res.get('origins', '')
                
                if origins_raw:
                    # On nettoie et sépare la chaîne (ex: "France, Italy" -> ["France", "Italy"])
                    origins_list = [o.strip() for o in origins_raw.split(',')]
                    
                    # On récupère les codes ISO correspondants
                    origin_isos = [name_to_iso.get(country) for country in origins_list if country in name_to_iso]
                    
                    if origin_isos:
                        df_map = pd.DataFrame({
                            "iso": origin_isos,
                            "presence": [1] * len(origin_isos),
                            "pays": [iso_to_name.get(iso) for iso in origin_isos]
                        })
                        
                        fig = px.choropleth(
                            df_map, 
                            locations="iso", 
                            color="presence", 
                            hover_name="pays", 
                            color_continuous_scale="Blues"
                        )
                        
                        fig.update_coloraxes(showscale=False) # Masque la barre de légende
                        fig.update_layout(
                            height=500, 
                            margin={"r":0,"t":0,"l":0,"b":0}, 
                            geo=dict(landcolor="#f8fafc", oceancolor="#e0f2fe", showocean=True)
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("🌍 Localisation impossible : les pays d'origine ne sont pas dans le référentiel.")
                else:
                    st.info("Aucune donnée d'origine disponible pour ce nom.")

            with col_details:
                st.subheader("📄 Détails du profil")
                with st.container(border=True):
                    gender = res.get('gender', 'u')
                    gender_text = "♂ Masculin" if gender == "m" else "♀ Féminin" if gender == "f" else "⚥ Unisexe"
                    
                    st.markdown(f'<span class="gender-pill">{gender_text}</span>', unsafe_allow_html=True)
                    st.markdown(f'<h1 style="margin-top:0px; color:#1e293b; font-size: 2.8rem; font-weight:800;">{res.get("name")}</h1>', unsafe_allow_html=True)
                    
                    # Section Stats
                    s1, s2, s3 = st.columns(3)
                    s1.markdown(f'<div class="stat-card"><span class="stat-label">🌍 Rang</span><span class="stat-val">#{res.get("rank")}</span></div>', unsafe_allow_html=True)
                    s2.markdown(f'<div class="stat-card"><span class="stat-label">👥 Incidence</span><span class="stat-val">{res.get("incidence")}</span></div>', unsafe_allow_html=True)
                    s3.markdown(f'<div class="stat-card"><span class="stat-label">📊 Fréquence</span><span class="stat-val">{res.get("frequency")}</span></div>', unsafe_allow_html=True)
                    
                    st.markdown(f'<p style="color:#64748b; margin-top:20px;"><b>Origines :</b> {origins_raw}</p><hr style="border:0; border-top:1px solid #f1f5f9; margin: 20px 0;"><p style="font-weight: bold; color:#1e293b;">Variants :</p>', unsafe_allow_html=True)

                    v_list = res.get('variants_list', [])
                    if v_list:
                        cv = st.columns(3)
                        for i, v in enumerate(v_list[:9]):
                            if cv[i % 3].button(v, key=f"v_{i}"):
                                if search_type == "prenom": 
                                    st.session_state.input_p, st.session_state.input_n = v, ""
                                else: 
                                    st.session_state.input_n, st.session_state.input_p = v, ""
                                st.rerun()
                    else: 
                        st.info("Aucun variant.")
        else: 
            st.sidebar.error("❌ Non trouvé.")
    except Exception as e: 
        st.error(f"🔌 Connexion API impossible : {e}")
else:
    st.info("👋 Recherchez un nom ou un prénom dans les barres latérale pour commencer.")