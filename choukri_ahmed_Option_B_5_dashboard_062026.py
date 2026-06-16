import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuration de la page
st.set_page_config(
    page_title="Sport Data Solution - Dashboard Dynamique",
    page_icon="🏃",
    layout="wide"
)

st.title("🏃 Sport Data Solution - Dashboard Dynamique")
st.markdown("### Avantages Sportifs - Analyse interactive")

# Chargement des données
@st.cache_data
def load_data():
    conn = sqlite3.connect('sport_data.db')
    df_avantages = pd.read_sql("SELECT * FROM avantages", conn)
    df_salaries = pd.read_sql("SELECT * FROM salaries", conn)
    df_activites = pd.read_sql("SELECT * FROM activites", conn)
    conn.close()
    return df_avantages, df_salaries, df_activites

df_avantages, df_salaries, df_activites = load_data()

# === SIDEBAR - FILTRES ===
st.sidebar.header("🎛️ Filtres interactifs")

# Filtre par mode de transport
modes = df_salaries['Moyen de déplacement'].unique()
selected_mode = st.sidebar.multiselect(
    "Mode de transport",
    options=modes,
    default=modes
)

# Filtre par éligibilité
eligible_filter = st.sidebar.radio(
    "Afficher",
    ["Tous", "Éligibles uniquement", "Non éligibles uniquement"]
)

# Slider pour le taux de prime
prime_pct = st.sidebar.slider(
    "Taux de prime sportive (%)",
    min_value=0,
    max_value=15,
    value=5,
    step=1
)

# Slider pour le seuil d'activités
min_activites = st.sidebar.slider(
    "Seuil minimum d'activités pour bien-être",
    min_value=5,
    max_value=30,
    value=15,
    step=1
)

# Application des filtres
filtered_ids = df_salaries[df_salaries['Moyen de déplacement'].isin(selected_mode)]['ID salarié']
df_filtered = df_avantages[df_avantages['ID salarié'].isin(filtered_ids)]

if eligible_filter == "Éligibles uniquement":
    df_filtered = df_filtered[df_filtered['eligible_prime'] == 1]
elif eligible_filter == "Non éligibles uniquement":
    df_filtered = df_filtered[df_filtered['eligible_prime'] == 0]

# Calcul des KPI
total = len(df_filtered)
eligible_count = df_filtered['eligible_prime'].sum()
eligible_rate = (eligible_count / total * 100) if total > 0 else 0
total_prime = df_filtered['montant_prime'].sum() * (prime_pct / 5)  # Ajustement dynamique

# Recalcul bien-être avec seuil dynamique
df_activites_filtered = df_activites[df_activites['id_salarie'].isin(filtered_ids)]
act_count = df_activites_filtered.groupby('id_salarie').size().reset_index(name='nb_act')
act_count['eligible_be'] = act_count['nb_act'] >= min_activites
eligible_be = act_count['eligible_be'].sum()
total_be = len(act_count)
be_rate = (eligible_be / total_be * 100) if total_be > 0 else 0

# === KPI ===
st.markdown("## 📊 Indicateurs clés")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("👥 Effectif", total)
with col2:
    st.metric("✅ Éligibles prime", f"{eligible_count}", delta=f"{eligible_rate:.1f}%")
with col3:
    st.metric("💰 Coût primes", f"{total_prime:,.0f} €")
with col4:
    st.metric("🏖️ Éligibles bien-être", f"{eligible_be}", delta=f"{be_rate:.1f}%")
with col5:
    st.metric("💵 Coût total", f"{total_prime + (eligible_be * 5 * 230):,.0f} €")

st.markdown("---")

# === GRAPHIQUES ===
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("### 🚲 Éligibilité par mode de transport")
    mode_elig = df_filtered.groupby('Moyen de déplacement')['eligible_prime'].agg(['count', 'sum'])
    mode_elig.columns = ['total', 'eligibles']
    mode_elig['taux'] = (mode_elig['eligibles'] / mode_elig['total'] * 100).round(1)
    fig = px.bar(
        mode_elig.reset_index(),
        x='Moyen de déplacement',
        y='taux',
        title="Taux d'éligibilité",
        color='taux',
        text='taux'
    )
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.markdown("### 🏆 Top sports pratiqués")
    sport_counts = df_activites_filtered['sport'].value_counts().head(10).reset_index()
    sport_counts.columns = ['Sport', 'Nombre']
    fig = px.bar(
        sport_counts,
        x='Nombre',
        y='Sport',
        orientation='h',
        title="Top 10 sports",
        color='Nombre'
    )
    st.plotly_chart(fig, use_container_width=True)

# === TABLEAU INTERACTIF ===
st.markdown("### 📋 Liste des salariés")
st.dataframe(
    df_filtered[['ID salarié', 'Nom', 'Prénom', 'Salaire brut', 'distance_km', 'eligible_prime', 'montant_prime']].head(50),
    use_container_width=True
)

# === TÉLÉCHARGEMENT ===
csv = df_filtered.to_csv(index=False).encode('utf-8-sig')
st.download_button(
    label="📥 Télécharger les données (CSV)",
    data=csv,
    file_name="export_salaries.csv",
    mime="text/csv"
)

st.markdown("---")
st.caption("📅 Dashboard dynamique - Mise à jour en temps réel")