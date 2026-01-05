import streamlit as st
import pandas as pd
from datetime import datetime, date as _date

# Plotly est optionnel
try:
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except Exception:
    px = None
    PLOTLY_AVAILABLE = False

st.set_page_config(page_title="Dashaalia", layout="wide", initial_sidebar_state="expanded")

# --- Load external CSS ---
def load_css(file_path: str = "style.css"):
    try:
        with open(file_path, "r") as f:
            css = f.read()
            st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"⚠️ Le fichier CSS {file_path} est introuvable.")

load_css()

# --- Helpers ---
@st.cache_data
def load_data(path: str = "./sessions_dataset_320.csv") -> pd.DataFrame:
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        st.error(f"Fichier introuvable : {path}")
        return pd.DataFrame()

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    expected = ["service", "langue", "duree_minutes", "interactions_patient",
                "interactions_praticien", "note_praticien", "qualite_score",
                "segments_non_reconnus", "device"]
    for col in expected:
        if col not in df.columns:
            df[col] = pd.NA

    return df


def filter_data(df: pd.DataFrame,
                date_range=None,
                services=None,
                langues=None,
                min_note=None,
                min_qualite=None,
                device=None,
                notes_query: str = "") -> pd.DataFrame:
    if df.empty:
        return df

    d = df.copy()

    if date_range is not None:
        start, end = date_range
        start = pd.to_datetime(start).date()
        end = pd.to_datetime(end).date()
        today = datetime.now().date()
        if start > today:
            start = today
        if end > today:
            end = today
        d = d[(d["date"].dt.date >= start) & (d["date"].dt.date <= end)]

    if services:
        d = d[d["service"].isin(services)]
    if langues:
        d = d[d["langue"].isin(langues)]

    if min_note is not None:
        d = d[pd.to_numeric(d["note_praticien"], errors="coerce") >= min_note]

    if min_qualite is not None:
        d = d[pd.to_numeric(d["qualite_score"], errors="coerce") >= min_qualite]

    if device:
        d = d[d["device"] == device]

    # Détecter les colonnes de notes textuelles : nom contenant 'note' et non numériques
    notes_cols = []
    for c in d.columns:
        if "note" in c:
            if not pd.api.types.is_numeric_dtype(d[c]):
                notes_cols.append(c)

    # Recherche textuelle seulement dans les colonnes textuelles détectées
    if notes_query and notes_cols:
        mask = False
        for c in notes_cols:
            mask = mask | d[c].astype(str).str.contains(notes_query, case=False, na=False)
        d = d[mask]

    return d


# --- Helpers d'affichage ---
def format_for_display(df: pd.DataFrame, date_cols=('date',)) -> pd.DataFrame:
    """Retourne une copie du DataFrame avec les colonnes date tronquées à la date seulement (pas d'heure)."""
    d2 = df.copy()
    for c in date_cols:
        if c in d2.columns:
            d2[c] = pd.to_datetime(d2[c], errors='coerce').dt.date
    return d2


@st.cache_data
def convert_df_to_csv(df):
    df2 = format_for_display(df)
    return df2.to_csv(index=False).encode('utf-8')


# --- Main ---

# Header stylisé
st.markdown("""
<div class="header-style">
    <div class="header-title">📊 Dashaalia</div>
    <div class="header-subtitle">Analyse complète des sessions médicales</div>
</div>
""", unsafe_allow_html=True)

# Sidebar avec header stylisé
st.sidebar.markdown('<div class="sidebar-header">🎛️ Panneau de Filtres</div>', unsafe_allow_html=True)

# Load data
with st.spinner("⏳ Chargement des données..."):
    df = load_data()

if df.empty:
    st.warning("⚠️ Le dataset est vide ou manquant. Placez `sessions_dataset_320.csv` à la racine du projet.")
    st.stop()

# --- Sidebar filters ---
st.sidebar.markdown("### 📅 Période")
min_date = df["date"].min().date()
max_date = df["date"].max().date()
today = _date.today()

default_end = min(max_date, today)
default_start = min_date if min_date <= default_end else default_end

st.sidebar.caption(f"📌 Dates disponibles : {min_date} — {max_date}")
st.sidebar.caption(f"🔒 Limité à aujourd'hui : {today}")

date_range = st.sidebar.date_input(
    "Intervalle de dates",
    value=[default_start, default_end],
    min_value=min_date,
    max_value=today,
    key="date_range",
    help="Sélectionnez un intervalle ; les dates futures sont interdites."
)

if isinstance(date_range, (tuple, list)):
    start, end = (date_range[0], date_range[-1])
else:
    start = end = date_range

start = pd.to_datetime(start).date()
end = pd.to_datetime(end).date()

inverted = False
if start > end:
    inverted = True
    st.sidebar.warning("⚠️ Dates inversées — correction appliquée.")
    start, end = end, start

clamped = False
if start > today:
    clamped = True
    st.sidebar.warning(f"⚠️ Date de début ramenée à aujourd'hui.")
    start = today
if end > today:
    clamped = True
    st.sidebar.warning(f"⚠️ Date de fin ramenée à aujourd'hui.")
    end = today

# Update widget if corrections applied to reflect corrected dates
try:
    if inverted or clamped:
        current = st.session_state.get("date_range", None)
        need_update = True
        if current is not None:
            try:
                if isinstance(current, (list, tuple)):
                    cur0 = pd.to_datetime(current[0]).date()
                    cur1 = pd.to_datetime(current[-1]).date()
                else:
                    cur0 = cur1 = pd.to_datetime(current).date()
                need_update = (cur0 != start) or (cur1 != end)
            except Exception:
                need_update = True
        if need_update:
            st.session_state["date_range"] = [start, end]
            st.sidebar.info("La sélection de dates a été ajustée pour éviter les dates futures ou inversées.")
except Exception:
    pass

st.sidebar.markdown("---")
st.sidebar.markdown("### 🏥 Services & Langues")
services = st.sidebar.multiselect("Service(s)", options=sorted(df["service"].dropna().unique()), default=None)
langues = st.sidebar.multiselect("Langue(s)", options=sorted(df["langue"].dropna().unique()), default=None)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📱 Appareil")
device = st.sidebar.selectbox("Appareil", options=["Aucun"] + sorted(df["device"].dropna().unique().tolist()), index=0)

st.sidebar.markdown("---")
st.sidebar.markdown("### ⭐ Qualité")
min_note = st.sidebar.slider("Note praticien minimale", min_value=0.0, max_value=5.0, value=0.0, step=0.1)
min_qualite = st.sidebar.slider("Qualité minimale", min_value=0.0, max_value=1.0, value=0.0, step=0.01)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔍 Recherche")
notes_query = st.sidebar.text_input("Recherche dans les notes praticiens", placeholder="Entrez un mot-clé...")

# Apply filters
filtered = filter_data(
    df,
    date_range=(start, end),
    services=services if services else None,
    langues=langues if langues else None,
    min_note=min_note,
    min_qualite=min_qualite,
    device=None if device == "Aucun" else device,
    notes_query=notes_query
)

# --- KPIs ---
st.markdown('<div class="section-header">📈 Indicateurs Clés</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("🎯 Sessions", f"{len(filtered):,}", delta=None)
with col2:
    st.metric("⏱️ Durée moyenne", f"{filtered['duree_minutes'].mean():.1f} min", delta=None)
with col3:
    st.metric("⭐ Note praticien", f"{filtered['note_praticien'].mean():.2f}/5", delta=None)
with col4:
    st.metric("✨ Qualité", f"{filtered['qualite_score'].mean():.2f}", delta=None)

st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

# --- Analyse des Langues ---
st.markdown('<div class="section-header">🌐 Analyse des Langues</div>', unsafe_allow_html=True)

if filtered.empty:
    st.warning("⚠️ Aucun résultat après application des filtres.")
else:
    col_lang1, col_lang2 = st.columns([1, 3])
    with col_lang1:
        top_n = st.slider("📊 Nombre de langues", min_value=3, max_value=30, value=15)
    
    lang_counts = filtered["langue"].value_counts().reset_index()
    lang_counts.columns = ["langue", "count"]

    if PLOTLY_AVAILABLE:
        fig_lang = px.bar(lang_counts.head(top_n), x="langue", y="count", text="count",
                          labels={"count":"Nombre de sessions"}, 
                          title="Distribution des langues",
                          color_discrete_sequence=['#667eea'])
        fig_lang.update_layout(
            xaxis_tickangle=-45,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_lang, use_container_width=True)
    else:
        st.info("💡 Installez `plotly` pour voir ce graphique")

st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

# --- Évolution temporelle ---
st.markdown('<div class="section-header">📈 Évolution Temporelle</div>', unsafe_allow_html=True)

col_time1, col_time2 = st.columns([1, 3])
with col_time1:
    freq = st.selectbox("⏰ Agrégation", ["Jour", "Semaine", "Mois"], index=0)

if freq == "Jour":
    grp = filtered.groupby(filtered["date"].dt.date).size()
elif freq == "Semaine":
    grp = filtered.groupby(pd.Grouper(key="date", freq="W-MON")).size()
else:
    grp = filtered.groupby(pd.Grouper(key="date", freq="M")).size()
grp = grp.rename("sessions").reset_index()

if PLOTLY_AVAILABLE:
    fig_evo = px.line(grp, x=grp.columns[0], y="sessions", markers=True, 
                      title="Évolution du nombre de sessions",
                      color_discrete_sequence=['#764ba2'])
    fig_evo.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_evo, use_container_width=True)
else:
    st.info("💡 Installez `plotly` pour voir ce graphique")

st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

# --- Durée moyenne et Répartition services ---
col_left, col_right = st.columns(2)

with col_left:
    st.markdown('<div class="section-header">⏱️ Durée Moyenne</div>', unsafe_allow_html=True)
    dur_by_service = filtered.groupby("service")["duree_minutes"].mean().reset_index().sort_values(by="duree_minutes", ascending=False)
    if PLOTLY_AVAILABLE:
        fig_dur = px.bar(dur_by_service, x="service", y="duree_minutes", 
                         title="Durée moyenne par service",
                         labels={"duree_minutes":"Durée (min)"},
                         color_discrete_sequence=['#667eea'])
        fig_dur.update_layout(
            xaxis_tickangle=-45,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_dur, use_container_width=True)
    else:
        st.info("💡 Installez `plotly` pour voir ce graphique")

with col_right:
    st.markdown('<div class="section-header">🏥 Répartition Services</div>', unsafe_allow_html=True)
    serv_counts = filtered["service"].value_counts().reset_index()
    serv_counts.columns = ["service", "count"]
    if PLOTLY_AVAILABLE:
        fig_serv = px.pie(serv_counts, values="count", names="service", 
                          title="Répartition des sessions par service",
                          color_discrete_sequence=px.colors.sequential.Purples)
        fig_serv.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_serv, use_container_width=True)
    else:
        st.info("💡 Installez `plotly` pour voir ce graphique")

st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

# --- Indicateurs qualité ---
st.markdown('<div class="section-header">📋 Indicateurs Qualité</div>', unsafe_allow_html=True)

col_a, col_b = st.columns([1, 2])
with col_a:
    st.markdown("### 📊 Métriques")
    st.metric("⭐ Note praticien moyenne", f"{filtered['note_praticien'].mean():.2f}/5")
    st.metric("✨ Qualité moyenne", f"{filtered['qualite_score'].mean():.2f}")
    st.metric("🔇 Segments non reconnus", f"{filtered['segments_non_reconnus'].mean():.1f}")

with col_b:
    if PLOTLY_AVAILABLE:
        fig_q = px.histogram(filtered, x="qualite_score", nbins=20, 
                             title="Distribution du score de qualité",
                             color_discrete_sequence=['#764ba2'])
        fig_q.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_q, use_container_width=True)
    else:
        st.info("💡 Installez `plotly` pour voir ce graphique")

st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

# --- Interactions ---
st.markdown('<div class="section-header">🤝 Analyse des Interactions</div>', unsafe_allow_html=True)

if PLOTLY_AVAILABLE:
    fig_int = px.box(filtered, y=["interactions_patient", "interactions_praticien"], 
                     title="Répartition des interactions patient/praticien",
                     color_discrete_sequence=['#667eea', '#764ba2'])
    fig_int.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_int, use_container_width=True)
else:
    st.info("💡 Installez `plotly` pour voir ce graphique")

st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

# --- Notes praticiens ---
st.markdown('<div class="section-header">📝 Notes Praticiens</div>', unsafe_allow_html=True)

# Afficher uniquement les colonnes numériques contenant 'note' dans un tableau
note_columns = [c for c in filtered.columns if "note" in c and pd.api.types.is_numeric_dtype(filtered[c])]

if note_columns:
    with st.expander("Afficher les notes praticiens", expanded=False):
        df_notes = filtered[note_columns + ['session_id', 'service', 'date']].sort_values('date', ascending=False)
        st.dataframe(format_for_display(df_notes), use_container_width=True)
else:
    st.info("ℹ️ Aucune colonne numérique 'note' trouvée dans le dataset.")

st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

# --- Export CSV ---
st.markdown('<div class="section-header">📥 Export des Données</div>', unsafe_allow_html=True)

with st.expander("📊 Voir les données filtrées", expanded=False):
    st.dataframe(format_for_display(filtered), use_container_width=True)

csv = convert_df_to_csv(filtered)
st.download_button(
    label="⬇️ Télécharger les données filtrées (CSV)", 
    data=csv, 
    file_name="sessions_filtered.csv", 
    mime="text/csv",
    use_container_width=True
)

st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

# Footer
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem 0; font-size: 0.9rem;'>
    <p>🚀 Interface générée avec Streamlit</p>
    <p>📧 Contactez l'équipe données pour ajouter des colonnes de notes ou d'autres métadonnées</p>
</div>
""", unsafe_allow_html=True)
