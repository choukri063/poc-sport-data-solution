"""
Tests de qualite des donnees - Great Expectations (style)
POC Avantages Sportifs - Sport Data Solution
VERSION CORRIGEE - Adaptee au format reel des donnees
"""
import pandas as pd
import sqlite3
from datetime import datetime

DB = 'sport_data.db'

def run_tests():
    conn = sqlite3.connect(DB)
    sal = pd.read_sql('SELECT * FROM salaries', conn)
    act = pd.read_sql('SELECT * FROM activites', conn)
    ava = pd.read_sql('SELECT * FROM avantages', conn)
    conn.close()

    results = []

    def test(name, passed, detail=""):
        status = "PASS" if passed else "FAIL"
        results.append({'test': name, 'status': status, 'detail': detail})
        print(f"  {status}  {name}" + (f" - {detail}" if detail else ""))

    print("\n-- Tests : Table salaries -------------------------")
    test("ID salarie unique",
         sal['ID salarié'].nunique() == len(sal),
         f"{sal['ID salarié'].nunique()} uniques / {len(sal)} lignes")

    test("Pas de doublons nom+prenom",
         sal.duplicated(['Nom','Prénom']).sum() == 0,
         f"{sal.duplicated(['Nom','Prénom']).sum()} doublons")

    test("Salaire brut positif",
         (sal['Salaire brut'] > 0).all(),
         f"min={sal['Salaire brut'].min():.0f} EUR")

    test("Salaire brut dans fourchette realiste [20k-200k]",
         sal['Salaire brut'].between(20000, 200000).all(),
         f"hors-fourchette : {(~sal['Salaire brut'].between(20000,200000)).sum()}")

    test("Pas de nom vide",
         sal['Nom'].notna().all() and (sal['Nom'].str.strip() != '').all())

    test("Moyen de deplacement valide",
         sal['Moyen de déplacement'].isin([
             'Marche/running','Vélo/Trottinette/Autres',
             'Transports en commun','véhicule thermique/électrique']).all(),
         f"valeurs inconnues : {sal[~sal['Moyen de déplacement'].isin(['Marche/running','Vélo/Trottinette/Autres','Transports en commun','véhicule thermique/électrique'])]['Moyen de déplacement'].unique()}")

    print("\n-- Tests : Table activites Strava -----------------")
    test("ID salarie present dans activites",
         act['id_salarie'].notna().all(),
         f"{act['id_salarie'].isna().sum()} valeurs manquantes")

    test("Distance non negative (quand renseignee)",
         (act['distance_km'].dropna() >= 0).all(),
         f"min distance = {act['distance_km'].dropna().min():.1f} km")

    test("Distance raisonnable (< 200 km)",
         (act['distance_km'].dropna() < 200).all(),
         f"max = {act['distance_km'].dropna().max():.1f} km")

    test("Duree positive",
         (act['duree_minutes'] > 0).all(),
         f"min = {act['duree_minutes'].min()} min")

    test("Duree raisonnable (< 24h)",
         (act['duree_minutes'] <= 1440).all(),
         f"max = {act['duree_minutes'].max()/60:.1f} h")

    test("Dates valides (format parseable)",
         pd.to_datetime(act['date'], errors='coerce').notna().all(),
         f"{pd.to_datetime(act['date'], errors='coerce').isna().sum()} dates invalides")

    test("ID salarie en activites reference un salarie connu",
         act['id_salarie'].isin(sal['ID salarié']).all(),
         f"inconnus : {(~act['id_salarie'].isin(sal['ID salarié'])).sum()}")

    test("Sport dans liste referentielle",
         act['sport'].isin(['running','cycling','swimming','walking','tennis',
             'football','hiking','yoga','crossfit']).all(),
         f"valeurs inconnues : {act[~act['sport'].isin(['running','cycling','swimming','walking','tennis','football','hiking','yoga','crossfit'])]['sport'].unique()}")

    test("Intensite valide",
         act['intensite'].isin(['soutenu','modere','leger']).all(),
         f"valeurs inconnues : {act[~act['intensite'].isin(['soutenu','modere','leger'])]['intensite'].unique()}")

    test("Calories positives",
         (act['calories'] > 0).all(),
         f"min = {act['calories'].min()} cal")

    print("\n-- Tests : Table avantages ------------------------")
    test("Montant prime >= 0",
         (ava['montant_prime'] >= 0).all())

    test("Montant prime = 5% salaire si eligible",
         (ava[ava['eligible_prime'] == 1].apply(
             lambda r: abs(r['montant_prime'] - r['Salaire brut']*0.05) < 1, axis=1
         ).all()))

    test("Jours bien-etre = 0 ou 5 uniquement",
         ava['jours_bienetre'].isin([0, 5]).all())

    test("Pas d'eligible prime avec anomalie transport",
         ((ava['eligible_prime']==1) & (ava['validation_transport']=='anomalie')).sum() == 0)

    test("Nombre d'activites coherent",
         ava['nb_activites_annee'].between(0, 100).all(),
         f"min={ava['nb_activites_annee'].min()}, max={ava['nb_activites_annee'].max()}")

    test("Correlation prime/bien-etre coherente",
         (ava[ava['eligible_prime']==1]['nb_activites_annee'].mean() > 
          ava[ava['eligible_prime']==0]['nb_activites_annee'].mean()),
         f"moyenne eligibles: {ava[ava['eligible_prime']==1]['nb_activites_annee'].mean():.1f}, "
         f"non-eligibles: {ava[ava['eligible_prime']==0]['nb_activites_annee'].mean():.1f}")

    # Resume
    nb_pass = sum(1 for r in results if 'PASS' in r['status'])
    nb_fail = sum(1 for r in results if 'FAIL' in r['status'])
    print(f"\n{'='*50}")
    print(f"  Resultat : {nb_pass} tests passes, {nb_fail} echecs")
    print(f"{'='*50}")
    return results

if __name__ == '__main__':
    run_tests()