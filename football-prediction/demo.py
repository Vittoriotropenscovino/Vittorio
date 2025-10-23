#!/usr/bin/env python3
"""
🎮 DEMO INTERATTIVA - AI Football Prediction System v3.0

Prova il sistema con predizioni mock senza bisogno di API o database!
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def print_header():
    print("\n" + "="*70)
    print("⚽ AI FOOTBALL PREDICTION SYSTEM v3.0 - DEMO INTERATTIVA")
    print("="*70)
    print("\nQuesta demo ti mostra il sistema in azione con dati MOCK")
    print("(Nessuna API o database richiesto!)\n")

def demo_clasico():
    """Demo: Barcellona vs Real Madrid - El Clásico"""
    from models.prediction_model import PredictionModel
    from models.supplementary import SupplementaryCalculations
    from validation.validator import PredictionValidator

    print("\n" + "─"*70)
    print("🏟️  DEMO 1: BARCELLONA vs REAL MADRID - El Clásico")
    print("─"*70)

    features = {
        'home_form': 8.5,
        'away_form': 7.5,
        'home_squad_quality': 9.0,
        'away_squad_quality': 8.5,
        'home_motivation': 9.5,
        'away_motivation': 9.5,
        'home_physical_condition': 8.5,
        'away_physical_condition': 8.0,
        'home_field_advantage': 7.0,
        'home_avg_goals': 2.5,
        'away_avg_goals': 2.2,
        'home_avg_conceded': 0.8,
        'away_avg_conceded': 1.0,
        'tactical_matchup_score': 0.3,
        'h2h_home_advantage': 0.1,
        'rivalry_level': 10,
        'home_position': 1,
        'away_position': 2,
        '_meta': {
            'overall_confidence': 0.92,
            'missing_data': []
        }
    }

    config = {'use_ml': False}

    # Genera predizione
    print("\n⚙️  Generando predizione...")
    model = PredictionModel(features, config)
    prediction = model.predict()

    # Calcola mercati supplementari
    supp = SupplementaryCalculations(
        prediction['expected_goals'],
        prediction['probabilities']
    )
    markets = supp.calculate_all()

    # Validazione
    validator = PredictionValidator(prediction, features)
    validation = validator.validate()

    # Mostra risultati
    print("\n" + "─"*70)
    print("📊 RISULTATI PREDIZIONE")
    print("─"*70)

    print(f"\n🎯 PROBABILITÀ (1X2):")
    print(f"   🏠 Barcellona Win:  {prediction['probabilities']['1']:>6.1%}")
    print(f"   ⚖️  Pareggio:        {prediction['probabilities']['X']:>6.1%}")
    print(f"   ✈️  Real Madrid Win: {prediction['probabilities']['2']:>6.1%}")

    print(f"\n⚽ EXPECTED GOALS (xG):")
    print(f"   Barcellona:     {prediction['expected_goals']['home']:.2f}")
    print(f"   Real Madrid:    {prediction['expected_goals']['away']:.2f}")

    print(f"\n📈 PREDIZIONE FINALE:")
    print(f"   Risultato più probabile: {prediction['most_likely_score']}")
    print(f"   Confidenza predizione:   {prediction['confidence']:.1%}")
    print(f"   Qualità dati:            {validation.get('validation_passed', True) and 'ALTA' or 'MEDIA'}")

    print(f"\n💰 MERCATI SUPPLEMENTARI:")
    print(f"   Over 2.5 gol:            {markets['over_under']['over_2.5']:>6.1%}")
    print(f"   Under 2.5 gol:           {markets['over_under']['under_2.5']:>6.1%}")
    print(f"   BTTS Yes (entrambe):     {markets['btts']['btts_yes']:>6.1%}")
    print(f"   BTTS No:                 {markets['btts']['btts_no']:>6.1%}")

    print(f"\n🎲 TOP 5 PUNTEGGI PIÙ PROBABILI:")
    for i, score in enumerate(markets['correct_score_top5'][:5], 1):
        print(f"   {i}. {score['score']:>5}  →  {score['probability']:>6.2%}")

    print(f"\n🧹 CLEAN SHEET:")
    print(f"   Barcellona:     {markets['clean_sheet']['home_clean_sheet']:>6.1%}")
    print(f"   Real Madrid:    {markets['clean_sheet']['away_clean_sheet']:>6.1%}")

    if validation['warnings']:
        print(f"\n⚠️  AVVISI ({len(validation['warnings'])}):")
        for warning in validation['warnings'][:3]:
            print(f"   • {warning}")

    return prediction

def demo_upset():
    """Demo: Underdog che vince"""
    from models.prediction_model import PredictionModel
    from models.supplementary import SupplementaryCalculations

    print("\n\n" + "─"*70)
    print("🏟️  DEMO 2: ATALANTA (casa) vs NAPOLI (trasferta)")
    print("     Scenario: Underdog in forma contro favorita in difficoltà")
    print("─"*70)

    features = {
        'home_form': 8.5,      # Atalanta in ottima forma
        'away_form': 5.5,      # Napoli in crisi
        'home_squad_quality': 7.5,
        'away_squad_quality': 8.5,
        'home_motivation': 8.5,
        'away_motivation': 6.0,  # Napoli demotivato
        'home_physical_condition': 8.5,
        'away_physical_condition': 6.5,  # Napoli con infortuni
        'home_field_advantage': 7.5,
        'home_avg_goals': 2.2,
        'away_avg_goals': 1.5,
        'home_avg_conceded': 1.2,
        'away_avg_conceded': 1.8,
        'tactical_matchup_score': 0.4,  # Tattica Atalanta efficace
        'h2h_home_advantage': 0.2,
        'home_position': 5,
        'away_position': 3,
        'home_key_absences': 1,
        'away_key_absences': 4,  # Napoli con molti assenti
        '_meta': {
            'overall_confidence': 0.85,
            'missing_data': []
        }
    }

    config = {'use_ml': False}

    print("\n⚙️  Generando predizione...")
    model = PredictionModel(features, config)
    prediction = model.predict()

    supp = SupplementaryCalculations(
        prediction['expected_goals'],
        prediction['probabilities']
    )
    markets = supp.calculate_all()

    print("\n" + "─"*70)
    print("📊 RISULTATI PREDIZIONE")
    print("─"*70)

    print(f"\n🎯 PROBABILITÀ:")
    print(f"   🏠 Atalanta Win:  {prediction['probabilities']['1']:>6.1%}")
    print(f"   ⚖️  Pareggio:      {prediction['probabilities']['X']:>6.1%}")
    print(f"   ✈️  Napoli Win:    {prediction['probabilities']['2']:>6.1%}")

    print(f"\n⚽ EXPECTED GOALS:")
    print(f"   Atalanta:  {prediction['expected_goals']['home']:.2f}")
    print(f"   Napoli:    {prediction['expected_goals']['away']:.2f}")

    print(f"\n📈 PREDIZIONE FINALE:")
    print(f"   Risultato: {prediction['most_likely_score']}")
    print(f"   Confidenza: {prediction['confidence']:.1%}")

    print(f"\n💡 ANALISI:")
    print(f"   • Atalanta favorita nonostante rosa meno forte")
    print(f"   • Forma e motivazione fanno la differenza")
    print(f"   • Napoli penalizzato da 4 assenze chiave")
    print(f"   • Over 2.5: {markets['over_under']['over_2.5']:.1%} (probabile gol)")

    return prediction

def demo_defensive():
    """Demo: Partita tattica difensiva"""
    from models.prediction_model import PredictionModel
    from models.supplementary import SupplementaryCalculations

    print("\n\n" + "─"*70)
    print("🏟️  DEMO 3: INTER (casa) vs JUVENTUS (trasferta)")
    print("     Scenario: Derby tattico difensivo")
    print("─"*70)

    features = {
        'home_form': 7.5,
        'away_form': 7.0,
        'home_squad_quality': 8.5,
        'away_squad_quality': 8.5,
        'home_motivation': 9.0,
        'away_motivation': 9.0,
        'home_physical_condition': 8.0,
        'away_physical_condition': 8.0,
        'home_field_advantage': 6.0,
        'home_avg_goals': 1.6,      # Difese solide
        'away_avg_goals': 1.5,
        'home_avg_conceded': 0.7,   # Pochi gol subiti
        'away_avg_conceded': 0.8,
        'tactical_matchup_score': 0.1,
        'h2h_home_advantage': 0.0,
        'rivalry_level': 9,
        'is_rivalry': True,
        '_meta': {
            'overall_confidence': 0.88,
            'missing_data': []
        }
    }

    config = {'use_ml': False}

    print("\n⚙️  Generando predizione...")
    model = PredictionModel(features, config)
    prediction = model.predict()

    supp = SupplementaryCalculations(
        prediction['expected_goals'],
        prediction['probabilities']
    )
    markets = supp.calculate_all()

    print("\n" + "─"*70)
    print("📊 RISULTATI PREDIZIONE")
    print("─"*70)

    print(f"\n🎯 PROBABILITÀ:")
    print(f"   🏠 Inter Win:  {prediction['probabilities']['1']:>6.1%}")
    print(f"   ⚖️  Pareggio:   {prediction['probabilities']['X']:>6.1%}")
    print(f"   ✈️  Juve Win:   {prediction['probabilities']['2']:>6.1%}")

    print(f"\n⚽ EXPECTED GOALS:")
    print(f"   Inter:      {prediction['expected_goals']['home']:.2f}")
    print(f"   Juventus:   {prediction['expected_goals']['away']:.2f}")
    print(f"   TOTALE:     {prediction['expected_goals']['home'] + prediction['expected_goals']['away']:.2f}")

    print(f"\n📈 PREDIZIONE FINALE:")
    print(f"   Risultato: {prediction['most_likely_score']}")
    print(f"   Confidenza: {prediction['confidence']:.1%}")

    print(f"\n💰 MERCATI CHIAVE:")
    print(f"   Under 2.5 gol:       {markets['over_under']['under_2.5']:>6.1%} ⭐")
    print(f"   BTTS No:             {markets['btts']['btts_no']:>6.1%}")
    print(f"   Clean Sheet Inter:   {markets['clean_sheet']['home_clean_sheet']:>6.1%}")
    print(f"   Clean Sheet Juve:    {markets['clean_sheet']['away_clean_sheet']:>6.1%}")

    print(f"\n💡 ANALISI:")
    print(f"   • Derby tattico equilibrato")
    print(f"   • Alta probabilità pareggio ({prediction['probabilities']['X']:.1%})")
    print(f"   • Difese solide → pochi gol attesi")
    print(f"   • Under 2.5 molto probabile")
    print(f"   • Consiglio: scommettere su risultati bassi (0-0, 1-0, 1-1)")

    return prediction

def main():
    """Main demo function"""
    print_header()

    try:
        # Demo 1: El Clásico
        demo_clasico()

        input("\n\nPremi INVIO per vedere la prossima demo...")

        # Demo 2: Upset
        demo_upset()

        input("\n\nPremi INVIO per vedere l'ultima demo...")

        # Demo 3: Defensive
        demo_defensive()

        # Summary
        print("\n\n" + "="*70)
        print("✅ DEMO COMPLETATA!")
        print("="*70)
        print("\n🎉 Hai visto il sistema in azione con 3 scenari diversi:")
        print("   1. ⚔️  Derby equilibrato di alto livello")
        print("   2. 🎲 Underdog che batte la favorita")
        print("   3. 🛡️  Partita tattica difensiva")

        print("\n📚 PROSSIMI PASSI:")
        print("   • Leggi QUICKSTART.md per creare le tue predizioni")
        print("   • Modifica i parametri per testare scenari diversi")
        print("   • Installa dipendenze per test completi: pip install -r requirements.txt")
        print("   • Setup database per usare dati reali")

        print("\n🚀 COMANDI UTILI:")
        print("   python demo.py                    # Questa demo")
        print("   python test_syntax.py             # Test sintassi")
        print("   python test_quick.py              # Test funzionali")
        print("   python test_my_prediction.py      # Crea predizione custom")

        print("\n" + "="*70)
        print("Grazie per aver provato AI Football Prediction System v3.0!")
        print("="*70 + "\n")

        return 0

    except ImportError as e:
        print(f"\n❌ ERRORE: Dipendenze mancanti")
        print(f"   {e}")
        print("\n💡 SOLUZIONE:")
        print("   python3 -m venv venv")
        print("   source venv/bin/activate")
        print("   pip install -r requirements.txt")
        print("   python demo.py")
        return 1

    except Exception as e:
        print(f"\n❌ ERRORE: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
