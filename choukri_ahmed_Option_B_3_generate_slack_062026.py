import pandas as pd
import random

print("="*60)
print("💬 GÉNÉRATION DES MESSAGES SLACK")
print("="*60)

df_activities = pd.read_csv('strava_activities.csv')
df_activities['date'] = pd.to_datetime(df_activities['date'])
df_salaries = pd.read_excel('Donnees-RH.xlsx')

MESSAGES = {
    'running': [
        "Bravo {prenom} {nom} ! Tu viens de courir {distance} km en {duree} min ! Quelle énergie ! 🏃‍♀️🏅",
        "Bravo {prenom} {nom} ! {distance} km en {duree} minutes, tu assures ! 🔥🏃‍♂️"
    ],
    'hiking': [
        "Magnifique {prenom} {nom} ! Une randonnée de {distance} km terminée et un nouveau spot à découvrir ! 🥾🏔️",
        "Bravo {prenom} {nom} ! {distance} km de randonnée, quelle belle aventure ! 🥾✨"
    ],
    'cycling': [
        "Bravo {prenom} {nom} ! Tu viens de parcourir {distance} km à vélo ! 🚴‍♂️💨",
        "Félicitations {prenom} {nom} ! {distance} km à vélo, tu déchires ! 🚴‍♀️🔥"
    ],
    'swimming': [
        "Bravo {prenom} {nom} ! {distance} km en natation, quelle endurance ! 🏊‍♀️💦",
        "Félicitations {prenom} {nom} ! Séance de natation de {duree} minutes ! 🏊‍♂️🏅"
    ],
    'walking': [
        "Bravo {prenom} {nom} ! Marche de {distance} km, excellent pour la santé ! 🚶‍♀️🌿",
        "Félicitations {prenom} {nom} ! {distance} km de marche, tu as profité du grand air ! 🚶‍♂️✨"
    ],
    'tennis': [
        "Bravo {prenom} {nom} ! Match de tennis de {duree} minutes ! 🎾🔥",
        "Félicitations {prenom} {nom} ! {duree} minutes sur le court ! 🎾🏆"
    ],
    'football': [
        "Bravo {prenom} {nom} ! Match de foot de {duree} minutes ! ⚽🥅",
        "Félicitations {prenom} {nom} ! {duree} minutes sur le terrain ! ⚽🔥"
    ],
    'yoga': [
        "Bravo {prenom} {nom} ! Séance de yoga de {duree} minutes ! 🧘‍♀️✨",
        "Félicitations {prenom} {nom} ! {duree} minutes de yoga ! 🧘‍♂️🌿"
    ],
    'crossfit': [
        "Bravo {prenom} {nom} ! Séance crossfit de {duree} minutes ! 💪🔥",
        "Félicitations {prenom} {nom} ! {duree} minutes de crossfit ! 🏋️‍♂️💥"
    ]
}

def get_message(row):
    sport = row['sport']
    prenom = row['prenom']
    nom = row['nom']
    duree = row['duree_minutes']
    distance = round(row['distance_km'], 1) if pd.notna(row['distance_km']) and row['distance_km'] > 0 else None
    
    if sport in MESSAGES:
        template = random.choice(MESSAGES[sport])
        if distance:
            return template.format(prenom=prenom, nom=nom, distance=distance, duree=duree)
        else:
            return template.format(prenom=prenom, nom=nom, duree=duree)
    else:
        return f"Bravo {prenom} {nom} pour ta séance de {sport} ! 🏅"

df_activities['slack_message'] = df_activities.apply(get_message, axis=1)

df_activities[['date', 'prenom', 'nom', 'sport', 'distance_km', 'duree_minutes', 'slack_message']].to_csv(
    'slack_messages_final.csv', index=False
)

print(f"\n✅ {len(df_activities)} messages générés")
print(f"💾 Fichier : slack_messages_final.csv")

print("\n📝 Exemples :")
print("-"*40)
for _, row in df_activities.head(10).iterrows():
    print(f"   {row['slack_message']}")

print("\n" + "="*60)
print("✅ Terminé")
print("="*60)