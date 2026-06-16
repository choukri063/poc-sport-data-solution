import pandas as pd
import sqlite3
import math
import random
import logging
from datetime import datetime
from pathlib import Path

BUREAU_LAT, BUREAU_LON = 43.5735, 3.9021
PRIME_PCT = 0.05
BIENETRE_MIN = 15
BIENETRE_JOURS = 5
MARCHE_MAX_KM = 15
VELO_MAX_KM = 25
DB_PATH = "sport_data.db"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

COORDS_MAP = {
    "34970":(43.5735,3.9021),"34470":(43.5583,3.9289),"34000":(43.6047,3.8772),
    "34090":(43.6200,3.8500),"34080":(43.6350,3.8200),"34130":(43.6188,4.0076),
    "30900":(43.8367,4.3601),"34280":(43.5617,4.0858),"34920":(43.6333,3.9500),
    "34830":(43.6667,3.8833),"34750":(43.5333,3.8667),"34690":(43.5500,3.7667),
    "34250":(43.5283,3.9272),"34740":(43.5667,3.8667),"34170":(43.6333,3.8000),
}

def haversine(la1, lo1, la2, lo2):
    R = 6371
    dlat = math.radians(la2 - la1)
    dlon = math.radians(lo2 - lo1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(la1)) * math.cos(math.radians(la2)) * math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def get_distance_km(adresse):
    if pd.isna(adresse):
        return None
    for p in str(adresse).split(","):
        for w in p.strip().split():
            if len(w) == 5 and w.isdigit() and w in COORDS_MAP:
                la, lo = COORDS_MAP[w]
                return round(haversine(BUREAU_LAT, BUREAU_LON, la, lo), 2)
    return None

def extract(rh_path, sport_path, strava_path):
    log.info("Extract RH + Sport + Strava")
    df_rh = pd.read_excel(rh_path)
    df_sport = pd.read_excel(sport_path)
    df_strava = pd.read_csv(strava_path)
    return df_rh, df_sport, df_strava

def transform(df_rh, df_sport, df_strava):
    log.info("Transform : validation + éligibilité")
    df = df_rh.merge(df_sport, on="ID salarié", how="left")
    df["distance_km"] = df["Adresse du domicile"].apply(get_distance_km)

    def val(row):
        m = row["Moyen de déplacement"]
        d = row["distance_km"]
        if d is None:
            return "non_calcule"
        if m == "Marche/running":
            return "ok" if d <= MARCHE_MAX_KM else "anomalie"
        elif m == "Vélo/Trottinette/Autres":
            return "ok" if d <= VELO_MAX_KM else "anomalie"
        return "non_concerne"

    df["validation_transport"] = df.apply(val, axis=1)
    df["eligible_prime"] = df["Moyen de déplacement"].isin(["Marche/running","Vélo/Trottinette/Autres"]) & (df["validation_transport"] == "ok")
    df["montant_prime"] = df.apply(lambda r: round(r["Salaire brut"] * PRIME_PCT, 2) if r["eligible_prime"] else 0.0, axis=1)

    # CORRECTION: strava_activities.csv utilise 'id_salarie' (minuscule, sans accent)
    # et non 'ID salarié' comme dans les fichiers Excel
    act = df_strava.groupby("id_salarie").size().reset_index(name="nb_activites_annee")
    act["eligible_bienetre"] = act["nb_activites_annee"] >= BIENETRE_MIN
    act["jours_bienetre"] = act["eligible_bienetre"].apply(lambda x: BIENETRE_JOURS if x else 0)

    # CORRECTION: merge sur 'id_salarie' pour correspondre à la colonne de strava_activities.csv
    ava = df[["ID salarié","Nom","Prénom","Salaire brut","eligible_prime","montant_prime","distance_km","Moyen de déplacement","validation_transport"]].merge(
        act, left_on="ID salarié", right_on="id_salarie", how="left")
    ava = ava.drop(columns=["id_salarie"])  # Supprime la colonne dupliquée après merge
    ava["nb_activites_annee"] = ava["nb_activites_annee"].fillna(0).astype(int)
    ava["eligible_bienetre"] = ava["eligible_bienetre"].fillna(False)
    ava["jours_bienetre"] = ava["jours_bienetre"].fillna(0).astype(int)

    log.info("  → %d éligibles prime | %d éligibles bien-être | %d anomalies",
             ava["eligible_prime"].sum(), ava["eligible_bienetre"].sum(),
             (ava["validation_transport"] == "anomalie").sum())
    return df, ava

def load(df_sal, df_ava, df_strava, db_path):
    log.info("Load → SQLite %s", db_path)
    conn = sqlite3.connect(db_path)
    df_sal.to_sql("salaries", conn, if_exists="replace", index=False)
    df_strava.to_sql("activites", conn, if_exists="replace", index=False)
    df_ava.to_sql("avantages", conn, if_exists="replace", index=False)
    conn.close()
    df_ava.to_csv("validation_complete.csv", index=False)

def rapport(df_ava):
    cp = df_ava["montant_prime"].sum()
    print(f"\n{'='*52}\n  RAPPORT – AVANTAGES SPORTIFS\n{'='*52}")
    print(f"  Effectif total        : {len(df_ava)} salariés")
    print(f"  Éligibles prime       : {df_ava['eligible_prime'].sum()}")
    print(f"  Coût prime annuel     : {cp:>10,.0f} €")
    print(f"{'='*52}")

def run(rh_path, sport_path, strava_path, db_path=DB_PATH):
    log.info("=== Pipeline ETL démarré ===")
    df_rh, df_sport, df_strava = extract(rh_path, sport_path, strava_path)
    df_sal, df_ava = transform(df_rh, df_sport, df_strava)
    load(df_sal, df_ava, df_strava, db_path)
    rapport(df_ava)
    log.info("=== Pipeline terminé ===")
    return df_sal, df_ava

if __name__ == "__main__":
    # CORRECTION: noms de fichiers sans accents (é → e)
    run("Donnees-RH.xlsx",
        "Donnees-Sportive.xlsx",
        "strava_activities.csv")