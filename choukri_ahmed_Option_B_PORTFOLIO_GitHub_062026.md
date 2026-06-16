# Portfolio - Data Engineer

> **Sport Data Solution** - Parcours Data Engineer - Juin 2026

---

## A propos

Data Engineer passionne de sport et de data, j'interviens sur l'ensemble de la chaine de valeur de la donnee : collecte, transformation, stockage, qualite, monitoring et restitution. Ce portfolio presente les projets realises au cours de ma formation et de mes missions professionnelles.

---

## Projets

---

### POC Avantages Sportifs - Sport Data Solution

> **Pipeline de donnees de bout en bout pour un systeme de recompenses sportives**

**Contexte**  
Sport Data Solution souhaitait mettre en place un systeme d'avantages pour recompenser les salaries pratiquant une activite physique reguliere : prime de 5% sur le salaire brut pour les deplacements sportifs domicile-bureau, et 5 jours de bien-etre pour les sportifs actifs.

**Mission**  
Concevoir et implementer le POC complet : infrastructure de donnees, pipeline ETL, tests qualite, orchestration, notifications Slack et dashboard interactif.

**Donnees traitees**
- 161 salaries (donnees RH : salaires, adresses, modes de deplacement)
- 3 592 activites sportives simulees sur 12 mois (9 types de sport)
- Validation des distances domicile-bureau via geocodage (Haversine / cache codes postaux)

**Architecture technique**

```
Sources (Excel RH, CSV Strava simule, cache codes postaux)
    |
    v
Pipeline ETL Python (Extract -> Transform -> Load)
    |
    v
Tests qualite (Great Expectations style - 22 tests)
    |
    v
Base de donnees SQLite (salaries, activites, avantages, logs)
    |
    v
Orchestration Apache Airflow (DAG quotidien 6h)
    |
    v
Restitution (Dashboard Streamlit + Slack Webhook)
```

**Outils utilises**

| Categorie | Outils |
|-----------|--------|
| Langage | Python 3.12 |
| Traitement | Pandas, NumPy |
| Stockage | SQLite (PostgreSQL en prod) |
| Orchestration | Apache Airflow |
| Tests qualite | Great Expectations (style) |
| Notification | Slack Webhook |
| Visualisation | Streamlit, Plotly |
| Documentation | Markdown, GitHub |

**Resultats obtenus**

| Indicateur | Valeur |
|---|---|
| Effectif total | 161 salaries |
| Eligibles prime sportive | 59 salaries (36.6%) |
| Coût primes / an | 148 848 EUR |
| Eligibles journees bien-etre | 111 salaries (69.0%) |
| Jours bien-etre accordes | 555 jours |
| Activites simulees | 3 592 sur 12 mois |
| Tests qualite | 22/22 passes (100%) |
| Anomalies detectees | 9 declarations a verifier |

**Competences demontrees**
- Collecte et analyse des besoins metier (email + note de cadrage)
- Conception d'architecture data de bout en bout
- Developpement pipeline ETL Python (Extract / Transform / Load)
- Validation et tests qualite des donnees (Great Expectations style)
- Orchestration et monitoring (Apache Airflow, logs, alertes email)
- Generation de donnees synthetiques realistes (simulation Strava)
- Notifications automatiques via Slack Webhook
- Dashboard interactif avec parametres ajustables (Streamlit + Plotly)
- Gestion de projet data (planification, suivi, restitution)
- Documentation et versioning GitHub

**Valeur ajoutee**  
Solution parametrable en temps reel (taux de prime, seuil d'activites) sans redeveloppement. Architecture modulaire facilitant la migration vers la production (SQLite -> PostgreSQL, simulation -> vraie API Strava OAuth2). Impact financier estime a **148 848 EUR / an** pour les primes sportives.

**Liens**
- [Repository GitHub](https://github.com/votre-username/poc-sport-data-solution)
- [Dashboard Streamlit](http://localhost:8501) - Demo locale

---

## Stack technique maitrisee

| Domaine | Technologies |
|---------|-------------|
| **Langages** | Python, SQL |
| **Traitement donnees** | Pandas, NumPy |
| **Bases de donnees** | PostgreSQL, SQLite, MySQL |
| **Orchestration** | Apache Airflow |
| **Qualite donnees** | Great Expectations (style) |
| **Visualisation** | Streamlit, Plotly, Power BI |
| **Versionning** | Git, GitHub |
| **APIs** | REST, OAuth2, Webhooks (Slack) |

---

## Competences cles

- **Pipeline ETL de bout en bout** : ingestion, transformation, chargement, tests qualite
- **Architecture data** : conception de bases de donnees relationnelles
- **Qualite des donnees** : tests automatises, detection d'anomalies, documentation
- **Orchestration** : DAGs Airflow, planification, alertes et monitoring
- **Gestion de projet data** : collecte des besoins, planification, suivi, restitution
- **Communication** : dashboard interactifs, rapports, presentations parties prenantes

---

## Contact

**Sport Data Solution** - Montpellier, France  
Email : dataengineer@sportdatasolution.fr  
LinkedIn : [linkedin.com/in/votre-profil](https://linkedin.com/in/votre-profil)  
GitHub : [github.com/votre-username](https://github.com/votre-username)

---

*Portfolio mis a jour en juin 2026*
