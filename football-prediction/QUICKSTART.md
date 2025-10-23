# 🚀 QUICK START - Prova Subito il Sistema!

## 🎯 Setup Rapido (5 minuti)

### Step 1: Installa Dipendenze

```bash
cd football-prediction

# Crea virtual environment
python3 -m venv venv

# Attiva (Linux/Mac)
source venv/bin/activate

# Installa dipendenze
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 2: Configura API Keys (Opzionale per test)

Per test con dati MOCK (senza API):
```bash
# Non serve nulla! Vai allo Step 3
```

Per test con dati REALI:
```bash
# Crea file .env
cat > .env << EOF
# API Keys (opzionali per test iniziali)
RAPIDAPI_KEY=your_key_here
OPENWEATHER_API_KEY=your_key_here
FOOTBALL_DATA_API_KEY=your_key_here

# Database (opzionale)
DATABASE_URL=postgresql://user:pass@localhost:5432/football_predictions

# Config
ENABLE_ML=false
LOG_LEVEL=INFO
EOF
```

### Step 3: Test Rapido (Con Mock Data)

```bash
# Test funzionalità core (NO API richieste)
python3 test_quick.py
```

Output atteso:
```
TEST 7: Testing Complete Prediction Flow...
  ✓ Prediction generated
    - Probabilities: 1=52%, X=28%, 2=20%
    - Expected Goals: Home=2.0, Away=1.5
    - Most Likely: 2-1
    - Confidence: 85.3%

🎉 ALL TESTS PASSED!
```

---

## 🎮 Prova il Sistema con Predizioni Mock

### Esempio 1: Predizione Base

```python
# Crea file: test_my_prediction.py
import sys
sys.path.insert(0, 'src')

from models.prediction_model import PredictionModel
from models.supplementary import SupplementaryCalculations

# Dati mock per Barcellona vs Real Madrid
features = {
    'home_form': 8.5,  # Barcellona in ottima forma
    'away_form': 7.0,  # Real Madrid buona forma
    'home_squad_quality': 9.0,
    'away_squad_quality': 8.5,
    'home_motivation': 9.0,  # Derby - motivazione alta
    'away_motivation': 9.0,
    'home_physical_condition': 8.0,
    'away_physical_condition': 8.0,
    'home_field_advantage': 7.0,  # Camp Nou
    'home_avg_goals': 2.5,
    'away_avg_goals': 2.0,
    'home_avg_conceded': 0.8,
    'away_avg_conceded': 1.0,
    'tactical_matchup_score': 0.3,  # Leggero vantaggio Barça
    'h2h_home_advantage': 0.2,
    'rivalry_level': 10,  # El Clásico!
    '_meta': {'overall_confidence': 0.90}
}

config = {'use_ml': False}

# Genera predizione
model = PredictionModel(features, config)
prediction = model.predict()

# Stampa risultati
print("\n🏟️  BARCELLONA vs REAL MADRID - El Clásico")
print("="*50)
print(f"\n📊 PROBABILITÀ:")
print(f"   Barcellona Win: {prediction['probabilities']['1']:.1%}")
print(f"   Pareggio:       {prediction['probabilities']['X']:.1%}")
print(f"   Real Madrid Win: {prediction['probabilities']['2']:.1%}")

print(f"\n⚽ EXPECTED GOALS:")
print(f"   Barcellona: {prediction['expected_goals']['home']}")
print(f"   Real Madrid: {prediction['expected_goals']['away']}")

print(f"\n🎯 PREDIZIONE:")
print(f"   Risultato più probabile: {prediction['most_likely_score']}")
print(f"   Confidenza: {prediction['confidence']:.1%}")

# Calcola mercati supplementari
supp = SupplementaryCalculations(
    prediction['expected_goals'],
    prediction['probabilities']
)
markets = supp.calculate_all()

print(f"\n💰 MERCATI SUPPLEMENTARI:")
print(f"   Over 2.5 gol: {markets['over_under']['over_2.5']:.1%}")
print(f"   BTTS (Entrambe segnano): {markets['btts']['btts_yes']:.1%}")
print(f"\n📈 Top 3 punteggi più probabili:")
for i, score in enumerate(markets['correct_score_top5'][:3], 1):
    print(f"   {i}. {score['score']}: {score['probability']:.2%}")
```

Esegui:
```bash
python test_my_prediction.py
```

---

## 🎲 Esempi Rapidi

### Esempio A: Squadra Forte vs Squadra Debole

```python
# Milan (casa) vs Salernitana (trasferta)
features = {
    'home_form': 8.0, 'away_form': 3.0,
    'home_squad_quality': 8.5, 'away_squad_quality': 5.0,
    'home_motivation': 7.0, 'away_motivation': 8.0,  # Salernitana cerca salvezza
    'home_physical_condition': 8.0, 'away_physical_condition': 6.0,
    'home_field_advantage': 6.5,
    'home_avg_goals': 2.0, 'away_avg_goals': 0.8,
    'home_avg_conceded': 0.9, 'away_avg_conceded': 2.0,
    'tactical_matchup_score': 0.5,  # Forte vantaggio Milan
    'h2h_home_advantage': 0.6,
    '_meta': {'overall_confidence': 0.85}
}
# Risultato atteso: ~70% Milan, ~20% Pareggio, ~10% Salernitana
```

### Esempio B: Derby Equilibrato

```python
# Inter vs Juventus - Derby d'Italia
features = {
    'home_form': 7.5, 'away_form': 7.0,
    'home_squad_quality': 8.5, 'away_squad_quality': 8.5,
    'home_motivation': 9.0, 'away_motivation': 9.0,  # Derby!
    'home_physical_condition': 8.0, 'away_physical_condition': 8.0,
    'home_field_advantage': 6.0,
    'home_avg_goals': 1.8, 'away_avg_goals': 1.7,
    'home_avg_conceded': 1.0, 'away_avg_conceded': 1.1,
    'tactical_matchup_score': 0.1,  # Molto equilibrato
    'h2h_home_advantage': 0.0,  # H2H bilanciato
    'rivalry_level': 9,
    '_meta': {'overall_confidence': 0.88}
}
# Risultato atteso: ~40% Inter, ~35% Pareggio, ~25% Juve
```

### Esempio C: Team in Forma vs Team in Crisi

```python
# Napoli (casa, in forma) vs Roma (trasferta, in crisi)
features = {
    'home_form': 9.0, 'away_form': 4.0,  # Grande differenza di forma
    'home_squad_quality': 8.5, 'away_squad_quality': 7.5,
    'home_motivation': 8.0, 'away_motivation': 5.0,  # Roma demotivata
    'home_physical_condition': 9.0, 'away_physical_condition': 6.0,
    'home_field_advantage': 7.0,  # Maradona
    'home_avg_goals': 2.8, 'away_avg_goals': 1.2,
    'home_avg_conceded': 0.7, 'away_avg_conceded': 1.8,
    'tactical_matchup_score': 0.6,
    'h2h_home_advantage': 0.3,
    '_meta': {'overall_confidence': 0.92}
}
# Risultato atteso: ~65% Napoli, ~25% Pareggio, ~10% Roma
```

---

## 🔧 Modifica i Parametri

Tutti i parametri sono su scala **0-10** (tranne alcuni specifici):

### Parametri Principali:

| Parametro | Range | Descrizione |
|-----------|-------|-------------|
| `home_form` / `away_form` | 0-10 | Forma recente (10 = ottima) |
| `squad_quality` | 0-10 | Qualità rosa (10 = top) |
| `motivation` | 0-10 | Motivazione (10 = massima) |
| `physical_condition` | 0-10 | Condizione fisica (10 = perfetta) |
| `home_field_advantage` | 0-10 | Fattore casa (10 = fortissimo) |
| `avg_goals` | 0+ | Media gol segnati per partita |
| `avg_conceded` | 0+ | Media gol subiti per partita |
| `tactical_matchup_score` | -1 a +1 | Matchup tattico (+1 = vantaggio casa) |
| `h2h_home_advantage` | -1 a +1 | Vantaggio H2H (+1 = casa domina) |
| `rivalry_level` | 0-10 | Intensità rivalità (10 = derby) |

### Confidenza Dati:
- `overall_confidence`: 0.0-1.0 (1.0 = dati perfetti)

---

## 🎯 Test Scenari Specifici

### Scenario: Partita con Molti Infortuni

```python
features = {
    'home_form': 7.0,
    'away_form': 7.0,
    # ... altri parametri ...
    'home_physical_condition': 5.0,  # 5+ giocatori chiave infortunati
    'away_physical_condition': 9.0,  # Rosa al completo
}
# Effetto: Riduce probabilità vittoria casa
```

### Scenario: Team in Corsa per Titolo vs Team Salvo

```python
features = {
    'home_motivation': 10.0,  # Lotta per il titolo!
    'away_motivation': 3.0,   # Metà classifica, tranquilli
    # ... altri parametri equilibrati ...
}
# Effetto: Aumenta probabilità vittoria casa
```

### Scenario: Campo Difficile (Neve/Pioggia)

```python
features = {
    'home_field_advantage': 8.0,  # Campo pesante avvantaggia squadra fisica
    'tactical_matchup_score': 0.3,  # Squadra casa più fisica
}
```

---

## 🚨 Troubleshooting

### Errore: "No module named 'numpy'"
```bash
# Assicurati di aver attivato il venv
source venv/bin/activate
pip install -r requirements.txt
```

### Errore: "Features dictionary cannot be None or empty"
```bash
# Hai dimenticato qualche parametro richiesto
# Assicurati di includere almeno:
# - home_form, away_form
# - home_avg_goals, away_avg_goals
# - home_avg_conceded, away_avg_conceded
# - _meta (con overall_confidence)
```

### Warning: "Draw probability unusual"
```bash
# Normale per partite molto sbilanciate
# Es: Top team vs ultima in classifica
# La probabilità pareggio potrebbe essere <5%
```

---

## 📚 Prossimi Passi

1. ✅ **Test con mock data** (FATTO con questa guida)
2. ⏳ **Setup Database** → `python scripts/setup_database.py`
3. ⏳ **Configura API keys** → Per dati reali
4. ⏳ **Esegui predizione reale** → `python src/pipeline.py <match_id>`

---

## 🎉 Pronto per iniziare!

```bash
# 1. Installa
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 2. Testa
python3 test_quick.py

# 3. Prova con mock
python test_my_prediction.py

# 4. Divertiti! 🚀
```

Per domande o aiuto: vedi `TESTING_GUIDE.md`
