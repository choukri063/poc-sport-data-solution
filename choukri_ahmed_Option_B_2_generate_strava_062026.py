# generate_strava_data.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

print("="*60)
print("🏃 GÉNÉRATION DES DONNÉES SPORTIVES (STRAVA)")
print("="*60)

# Configuration
SPORTS = {
    'running': {
        'duree_min': 20, 'duree_max': 90, 
        'distance_km': (3, 15), 
        'calories_par_min': 10,
        'intensite': 'soutenu'
    },
    'cycling': {
        'duree_min': 30, 'duree_max': 180, 
        'distance_km': (8, 40), 
        'calories_par_min': 8,
        'intensite': 'soutenu'
    },
    'swimming': {
        'duree_min': 20, 'duree_max': 60, 
        'distance_km': (0.5, 3), 
        'calories_par_min': 9,
        'intensite': 'soutenu'
    },
    'walking': {
        'duree_min': 15, 'duree_max': 60, 
        'distance_km': (1, 5), 
        'calories_par_min': 5,
        'intensite': 'modere'
    },
    'tennis': {
        'duree_min': 45, 'duree_max': 120, 
        'distance_km': (0, 2), 
        'calories_par_min': 8,
        'intensite': 'soutenu'
    },
    'football': {
        'duree_min': 60, 'duree_max': 90, 
        'distance_km': (2, 6), 
        'calories_par_min': 9,
        'intensite': 'soutenu'
    },
    'hiking': {
        'duree_min': 60, 'duree_max': 240, 
        'distance_km': (5, 20), 
        'calories_par_min': 7,
        'intensite': 'soutenu'
    },
    'yoga': {
        'duree_min': 30, 'duree_max': 90, 
        'distance_km': (0, 0), 
        'calories_par_min': 4,
        'intensite': 'leger'
    },
    'crossfit': {
        'duree_min': 30, 'duree_max': 60, 
        'distance_km': (0, 1), 
        'calories_par_min': 12,
        'intensite': 'soutenu'
    }
}

# Charger les salariés
df_employees = pd.read_csv('validation_complete.csv')
print(f"\n📂 {len(df_employees)} salariés chargés")

# Générer des activités sur 12 mois
start_date = datetime(2024, 6, 1)
end_date = datetime(2025, 5, 31)
total_days = (end_date - start_date).days

activities = []
np.random.seed(42)  # Pour reproductibilité

for idx, emp in df_employees.iterrows():
    # Les salariés éligibles à la prime sont plus sportifs
    if emp['eligible_prime']:
        nb_activities = np.random.poisson(35)  # Moyenne 35 activités/an
    else:
        nb_activities = np.random.poisson(15)  # Moyenne 15 activités/an
    
    nb_activities = max(5, min(60, nb_activities))
    
    # Sports préférés (plus variés pour les sportifs)
    if emp['eligible_prime']:
        preferred_sports = random.sample(list(SPORTS.keys()), k=random.randint(2, 4))
    else:
        preferred_sports = random.sample(list(SPORTS.keys()), k=random.randint(1, 3))
    
    for _ in range(nb_activities):
        # Date aléatoire
        random_days = random.randint(0, total_days)
        activity_date = start_date + timedelta(days=random_days)
        
        # Choix du sport
        sport = random.choice(preferred_sports)
        sport_config = SPORTS[sport]
        
        # Durée
        duration = random.randint(sport_config['duree_min'], sport_config['duree_max'])
        
        # Distance
        if sport_config['distance_km'][1] > 0:
            distance = round(random.uniform(sport_config['distance_km'][0], sport_config['distance_km'][1]), 1)
        else:
            distance = None
        
        # Calories
        calories = int(duration * sport_config['calories_par_min'] * random.uniform(0.8, 1.2))
        
        activities.append({
            'id_salarie': emp['id_salarie'],
            'nom': emp['nom'],
            'prenom': emp['prenom'],
            'date': activity_date.strftime('%Y-%m-%d'),
            'sport': sport,
            'duree_minutes': duration,
            'distance_km': distance,
            'calories': calories,
            'intensite': sport_config['intensite']
        })

df_activities = pd.DataFrame(activities)

print(f"\n✅ {len(df_activities):,} activités générées")
print(f"   • Période : {start_date.strftime('%d/%m/%Y')} → {end_date.strftime('%d/%m/%Y')}")
print(f"   • Sports : {', '.join(df_activities['sport'].unique())}")

# Statistiques par sport
print(f"\n📊 Activités par sport :")
sport_stats = df_activities.groupby('sport').size().sort_values(ascending=False)
for sport, count in sport_stats.items():
    print(f"   • {sport:12} : {count:4} activités")

# Statistiques par intensité
print(f"\n⚡ Répartition par intensité :")
intensity_stats = df_activities['intensite'].value_counts()
for intensite, count in intensity_stats.items():
    pct = count/len(df_activities)*100
    print(f"   • {intensite:8} : {count:4} ({pct:.1f}%)")

# Sauvegarde
df_activities.to_csv('strava_activities.csv', index=False)
print(f"\n💾 Sauvegardé : strava_activities.csv")

# Calcul de l'éligibilité pour les jours bien-être
print(f"\n" + "="*60)
print(f"🏖️ ÉLIGIBILITÉ AUX 5 JOURS BIEN-ÊTRE")
print(f"="*60)

# Comptage des activités soutenues par salarié
intense_activities = df_activities[df_activities['intensite'] == 'soutenu']
activities_per_employee = intense_activities.groupby('id_salarie').size().reset_index(name='nb_activites_soutenues')

# Fusion avec tous les salariés
df_wellness = df_employees[['id_salarie', 'nom', 'prenom', 'bu', 'eligible_prime']].merge(
    activities_per_employee, on='id_salarie', how='left'
)
df_wellness['nb_activites_soutenues'] = df_wellness['nb_activites_soutenues'].fillna(0).astype(int)
df_wellness['eligible_wellness'] = df_wellness['nb_activites_soutenues'] >= 15

eligibles_wellness = df_wellness['eligible_wellness'].sum()
print(f"\n   • Salariés avec ≥15 activités soutenues : {eligibles_wellness}/{len(df_wellness)}")
print(f"   • Taux d'éligibilité : {eligibles_wellness/len(df_wellness)*100:.1f}%")

# Détail par BU
print(f"\n🏢 Détail par Business Unit :")
bu_wellness = df_wellness.groupby('bu').agg({
    'eligible_wellness': ['count', 'sum']
})
bu_wellness.columns = ['total', 'eligibles']
bu_wellness['taux'] = (bu_wellness['eligibles'] / bu_wellness['total'] * 100).round(1)
print(bu_wellness.sort_values('taux', ascending=False))

# Lien entre prime sportive et activité sportive
print(f"\n🔗 Corrélation avec la prime sportive :")
correlation = pd.crosstab(
    df_wellness['eligible_prime'], 
    df_wellness['eligible_wellness'],
    normalize='index'
) * 100
correlation.columns = ['Non éligible wellness', 'Éligible wellness']
correlation.index = ['Non éligible prime', 'Éligible prime']
print(correlation.round(1))

# Sauvegarde
df_wellness.to_csv('wellness_eligibility.csv', index=False)
print(f"\n💾 Sauvegardé : wellness_eligibility.csv")

print("\n" + "="*60)
print("✅ Génération des données Strava terminée !")
print("="*60)