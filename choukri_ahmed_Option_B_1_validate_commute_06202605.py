# validate_commute.py - VERSION FINALE OPTIMISÉE
import pandas as pd
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import time
import re

# Configuration
BUREAU_COORDS = (43.5868926, 3.9190444)  # 1362 Avenue des Platanes, Lattes
BUREAU_ADDRESS = "1362 Avenue des Platanes, Lattes, France"

# Mapping intelligent des modes de transport
SPORT_KEYWORDS = {
    'marche': ['marche', 'walking', 'pied'],
    'course': ['course', 'running', 'run', 'jogging'],
    'vélo': ['vélo', 'velo', 'bike', 'bicycle', 'cyclisme', 'vtt'],
    'trottinette': ['trottinette', 'scooter', 'trotti']
}

MAX_DISTANCES = {
    'marche': 15,
    'course': 15,
    'vélo': 25,
    'trottinette': 25
}

geolocator = Nominatim(user_agent="commute_validation_poc")

def extract_sport_mode(mode_text):
    """Extrait le mode sportif à partir du texte"""
    if pd.isna(mode_text) or not mode_text:
        return None, False
    
    mode_lower = str(mode_text).lower()
    
    # Recherche de mots-clés
    for sport_mode, keywords in SPORT_KEYWORDS.items():
        if any(keyword in mode_lower for keyword in keywords):
            return sport_mode, True
    
    return None, False

def geocode_address(address):
    """Géocode une adresse avec gestion d'erreur"""
    try:
        location = geolocator.geocode(address, timeout=10)
        if location:
            return (location.latitude, location.longitude)
        return None
    except Exception as e:
        print(f"      ⚠️ Erreur: {str(e)[:50]}")
        return None
    finally:
        time.sleep(1.1)  # Légère marge pour respecter la limite

def calculate_distance(employee_addr, bureau_coords):
    """Calcule la distance entre domicile et bureau"""
    coords_employee = geocode_address(employee_addr)
    if coords_employee:
        return geodesic(bureau_coords, coords_employee).kilometers
    return None

# Chargement des données
print("="*60)
print("🏢 VALIDATION PRIME SPORTIVE - MOBILITÉ DOUCE")
print("="*60)

print("\n📂 Chargement du fichier RH...")
df = pd.read_excel('Données-RH.xlsx')
print(f"✅ {len(df)} salariés chargés")

# Nettoyage des colonnes
df.columns = df.columns.str.lower().str.replace(' ', '_')
print(f"Colonnes: {', '.join(df.columns)}\n")

# Analyse des modes de transport uniques
print("📊 Analyse des modes de transport déclarés :")
modes_uniques = df['moyen_de_déplacement'].dropna().unique()
for mode in sorted(modes_uniques):
    sport_mode, is_sport = extract_sport_mode(mode)
    status = "🏃 SPORTIF" if is_sport else "🚗 NON SPORTIF"
    print(f"  • '{mode}' → {status}" + (f" (catégorie: {sport_mode})" if is_sport else ""))

print("\n" + "-"*60)
print("📍 Géocodage des adresses et calcul des distances...")
print("⏱️  Temps estimé: ~3 minutes (1 requête/seconde)")
print("-"*60)

results = []

for idx, row in df.iterrows():
    # Extraction des données
    nom_complet = f"{row['prénom']} {row['nom']}"
    adresse = row['adresse_du_domicile']
    mode_original = row['moyen_de_déplacement']
    
    # Ajout de "France" si nécessaire
    if 'France' not in adresse:
        adresse_complete = f"{adresse}, France"
    else:
        adresse_complete = adresse
    
    # Déterminer si le mode est sportif
    sport_mode, is_sport = extract_sport_mode(mode_original)
    
    print(f"\n[{idx+1}/{len(df)}] {nom_complet}")
    print(f"   📍 Domicile: {adresse[:60]}...")
    print(f"   🚲 Mode: {mode_original}")
    
    if not is_sport:
        # Non sportif - directement non éligible
        distance = None
        eligible = False
        raison = "Mode de déplacement non sportif (voiture ou transports en commun)"
        print(f"   ❌ NON ÉLIGIBLE: {raison}")
    else:
        # Mode sportif - calculer la distance
        print(f"   🏃 Mode sportif détecté: {sport_mode}")
        distance = calculate_distance(adresse_complete, BUREAU_COORDS)
        
        if distance is None:
            eligible = False
            raison = "Adresse non trouvée ou erreur de géocodage"
            print(f"   ❌ NON ÉLIGIBLE: {raison}")
        elif distance <= MAX_DISTANCES[sport_mode]:
            eligible = True
            raison = f"✅ ÉLIGIBLE - {distance:.1f}km en {sport_mode} (limite: {MAX_DISTANCES[sport_mode]}km)"
            print(f"   ✅ ÉLIGIBLE: {distance:.1f}km ≤ {MAX_DISTANCES[sport_mode]}km")
        else:
            eligible = False
            raison = f"❌ Distance trop élevée: {distance:.1f}km > {MAX_DISTANCES[sport_mode]}km"
            print(f"   ❌ NON ÉLIGIBLE: {raison}")
    
    # Stockage des résultats
    results.append({
        'id_salarie': row['id_salarié'],
        'nom': row['nom'],
        'prenom': row['prénom'],
        'date_naissance': row['date_de_naissance'],
        'bu': row['bu'],
        'adresse_domicile': adresse,
        'mode_deplacement': mode_original,
        'categorie_sportive': sport_mode if is_sport else None,
        'distance_km': round(distance, 1) if distance else None,
        'eligible_prime': eligible,
        'raison': raison
    })

# Création du DataFrame des résultats
df_results = pd.DataFrame(results)

# Statistiques globales
print("\n" + "="*60)
print("📊 RAPPORT FINAL DE VALIDATION")
print("="*60)

total = len(df_results)
eligibles = df_results['eligible_prime'].sum()
non_eligibles = total - eligibles
taux = (eligibles / total * 100) if total > 0 else 0

print(f"\n📈 Synthèse:")
print(f"   • Total salariés: {total}")
print(f"   • ✅ Éligibles à la prime: {eligibles}")
print(f"   • ❌ Non éligibles: {non_eligibles}")
print(f"   • 📊 Taux d'éligibilité: {taux:.1f}%")

# Analyse par mode
print(f"\n🚲 Détail par catégorie de transport:")
mode_cat_stats = df_results.groupby('categorie_sportive').agg({
    'eligible_prime': ['count', 'sum']
}).round(2)
mode_cat_stats.columns = ['total', 'eligibles']
mode_cat_stats['taux_eligibilite'] = (mode_cat_stats['eligibles'] / mode_cat_stats['total'] * 100).round(1)
print(mode_cat_stats)

# Analyse par mode original
print(f"\n📋 Détail par mode déclaré (top 10):")
mode_orig_stats = df_results.groupby('mode_deplacement').agg({
    'eligible_prime': ['count', 'sum']
}).round(2)
mode_orig_stats.columns = ['total', 'eligibles']
mode_orig_stats['taux'] = (mode_orig_stats['eligibles'] / mode_orig_stats['total'] * 100).round(1)
mode_orig_stats = mode_orig_stats.sort_values('total', ascending=False)
print(mode_orig_stats.head(10))

# Sauvegarde des fichiers
print(f"\n💾 Sauvegarde des fichiers CSV:")

# Fichier complet
df_results.to_csv('validation_complete.csv', index=False, encoding='utf-8-sig')
print(f"   ✅ validation_complete.csv ({len(df_results)} lignes)")

# Fichier des éligibles
df_eligibles = df_results[df_results['eligible_prime'] == True]
if len(df_eligibles) > 0:
    df_eligibles.to_csv('salaries_eligibles.csv', index=False, encoding='utf-8-sig')
    print(f"   ✅ salaries_eligibles.csv ({len(df_eligibles)} salariés)")

# Fichier des non éligibles
df_non_eligibles = df_results[df_results['eligible_prime'] == False]
if len(df_non_eligibles) > 0:
    df_non_eligibles.to_csv('salaries_non_eligibles.csv', index=False, encoding='utf-8-sig')
    print(f"   📋 salaries_non_eligibles.csv ({len(df_non_eligibles)} salariés)")

# Rapport des motifs
print(f"\n📝 Motifs de non-éligibilité:")
motifs = df_non_eligibles['raison'].value_counts()
for motif, count in motifs.head(5).items():
    print(f"   • {motif[:60]}: {count}")

print("\n" + "="*60)
print("✅ Validation terminée avec succès !")
print("="*60)