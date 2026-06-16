"""
SCRIPT POC SIMPLIFIÉ - UTILISE DIRECTEMENT VOS FICHIERS
"""

import pandas as pd

print("=" * 60)
print("📊 RAPPORT POC - AVANTAGES SPORTIFS")
print("=" * 60)

# ============================================================
# 1. LIRE LES FICHIERS
# ============================================================

print("\n📂 Lecture de vos fichiers...")

# Fichier validation_complete.csv
df_prime = pd.read_csv('validation_complete.csv')
print(f"   ✅ validation_complete.csv : {len(df_prime)} lignes")

# Fichier wellness_eligibility.csv
df_wellness = pd.read_csv('wellness_eligibility.csv')
print(f"   ✅ wellness_eligibility.csv : {len(df_wellness)} lignes")

# ============================================================
# 2. EXTRAIRE LES VALEURS
# ============================================================

print("\n📊 Extraction des résultats...")

# Nombre d'éligibles prime
nb_eligibles_prime = df_prime['eligible_prime'].sum()
print(f"   • Éligibles prime : {nb_eligibles_prime}")

# Nombre d'éligibles bien-être
nb_eligibles_wellness = df_wellness['eligible_wellness'].sum()
print(f"   • Éligibles bien-être : {nb_eligibles_wellness}")

# Coût total des primes (déjà calculé dans le fichier)
cout_prime = df_prime['montant_prime'].sum()
print(f"   • Coût prime total : {cout_prime:,.0f} €")

# Salaire moyen
salaire_moyen = df_prime['Salaire brut'].mean()
print(f"   • Salaire moyen : {salaire_moyen:,.0f} €")

# ============================================================
# 3. CALCULER COÛT JOURS BIEN-ÊTRE
# ============================================================

print("\n💰 Calcul du coût des jours bien-être...")

cout_par_jour = salaire_moyen / 218  # 218 jours ouvrés
jours_offerts = 5

cout_wellness = nb_eligibles_wellness * jours_offerts * cout_par_jour
print(f"   • Coût journalier moyen : {cout_par_jour:.0f} €")
print(f"   • Coût par salarié (5j) : {jours_offerts * cout_par_jour:.0f} €")
print(f"   • Coût total bien-être : {cout_wellness:,.0f} €")

# ============================================================
# 4. TOTAL GLOBAL
# ============================================================

cout_total = cout_prime + cout_wellness

print("\n" + "=" * 60)
print("📊 TOTAL GLOBAL")
print("=" * 60)
print(f"   • Prime sportive : {cout_prime:,.0f} €")
print(f"   • Jours bien-être : {cout_wellness:,.0f} €")
print(f"   • COÛT TOTAL : {cout_total:,.0f} €")

# ============================================================
# 5. BÉNÉFICIAIRES
# ============================================================

print("\n👥 BÉNÉFICIAIRES")

# Nombre de personnes avec les deux avantages
nb_deux = ((df_prime['eligible_prime'] == True) & 
           (df_wellness['eligible_wellness'] == True)).sum()

nb_prime_seul = nb_eligibles_prime - nb_deux
nb_wellness_seul = nb_eligibles_wellness - nb_deux
nb_total = nb_prime_seul + nb_wellness_seul + nb_deux

print(f"   • Prime uniquement : {nb_prime_seul}")
print(f"   • Wellness uniquement : {nb_wellness_seul}")
print(f"   • Les deux : {nb_deux}")
print(f"   • Total : {nb_total} / {len(df_prime)} ({nb_total/len(df_prime)*100:.0f}%)")

# ============================================================
# 6. ROI
# ============================================================

print("\n" + "=" * 60)
print("📈 RETOUR SUR INVESTISSEMENT")
print("=" * 60)

gain_absent = cout_total * 0.30
gain_product = cout_total * 0.45
gain_talents = 35000

benefices = gain_absent + gain_product + gain_talents
roi = (benefices - cout_total) / cout_total * 100
net = benefices - cout_total
mois_retour = cout_total / (benefices / 12)

print(f"\n   Bénéfices estimés :")
print(f"   • Réduction absentéisme : {gain_absent:,.0f} €")
print(f"   • Gain productivité : {gain_product:,.0f} €")
print(f"   • Attraction talents : {gain_talents:,.0f} €")
print(f"   → TOTAL : {benefices:,.0f} €")

print(f"\n   Investissement : {cout_total:,.0f} €")
print(f"   Bénéfice net : {net:,.0f} €")
print(f"   ROI : {roi:.1f}%")
print(f"   Retour investissement : {mois_retour:.1f} mois")

# ============================================================
# 7. CONCLUSION
# ============================================================

print("\n" + "=" * 60)
print("📄 CONCLUSION")
print("=" * 60)

if roi > 0:
    print("\n   ✅ RECOMMANDATION : VALIDER LE POC")
else:
    print("\n   ⚠️ RECOMMANDATION : REVOIR LE POC")

print(f"""
   Résumé des résultats :
   ┌─────────────────────────────────────────────────────┐
   │ Investissement annuel : {cout_total:,.0f} €              │
   │ Bénéfice net annuel  : {net:,.0f} €                   │
   │ ROI                  : {roi:.1f}%                         │
   │ Retour investissement : {mois_retour:.1f} mois            │
   └─────────────────────────────────────────────────────┘
""")

# ============================================================
# 8. SAUVEGARDE
# ============================================================

print("💾 Sauvegarde...")

resultats = pd.DataFrame([
    ["Effectif total", len(df_prime)],
    ["Éligibles prime sportive", nb_eligibles_prime],
    ["Taux éligibilité prime", f"{nb_eligibles_prime/len(df_prime)*100:.0f}%"],
    ["Coût prime sportive (€)", f"{cout_prime:,.0f}"],
    ["Éligibles jours bien-être", nb_eligibles_wellness],
    ["Taux éligibilité bien-être", f"{nb_eligibles_wellness/len(df_prime)*100:.0f}%"],
    ["Coût jours bien-être (€)", f"{cout_wellness:,.0f}"],
    ["Coût total (€)", f"{cout_total:,.0f}"],
    ["ROI (%)", f"{roi:.1f}"],
    ["Bénéfice net (€)", f"{net:,.0f}"],
    ["Retour investissement (mois)", f"{mois_retour:.1f}"],
], columns=["Indicateur", "Valeur"])

resultats.to_csv('rapport_poc_officiel.csv', index=False, encoding='utf-8-sig')
print("   ✅ rapport_poc_officiel.csv")

print("\n" + "=" * 60)
print("✅ RAPPORT TERMINÉ")
print("=" * 60)