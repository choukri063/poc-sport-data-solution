"""
DAG Airflow – Pipeline Avantages Sportifs
Sport Data Solution
Execution quotidienne avec monitoring et alertes
VERSION CORRIGEE - 2026-06-15
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.email import EmailOperator
from airflow.utils.trigger_rule import TriggerRule

# -- Parametres par defaut -------------------------------
default_args = {
    'owner': 'sport_data_solution',
    'depends_on_past': False,
    'email': ['juliette@sportdatasolution.fr'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

# -- Fonctions de taches -------------------------------
def task_extract_rh(**ctx):
    """Extraction des donnees RH depuis la source."""
    import pandas as pd
    import logging
    log = logging.getLogger(__name__)
    # CORRECTION: nom de fichier sans accent
    df = pd.read_excel('/data/inputs/Donnees-RH.xlsx')
    log.info("RH extrait : %d lignes", len(df))
    ctx['ti'].xcom_push(key='nb_salaries', value=len(df))
    df.to_parquet('/tmp/rh_raw.parquet', index=False)


def task_extract_strava(**ctx):
    """Extraction des activites Strava (simulation ou API reelle)."""
    import pandas as pd
    # CORRECTION: nom de fichier correspondant au generateur
    df = pd.read_csv('/data/inputs/strava_activities.csv')
    ctx['ti'].xcom_push(key='nb_activites', value=len(df))
    df.to_parquet('/tmp/strava_raw.parquet', index=False)


def task_validate_distances(**ctx):
    """
    Validation des distances domicile-bureau via cache de codes postaux.
    Regles : Marche <= 15 km | Velo <= 25 km
    """
    import pandas as pd, math, logging
    log = logging.getLogger(__name__)

    BUREAU_LAT, BUREAU_LON = 43.5735, 3.9021
    COORDS_MAP = {
        "34970":(43.5735,3.9021),"34470":(43.5583,3.9289),
        "34000":(43.6047,3.8772),"34090":(43.6200,3.8500),
        "34080":(43.6350,3.8200),"34130":(43.6188,4.0076),
        "30900":(43.8367,4.3601),"34280":(43.5617,4.0858),
        "34920":(43.6333,3.9500),"34830":(43.6667,3.8833),
        "34750":(43.5333,3.8667),"34690":(43.5500,3.7667),
        "34250":(43.5283,3.9272),"34740":(43.5667,3.8667),
    }

    def haversine(la1,lo1,la2,lo2):
        R=6371; dlat=math.radians(la2-la1); dlon=math.radians(lo2-lo1)
        a=math.sin(dlat/2)**2+math.cos(math.radians(la1))*math.cos(math.radians(la2))*math.sin(dlon/2)**2
        return R*2*math.atan2(math.sqrt(a),math.sqrt(1-a))

    def get_dist(adr):
        for p in adr.split(','):
            for w in p.strip().split():
                if len(w)==5 and w.isdigit() and w in COORDS_MAP:
                    la,lo = COORDS_MAP[w]
                    return round(haversine(BUREAU_LAT,BUREAU_LON,la,lo),2)
        return None

    df = pd.read_parquet('/tmp/rh_raw.parquet')
    df['distance_km'] = df['Adresse du domicile'].apply(get_dist)

    def valider(row):
        m,d = row['Moyen de deplacement'], row['distance_km']
        if d is None: return 'non_calcule'
        if m == 'Marche/running': return 'ok' if d <= 15 else 'anomalie'
        elif m == 'Velo/Trottinette/Autres': return 'ok' if d <= 25 else 'anomalie'
        return 'non_concerne'

    df['validation_transport'] = df.apply(valider, axis=1)
    anomalies = (df['validation_transport'] == 'anomalie').sum()
    log.info("Anomalies detectees : %d", anomalies)
    ctx['ti'].xcom_push(key='nb_anomalies', value=int(anomalies))
    df.to_parquet('/tmp/rh_validated.parquet', index=False)


def task_compute_eligibility(**ctx):
    """Calcule l'eligibilite aux deux avantages avec parametres configurables."""
    import pandas as pd
    from airflow.models import Variable

    PRIME_PCT   = float(Variable.get('prime_pct',   default_var=0.05))
    BE_MIN_ACT  = int(Variable.get('be_min_activites', default_var=15))
    BE_JOURS    = int(Variable.get('be_nb_jours',  default_var=5))

    rh = pd.read_parquet('/tmp/rh_validated.parquet')
    strava = pd.read_parquet('/tmp/strava_raw.parquet')

    rh['eligible_prime'] = (
        rh['Moyen de deplacement'].isin(['Marche/running','Velo/Trottinette/Autres'])
        & (rh['validation_transport'] == 'ok')
    )
    rh['montant_prime'] = rh.apply(
        lambda r: round(r['Salaire brut'] * PRIME_PCT, 2) if r['eligible_prime'] else 0.0, axis=1
    )

    # CORRECTION: strava_activities.csv utilise 'id_salarie' et non 'ID salarie'
    act = strava.groupby('id_salarie').size().reset_index(name='nb_activites')
    act['eligible_bienetre'] = act['nb_activites'] >= BE_MIN_ACT
    act['jours_bienetre'] = act['eligible_bienetre'].apply(lambda x: BE_JOURS if x else 0)

    # CORRECTION: merge avec left_on/right_on car colonnes differentes
    avantages = rh.merge(act, left_on='ID salarie', right_on='id_salarie', how='left')
    avantages = avantages.drop(columns=['id_salarie'])  # supprime colonne dupliquee
    avantages['nb_activites'] = avantages['nb_activites'].fillna(0).astype(int)
    avantages['eligible_bienetre'] = avantages['eligible_bienetre'].fillna(False)
    avantages['jours_bienetre'] = avantages['jours_bienetre'].fillna(0).astype(int)
    avantages.to_parquet('/tmp/avantages.parquet', index=False)

    ctx['ti'].xcom_push(key='nb_eligibles_prime', value=int(avantages['eligible_prime'].sum()))
    ctx['ti'].xcom_push(key='cout_primes', value=float(avantages['montant_prime'].sum()))
    ctx['ti'].xcom_push(key='nb_eligibles_be', value=int(avantages['eligible_bienetre'].sum()))


def task_load_db(**ctx):
    """Charge les donnees transformees dans PostgreSQL/SQLite."""
    import pandas as pd
    from sqlalchemy import create_engine
    from airflow.models import Variable

    DB_URL = Variable.get('db_url', default_var='sqlite:////data/sport_data.db')
    engine = create_engine(DB_URL)

    rh = pd.read_parquet('/tmp/rh_validated.parquet')
    strava = pd.read_parquet('/tmp/strava_raw.parquet')
    avantages = pd.read_parquet('/tmp/avantages.parquet')

    rh.to_sql('salaries', engine, if_exists='replace', index=False)
    strava.to_sql('activites', engine, if_exists='replace', index=False)
    avantages.to_sql('avantages', engine, if_exists='replace', index=False)

    # Log d'execution pipeline
    pd.DataFrame([{
        'run_at': datetime.now().isoformat(),
        'nb_salaries': len(rh),
        'nb_activites': len(strava),
        'nb_eligibles_prime': ctx['ti'].xcom_pull(key='nb_eligibles_prime'),
        'cout_primes': ctx['ti'].xcom_pull(key='cout_primes'),
        'nb_eligibles_bienetre': ctx['ti'].xcom_pull(key='nb_eligibles_be'),
        'nb_anomalies': ctx['ti'].xcom_pull(key='nb_anomalies'),
    }]).to_sql('pipeline_logs', engine, if_exists='append', index=False)


def task_run_quality_tests(**ctx):
    """Lance les tests de qualite sur les donnees chargees."""
    import subprocess, sys
    result = subprocess.run(
        [sys.executable, '/app/poc_sport/tests_qualite.py'],
        capture_output=True, text=True
    )
    if '0 echecs' not in result.stdout and '0 FAIL' not in result.stdout:
        raise ValueError(f"Tests qualite echoues !\n{result.stdout}")


def task_send_slack_messages(**ctx):
    """
    Envoie les messages Slack pour les nouvelles activites (24h glissantes).
    En production : appel au Slack Webhook avec le token configure.
    """
    import pandas as pd, requests, logging
    from airflow.models import Variable

    SLACK_WEBHOOK = Variable.get('slack_webhook_url', default_var=None)
    if not SLACK_WEBHOOK:
        logging.getLogger(__name__).warning("Slack webhook non configure - messages ignores")
        return

    strava = pd.read_parquet('/tmp/strava_raw.parquet')
    rh = pd.read_parquet('/tmp/rh_validated.parquet')
    sal_map = rh.set_index('ID salarie')[['Prenom','Nom']].to_dict('index')

    EMOJIS = {"Course a pied":"🏃🔥","Randonnee":"🌄","Natation":"🏊",
              "Tennis":"🎾","Football":"⚽","Rugby":"🏉","Voile":"⛵","Escalade":"🧗"}

    # Filtre les activites des dernieres 24h
    strava['dt'] = pd.to_datetime(strava['date'], errors='coerce')
    recent = strava[strava['dt'] >= pd.Timestamp.now() - pd.Timedelta(hours=24)]

    for _, row in recent.iterrows():
        sal = sal_map.get(row['id_salarie'])
        if not sal: continue
        # CORRECTION: mapping des noms de sports
        sport_display = row['sport'].replace('running', 'Course a pied').replace('hiking', 'Randonnee').replace('swimming', 'Natation')
        emoji = EMOJIS.get(sport_display, '🏅')
        dist_km = round(row['distance_km'], 1) if pd.notna(row['distance_km']) else None
        mins = row['duree_minutes']
        msg = f"Bravo {sal['Prenom']} {sal['Nom']} ! "
        msg += f"{dist_km} km en {mins} min de {sport_display} ! {emoji}" if dist_km else f"Seance {sport_display} - {mins} min ! {emoji}"
        requests.post(SLACK_WEBHOOK, json={"text": msg}, timeout=5)


def task_check_anomalies(**ctx):
    """Leve une alerte si trop d'anomalies de declaration."""
    nb = ctx['ti'].xcom_pull(key='nb_anomalies', task_ids='validate_distances')
    SEUIL = 10
    if nb and int(nb) > SEUIL:
        raise ValueError(f"{nb} anomalies detectees (seuil = {SEUIL}). Verification manuelle requise.")


# -- DAG -------------------------------
with DAG(
    dag_id='poc_avantages_sportifs',
    default_args=default_args,
    description='Pipeline ETL Avantages Sportifs - Sport Data Solution',
    schedule_interval='0 6 * * *',   # Tous les jours a 6h
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=['poc', 'rh', 'sport', 'etl'],
) as dag:

    extract_rh      = PythonOperator(task_id='extract_rh',      python_callable=task_extract_rh)
    extract_strava  = PythonOperator(task_id='extract_strava',  python_callable=task_extract_strava)
    validate_dist   = PythonOperator(task_id='validate_distances', python_callable=task_validate_distances)
    compute_elig    = PythonOperator(task_id='compute_eligibility', python_callable=task_compute_eligibility)
    check_anom      = PythonOperator(task_id='check_anomalies', python_callable=task_check_anomalies)
    load_db         = PythonOperator(task_id='load_database',   python_callable=task_load_db)
    quality_tests   = PythonOperator(task_id='quality_tests',   python_callable=task_run_quality_tests)
    slack_notifs    = PythonOperator(task_id='slack_notifications', python_callable=task_send_slack_messages)

    alert_email = EmailOperator(
        task_id='alert_anomalies_email',
        to='juliette@sportdatasolution.fr',
        subject='[POC Sport] Anomalies detectees - verification requise',
        html_content="""
        <p>Bonjour Juliette,</p>
        <p>Le pipeline a detecte des anomalies dans les declarations de transport.</p>
        <p>Merci de consulter le dashboard Streamlit pour les details.</p>
        """,
        trigger_rule=TriggerRule.ONE_FAILED,
    )

    # Dependances
    [extract_rh, extract_strava] >> validate_dist >> compute_elig
    compute_elig >> check_anom >> load_db >> quality_tests >> slack_notifs
    check_anom >> alert_email