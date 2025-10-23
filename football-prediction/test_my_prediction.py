#!/usr/bin/env python3
"""
🎮 CREA LA TUA PREDIZIONE PERSONALIZZATA

Modifica i parametri qui sotto per testare diversi scenari!
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from models.prediction_model import PredictionModel
from models.supplementary import SupplementaryCalculations

# ============================================================
# 🔧 MODIFICA QUESTI PARAMETRI PER IL TUO SCENARIO
# ============================================================

# SQUADRE
home_team = "Manchester City"
away_team = "Liverpool"

# PARAMETRI (scala 0-10, tranne dove indicato)
features = {
    # FORMA RECENTE (0-10)
    'home_form': 8.5,           # Quanto sta giocando bene ultimamente?
    'away_form': 8.0,

    # QUALITÀ ROSA (0-10)
    'home_squad_quality': 9.0,  # Qualità giocatori
    'away_squad_quality': 8.5,

    # MOTIVAZIONE (0-10)
    'home_motivation': 9.0,     # Quanto è importante la partita?
    'away_motivation': 9.0,

    # CONDIZIONE FISICA (0-10)
    'home_physical_condition': 8.5,  # Forma fisica, infortuni
    'away_physical_condition': 8.0,

    # FATTORE CAMPO (0-10)
    'home_field_advantage': 7.0,  # Quanto conta giocare in casa?

    # STATISTICHE OFFENSIVE/DIFENSIVE (gol per partita)
    'home_avg_goals': 2.5,        # Media gol segnati
    'away_avg_goals': 2.2,
    'home_avg_conceded': 0.8,     # Media gol subiti
    'away_avg_conceded': 1.0,

    # TATTICA E PSICOLOGIA (-1 a +1)
    'tactical_matchup_score': 0.2,   # +1 = vantaggio casa, -1 = vantaggio trasferta
    'h2h_home_advantage': 0.1,       # Storico scontri diretti

    # ALTRI
    'rivalry_level': 8,           # 0-10: è un derby/rivalità? (10 = derby)

    # METADATA (non modificare)
    '_meta': {
        'overall_confidence': 0.90  # Confidenza nei dati (0-1)
    }
}

config = {
    'use_ml': False  # Usa modello ML (se disponibile)
}

# ============================================================
# 🚀 GENERA PREDIZIONE
# ============================================================

print("\n" + "="*70)
print(f"⚽ PREDIZIONE: {home_team} vs {away_team}")
print("="*70)

# Crea modello e genera predizione
model = PredictionModel(features, config)
prediction = model.predict()

# Calcola mercati supplementari
supp = SupplementaryCalculations(
    prediction['expected_goals'],
    prediction['probabilities']
)
markets = supp.calculate_all()

# ============================================================
# 📊 MOSTRA RISULTATI
# ============================================================

print(f"\n🎯 PROBABILITÀ 1X2:")
print(f"   {'🏠 ' + home_team + ' Win:':<30} {prediction['probabilities']['1']:>6.1%}")
print(f"   {'⚖️  Pareggio:':<30} {prediction['probabilities']['X']:>6.1%}")
print(f"   {'✈️  ' + away_team + ' Win:':<30} {prediction['probabilities']['2']:>6.1%}")

# Determina favorito
if prediction['probabilities']['1'] > prediction['probabilities']['2']:
    favorito = home_team
    prob_favorito = prediction['probabilities']['1']
elif prediction['probabilities']['2'] > prediction['probabilities']['1']:
    favorito = away_team
    prob_favorito = prediction['probabilities']['2']
else:
    favorito = "Equilibrato"
    prob_favorito = max(prediction['probabilities'].values())

print(f"\n💪 FAVORITO: {favorito} ({prob_favorito:.1%})")

print(f"\n⚽ EXPECTED GOALS (xG):")
print(f"   {home_team:<20} {prediction['expected_goals']['home']:.2f}")
print(f"   {away_team:<20} {prediction['expected_goals']['away']:.2f}")
print(f"   {'TOTALE':<20} {prediction['expected_goals']['home'] + prediction['expected_goals']['away']:.2f}")

print(f"\n📈 PREDIZIONE FINALE:")
print(f"   Risultato più probabile:  {prediction['most_likely_score']}")
print(f"   Confidenza predizione:    {prediction['confidence']:.1%}")

print(f"\n💰 MERCATI OVER/UNDER:")
for line in [0.5, 1.5, 2.5, 3.5]:
    over = markets['over_under'].get(f'over_{line}', 0)
    under = markets['over_under'].get(f'under_{line}', 0)
    # Evidenzia il più probabile
    over_mark = " ⭐" if over > 0.55 else ""
    under_mark = " ⭐" if under > 0.55 else ""
    print(f"   Over {line}:  {over:>6.1%}{over_mark:<3}  |  Under {line}: {under:>6.1%}{under_mark}")

print(f"\n🎲 BOTH TEAMS TO SCORE:")
print(f"   Si (BTTS Yes):  {markets['btts']['btts_yes']:>6.1%}" +
      (" ⭐" if markets['btts']['btts_yes'] > 0.55 else ""))
print(f"   No (BTTS No):   {markets['btts']['btts_no']:>6.1%}" +
      (" ⭐" if markets['btts']['btts_no'] > 0.55 else ""))

print(f"\n🧹 CLEAN SHEET (porta inviolata):")
print(f"   {home_team:<20} {markets['clean_sheet']['home_clean_sheet']:>6.1%}")
print(f"   {away_team:<20} {markets['clean_sheet']['away_clean_sheet']:>6.1%}")

print(f"\n🎯 TOP 5 PUNTEGGI PIÙ PROBABILI:")
for i, score in enumerate(markets['correct_score_top5'][:5], 1):
    print(f"   {i}. {score['score']:>5}  →  {score['probability']:>6.2%}")

print(f"\n🔍 RANGE GOL TOTALI:")
for range_name, prob in markets['goal_ranges'].items():
    bar = "█" * int(prob * 40)
    print(f"   {range_name:>5} gol: {prob:>6.1%} {bar}")

# ============================================================
# 💡 SUGGERIMENTI
# ============================================================

print(f"\n💡 SUGGERIMENTI SCOMMESSE:")
suggestions = []

# Over/Under
total_xg = prediction['expected_goals']['home'] + prediction['expected_goals']['away']
if total_xg > 2.7:
    suggestions.append(f"✓ OVER 2.5 gol ({markets['over_under']['over_2.5']:.1%} prob)")
elif total_xg < 2.2:
    suggestions.append(f"✓ UNDER 2.5 gol ({markets['over_under']['under_2.5']:.1%} prob)")

# BTTS
if markets['btts']['btts_yes'] > 0.60:
    suggestions.append(f"✓ BTTS Yes (entrambe segnano) - {markets['btts']['btts_yes']:.1%}")
elif markets['btts']['btts_no'] > 0.60:
    suggestions.append(f"✓ BTTS No (almeno una non segna) - {markets['btts']['btts_no']:.1%}")

# Favorito
if prob_favorito > 0.55:
    suggestions.append(f"✓ Favorito: {favorito} ({prob_favorito:.1%})")

# Correct score
if markets['correct_score_top5'][0]['probability'] > 0.10:
    top_score = markets['correct_score_top5'][0]
    suggestions.append(f"✓ Punteggio esatto: {top_score['score']} ({top_score['probability']:.1%})")

if suggestions:
    for suggestion in suggestions:
        print(f"   {suggestion}")
else:
    print("   • Partita equilibrata, valutare altre opzioni")

# ============================================================
# 🎓 ANALISI DETTAGLIATA
# ============================================================

print(f"\n🎓 ANALISI FATTORI:")

# Forma
form_diff = features['home_form'] - features['away_form']
if abs(form_diff) > 2:
    better_form = home_team if form_diff > 0 else away_team
    print(f"   • {better_form} in forma migliore ({abs(form_diff):.1f} punti diff)")

# Qualità
quality_diff = features['home_squad_quality'] - features['away_squad_quality']
if abs(quality_diff) > 1:
    better_squad = home_team if quality_diff > 0 else away_team
    print(f"   • {better_squad} ha rosa più forte")

# Motivazione
motiv_diff = features['home_motivation'] - features['away_motivation']
if abs(motiv_diff) > 2:
    more_motivated = home_team if motiv_diff > 0 else away_team
    print(f"   • {more_motivated} più motivato")

# Difesa
if features['home_avg_conceded'] < 1.0:
    print(f"   • {home_team} ha difesa solida ({features['home_avg_conceded']} gol/partita)")
if features['away_avg_conceded'] < 1.0:
    print(f"   • {away_team} ha difesa solida ({features['away_avg_conceded']} gol/partita)")

# Attacco
if features['home_avg_goals'] > 2.0:
    print(f"   • {home_team} ha attacco prolifico ({features['home_avg_goals']} gol/partita)")
if features['away_avg_goals'] > 2.0:
    print(f"   • {away_team} ha attacco prolifico ({features['away_avg_goals']} gol/partita)")

print("\n" + "="*70)
print("✅ Predizione completata!")
print("="*70)
print("\n💡 TIPS:")
print("   • Modifica i parametri in cima al file per testare altri scenari")
print("   • Esegui: python test_my_prediction.py")
print("   • Scala 0-10 per la maggior parte dei parametri")
print("   • Vedi QUICKSTART.md per esempi e guida completa")
print()
