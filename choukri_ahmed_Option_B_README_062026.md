# POC Avantages Sportifs – Sport Data Solution

Pipeline de donnees de bout en bout pour evaluer et calculer les avantages sportifs des salaries.

## Contexte

Sport Data Solution souhaite mettre en place un systeme de suivi des flux de donnees pour valider en continu l'integration des donnees RH et sportives, afin de calculer automatiquement les avantages sportifs des salaries.

## Livrables

| Livrable | Fichier | Statut |
|----------|---------|--------|
| Pipeline ETL | `pipeline_etl.py` | Fonctionnel |
| Tests qualite | `tests_qualite.py` | 22/22 PASS |
| Dashboard | `dashboard.py` | Streamlit fonctionnel |
| Orchestration | `airflow_dag.py` | DAG pret pour production |
| Validation trajets | `validate_commute.py` | Geocodage + distance |
| Generation donnees | `generate_strava_data.py` | Simulation 3 592 activites |
| Messages Slack | `generate_slack_messages.py` | Notifications automatiques |

## Structure du projet

```
P12_Gerez_un_projet_d_infrastructure
├── choukri_ahmed_Option_B_1_validate_commute_06202605.py      # Validation trajets domicile-bureau
├── choukri_ahmed_Option_B_1_1_test_nominatim_0620260502.py    # Test API geocodage
├── choukri_ahmed_Option_B_2_generate_strava_062026.py         # Generation donnees sportives simulees
├── choukri_ahmed_Option_B_3_generate_slack_062026.py         # Generation messages Slack
├── choukri_ahmed_Option_B_4_pipeline_etl_062026.py           # Pipeline ETL principal
├── choukri_ahmed_Option_B_5_2_airflow_dag_062026.py            # Orchestration Airflow
├── choukri_ahmed_Option_B_5_dashboard_062026.py               # Dashboard Streamlit
├── choukri_ahmed_Option_B_6_tests_qualite_062026.py           # Tests qualite des donnees
├── Donnees-RH.xlsx                                            # Donnees RH source
├── Donnees-Sportive.xlsx                                      # Declarations sportives
├── strava_activities.csv                                      # Activites generees (3 592)
├── validation_complete.csv                                    # Resultats validation
├── sport_data.db                                              # Base SQLite
├── wellness_eligibility.csv                                   # Eligibilite bien-etre
├── slack_messages_final.csv                                   # Messages Slack
└── venv/                                                      # Environnement virtuel
```

## Avantages calcules

| Avantage | Condition | Valeur |
|---|---|---|
| **Prime sportive** | Venir au bureau a pied / velo, distance validee | 5% du salaire annuel brut |
| **5 jours bien-etre** | >= 15 activites physiques soutenues dans l'annee | 5 jours supplementaires |

## Resultats du POC (161 salaries)

| Indicateur | Valeur |
|---|---|
| Effectif total | 161 salaries |
| Eligibles prime sportive | 59 salaries (36.6%) |
| Coût primes | 148 848 EUR / an |
| Anomalies declarations transport | 9 a verifier |
| Eligibles journees bien-etre | 111 salaries (69.0%) |
| Jours bien-etre accordes | 555 jours |
| **Coût total estime** | **148 848 EUR / an** (primes uniquement) |

## Regles de validation transport

- **Marche / Running** : distance domicile-bureau <= 15 km
- **Velo / Trottinette / Autres** : distance domicile-bureau <= 25 km

Validation via cache de coordonnees GPS par code postal + formule Haversine.  
En production : remplacer par l'API Google Maps Distance Matrix.

## Architecture technique

```
Sources (Excel/CSV) -> ETL (Python/Pandas) -> Tests qualite -> SQLite -> Streamlit + Slack
                                    |
                                    v
                              Airflow (orchestration)
```

| Couche | Outil | Description |
|---|---|---|
| Ingestion | Python / Pandas | Lecture Excel, CSV, geocodage |
| Transformation | Python / Pandas | Validation, calcul eligibilite, merge |
| Orchestration | Apache Airflow | DAG quotidien 6h avec monitoring |
| Stockage | SQLite | Base relationnelle (PostgreSQL en production) |
| Tests qualite | Great Expectations (style) | 22 tests sur 3 tables |
| Monitoring | Logs Python + XCom Airflow | Suivi execution et anomalies |
| Visualisation | Streamlit | Dashboard interactif avec filtres |
| Notifications | Slack Webhook | Messages automatiques par activite |

## Installation

```bash
# Cloner le repository
git clone https://github.com/choukri063/poc-sport-data-solution.git
cd poc-sport-data-solution

# Creer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Installer les dependances
pip install pandas numpy geopy openpyxl plotly streamlit requests

# Pour Airflow (optionnel)
pip install apache-airflow
```

## Utilisation

### 1. Valider les trajets domicile-bureau
```bash
python choukri_ahmed_Option_B_1_validate_commute_06202605.py
```
Genere : `validation_complete.csv`, `salaries_eligibles.csv`, `salaries_non_eligibles.csv`

### 2. Generer les donnees sportives simulees
```bash
python choukri_ahmed_Option_B_2_generate_strava_062026.py
```
Genere : `strava_activities.csv` (3 592 activites), `wellness_eligibility.csv`

### 3. Lancer le pipeline ETL complet
```bash
python choukri_ahmed_Option_B_4_pipeline_etl_062026.py
```
Genere : `sport_data.db` (SQLite avec 3 tables : salaries, activites, avantages)

### 4. Lancer les tests de qualite
```bash
python choukri_ahmed_Option_B_6_tests_qualite_062026.py
```
Resultat attendu : **22 tests passes, 0 echecs**

### 5. Lancer le dashboard Streamlit
```bash
streamlit run choukri_ahmed_Option_B_5_dashboard_062026.py
```
Acces : http://localhost:8501

### 6. Generer les messages Slack (optionnel)
```bash
python choukri_ahmed_Option_B_3_generate_slack_062026.py
```
Genere : `slack_messages_final.csv`

## Parametrages configurables

| Parametre | Valeur par defaut | Description | Ou modifier |
|-----------|-------------------|-------------|-----------|
| `PRIME_PCT` | 5% | Taux de la prime sportive | `pipeline_etl.py` ligne 12 |
| `BIENETRE_MIN` | 15 | Seuil activites pour bien-etre | `pipeline_etl.py` ligne 13 |
| `BIENETRE_JOURS` | 5 | Jours bien-etre accordes | `pipeline_etl.py` ligne 14 |
| `MARCHE_MAX_KM` | 15 | Distance max marche | `pipeline_etl.py` ligne 15 |
| `VELO_MAX_KM` | 25 | Distance max velo | `pipeline_etl.py` ligne 16 |
| Taux prime (dashboard) | 5% | Slider 0-15% | `dashboard.py` sidebar |
| Seuil activites (dashboard) | 15 | Slider 5-30 | `dashboard.py` sidebar |

## Tests de qualite (22 tests)

### Table salaries (6 tests)
- ID salarie unique
- Pas de doublons nom+prenom
- Salaire brut positif et dans fourchette [20k-200k]
- Pas de nom vide
- Moyen de deplacement valide

### Table activites (10 tests)
- ID salarie present
- Distance non negative et < 200 km
- Duree positive et < 24h
- Dates valides
- ID salarie reference un salarie connu
- Sport dans liste referentielle
- Intensite valide (soutenu/modere/leger)
- Calories positives

### Table avantages (6 tests)
- Montant prime >= 0
- Montant prime = 5% salaire si eligible
- Jours bien-etre = 0 ou 5 uniquement
- Pas d'eligible prime avec anomalie transport
- Nombre d'activites coherent
- Correlation prime/bien-etre coherente

## KPI Dashboard Streamlit

1. **Effectif** - Nombre total de salaries filtres
2. **Eligibles prime** - Nombre et taux d'eligibilite
3. **Coût primes** - Montant total avec ajustement dynamique du taux
4. **Eligibles bien-etre** - Nombre et taux avec seuil configurable
5. **Coût total** - Primes + cout des jours bien-etre
6. **Taux d'eligibilite par mode de transport** - Graphique barres Plotly
7. **Top 10 sports pratiques** - Graphique horizontal Plotly
8. **Tableau interactif** - Liste des salaries avec filtres

## Filtres interactifs

- Mode de transport (multiselect)
- Eligibilite (radio : Tous / Eligibles / Non eligibles)
- Taux de prime sportive (slider 0-15%)
- Seuil minimum d'activites pour bien-etre (slider 5-30)

## Notes de securite

- Donnees RH sensibles : base de donnees chiffree en production (PostgreSQL + SSL)
- Acces role-based (lecture seule pour dashboard, ecriture pipeline uniquement)
- Pas de donnees personnelles exposees dans les logs
- Connexion Strava reelle : OAuth2 par salarie (phase 2)
- Geocodage : Nominatim (OpenStreetMap) pour le POC, API payante en production

## Evolutions prevues

- Connexion directe API Strava (OAuth2) pour remplacer la simulation
- Integration API Google Maps pour validation distances en temps reel
- Dashboard Power BI avec rechargement automatique depuis PostgreSQL
- Airflow DAG pour execution quotidienne du pipeline
- Alertes email automatiques si anomalies > seuil
- Authentification sur le dashboard Streamlit

## Auteur

**Choukri Ahmed**  
Projet : P12 - Gerer un projet d'infrastructure de donnees  
Date : Juin 2026
