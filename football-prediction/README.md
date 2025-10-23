# ⚽ AI Football Prediction System v3.0

**Automated, intelligent football match prediction system powered by AI**

## 🌟 Features

- ✅ **Multi-source data collection** (API-Football, Understat, FBref, Transfermarkt)
- ✅ **Ensemble prediction models** (Scoring, Poisson, ML-ready)
- ✅ **Expected Goals (xG) analysis**
- ✅ **Value bet identification** vs bookmaker odds
- ✅ **Automated scheduling** (H-24, H-3, post-match analysis)
- ✅ **Post-match learning** and performance tracking
- ✅ **Confidence scoring** and quality assurance
- ✅ **Multiple output formats** (JSON, Markdown, Database)

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Architecture](#-architecture)
- [API Documentation](#-api-documentation)
- [Database Schema](#-database-schema)
- [Performance](#-performance)

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL 14+
- Redis (optional, for caching)

### 1. Clone & Install

```bash
git clone <repository-url>
cd football-prediction

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Setup Database

```bash
# Create database
createdb football_predictions

# Run schema
psql -d football_predictions -f src/database/schema.sql
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 4. Run Your First Prediction

```python
import asyncio
from src.pipeline import predict_match

# Predict a match by ID
result = asyncio.run(predict_match(1035480))

print(f"Prediction: {result.most_likely_score}")
print(f"Probabilities: {result.probabilities}")
print(f"Confidence: {result.confidence:.1%}")
```

## 📦 Installation

### Standard Installation

```bash
pip install -r requirements.txt
```

### Development Installation

```bash
pip install -e .
pip install -r requirements.txt
pytest  # Run tests
```

### Docker Installation

```bash
docker-compose up -d
```

## ⚙️ Configuration

### Environment Variables

Create `.env` file with:

```bash
# API Keys (REQUIRED)
FOOTBALL_DATA_API_KEY=your_key_here
RAPIDAPI_KEY=your_rapidapi_key
OPENWEATHER_API_KEY=your_weather_key

# Database (REQUIRED)
DATABASE_URL=postgresql://user:pass@localhost:5432/football_predictions

# Optional
REDIS_URL=redis://localhost:6379/0
ENABLE_ML=false
LOG_LEVEL=INFO
```

### Model Weights

Adjust prediction weights in `.env`:

```bash
WEIGHT_FORM=0.25
WEIGHT_SQUAD_QUALITY=0.20
WEIGHT_MOTIVATION=0.15
WEIGHT_PHYSICAL_CONDITION=0.15
WEIGHT_HOME_ADVANTAGE=0.10
WEIGHT_TACTICAL=0.10
WEIGHT_PSYCHOLOGICAL=0.05
```

## 📖 Usage

### CLI Usage

```bash
# Single match prediction
python src/pipeline.py 1035480

# Run automated scheduler
python src/scheduler.py
```

### Python API

```python
from src.pipeline import MatchPredictionPipeline
import asyncio

async def main():
    # Initialize pipeline
    pipeline = MatchPredictionPipeline(match_id=1035480)

    # Run prediction
    result = await pipeline.run(save_formats=['json', 'db', 'markdown'])

    # Access results
    print(f"Home Win: {result.probabilities['1']:.1%}")
    print(f"Draw: {result.probabilities['X']:.1%}")
    print(f"Away Win: {result.probabilities['2']:.1%}")

    # Expected goals
    print(f"xG Home: {result.expected_goals['home']}")
    print(f"xG Away: {result.expected_goals['away']}")

    # Value bets
    for vb in result.value_bets:
        print(f"Value: {vb['outcome']} @ {vb['odds']} (edge: {vb['edge']:.1%})")

asyncio.run(main())
```

### Batch Predictions

```python
from src.pipeline import predict_multiple

# Predict multiple matches in parallel
match_ids = [1035480, 1035481, 1035482]
results = await predict_multiple(match_ids)
```

### Post-Match Analysis

```python
from src.learning import PostMatchAnalyzer

# Analyze prediction accuracy
analyzer = PostMatchAnalyzer(prediction_id=123)
result = analyzer.analyze()

print(f"Correct: {result['prediction_accuracy']['correct']}")
print(f"Brier Score: {result['probability_calibration']:.4f}")
```

## 🏗️ Architecture

### System Components

```
football-prediction/
├── src/
│   ├── data_collection/      # API clients & scrapers
│   │   ├── api_clients.py    # Football-Data, API-Football, Weather
│   │   ├── scrapers.py       # Understat, FBref, Transfermarkt
│   │   ├── fallback.py       # Waterfall fetcher, proxy calculations
│   │   └── orchestrator.py   # Data collection coordinator
│   │
│   ├── processing/            # Feature engineering
│   │   └── processor.py      # Transform raw data to features
│   │
│   ├── models/                # Prediction models
│   │   ├── prediction_model.py  # Ensemble (Scoring, Poisson, ML)
│   │   └── supplementary.py     # Over/Under, BTTS, correct scores
│   │
│   ├── validation/            # Quality assurance
│   │   └── validator.py      # Sanity checks, confidence adjustment
│   │
│   ├── output/                # Report generation
│   │   ├── schemas.py        # Pydantic models
│   │   └── report_generator.py  # JSON, Markdown, DB output
│   │
│   ├── learning/              # Post-match analysis
│   │   └── post_match.py     # Accuracy tracking, model improvement
│   │
│   ├── database/              # Database layer
│   │   ├── models.py         # SQLAlchemy models
│   │   ├── schema.sql        # PostgreSQL schema
│   │   └── connection.py     # Connection management
│   │
│   ├── pipeline.py            # Main orchestrator
│   └── scheduler.py           # Automated job scheduler
│
├── predictions/               # Output directory
├── logs/                      # Log files
├── models_ml/                 # ML model files
├── tests/                     # Test suite
└── config/                    # Configuration files
```

### Workflow

```
1. Data Collection
   ├─→ API-Football (fixtures, stats, lineups)
   ├─→ Football-Data (match details, H2H)
   ├─→ Understat (xG data)
   ├─→ FBref (advanced stats)
   ├─→ Transfermarkt (injuries, market values)
   └─→ OpenWeather (match conditions)

2. Feature Engineering
   ├─→ Form analysis
   ├─→ Squad quality assessment
   ├─→ Injury impact calculation
   ├─→ Motivation factors
   ├─→ Tactical matchup
   └─→ Environmental factors

3. Prediction Generation
   ├─→ Weighted scoring method
   ├─→ Poisson distribution (goals)
   ├─→ ML model (if enabled)
   └─→ Ensemble combination

4. Validation & QA
   ├─→ Probability constraints
   ├─→ Logical consistency
   ├─→ Data quality checks
   └─→ Confidence adjustment

5. Output Generation
   ├─→ JSON export
   ├─→ Markdown report
   └─→ Database storage

6. Post-Match Learning
   ├─→ Accuracy tracking
   ├─→ Brier score calculation
   └─→ Model performance review
```

## 📊 Database Schema

### Key Tables

- **matches** - Match information
- **predictions** - Generated predictions
- **prediction_results** - Post-match evaluation
- **team_stats** - Team statistics
- **player_availability** - Injuries and suspensions

### Example Queries

```sql
-- Get recent prediction accuracy
SELECT
    COUNT(*) as total,
    AVG(CASE WHEN correct_result THEN 1.0 ELSE 0.0 END) as accuracy,
    AVG(brier_score) as avg_brier
FROM prediction_results
WHERE created_at >= NOW() - INTERVAL '30 days';

-- Find value bets
SELECT
    match_id,
    value_bets
FROM predictions
WHERE value_bets IS NOT NULL
ORDER BY created_at DESC;
```

## 📈 Performance

### Typical Metrics

- **Accuracy**: ~55-60% on 1X2 predictions
- **Brier Score**: ~0.20-0.25 (lower is better)
- **Data Collection**: ~10-30 seconds per match
- **Prediction Generation**: <5 seconds

### Benchmarks

```
Component              | Time
-----------------------|--------
API Data Collection    | 5-15s
Web Scraping           | 10-20s
Feature Engineering    | <1s
Prediction Calculation | <1s
Validation             | <1s
Total Pipeline         | 15-40s
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_pipeline.py

# Run with coverage
pytest --cov=src tests/
```

## 🐛 Troubleshooting

### Common Issues

**1. Import Errors**
```bash
# Ensure you're in the correct directory
cd football-prediction
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

**2. Database Connection Failed**
```bash
# Check PostgreSQL is running
pg_isready

# Verify connection string in .env
psql $DATABASE_URL
```

**3. API Rate Limits**
```
Error: Rate limit exceeded

Solution: Upgrade API plan or reduce request frequency
```

**4. Missing Data**
```
Warning: Critical data missing

Solution: System uses fallback calculations automatically
Check logs for which sources failed
```

## 📝 API Keys Required

### Free Tier Options

- **API-Football** (RapidAPI): 100 requests/day
- **Football-Data.org**: 10 requests/minute
- **OpenWeatherMap**: 60 calls/minute

### Getting API Keys

1. **API-Football**: https://rapidapi.com/api-sports/api/api-football
2. **Football-Data**: https://www.football-data.org/client/register
3. **OpenWeather**: https://openweathermap.org/api

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- **Data Sources**: API-Football, Understat, FBref, Transfermarkt
- **Statistical Models**: Based on Dixon-Coles and Poisson models
- **Inspiration**: Football analytics community

## 📞 Support

- **Issues**: Open a GitHub issue
- **Documentation**: Check `/docs` folder
- **Examples**: See `/examples` directory

---

**Made with ⚽ and 🤖 by AI Football Prediction System**

*Last Updated: January 2025*
