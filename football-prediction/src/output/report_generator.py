"""Report generator - Convert predictions to various formats"""

import json
import logging
from datetime import datetime
from typing import Dict, List
from pathlib import Path

from .schemas import PredictionOutput

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate prediction reports in various formats"""

    def __init__(self, match_input, all_data, prediction, validation):
        """
        Initialize report generator

        Args:
            match_input: MatchAnalysisInput object
            all_data: Complete collected data dict
            prediction: Prediction results dict
            validation: Validation results dict
        """
        self.input = match_input
        self.data = all_data
        self.pred = prediction
        self.val = validation

    def generate(self) -> PredictionOutput:
        """Generate structured output"""

        # Identify key factors
        key_factors = self._extract_key_factors()

        # Determine most likely result
        probs = self.pred['probabilities']
        most_likely = max(probs, key=probs.get)

        # Data quality level
        conf = self.pred['confidence'] * self.val['final_confidence_adjustment']
        if conf >= 0.75:
            quality = "HIGH"
        elif conf >= 0.60:
            quality = "MEDIUM"
        else:
            quality = "LOW"

        # Get supplementary calculations
        supp = self.pred.get('supplementary', {})

        output = PredictionOutput(
            match_id=self.input.match_id,
            home_team=self._get_team_name(self.input.home_team_id),
            away_team=self._get_team_name(self.input.away_team_id),
            competition=self._get_competition_name(self.input.competition_id),
            match_datetime=datetime.fromisoformat(self.input.match_datetime),

            probabilities=probs,
            most_likely_result=most_likely,
            most_likely_score=self.pred['most_likely_score'],

            expected_goals=self.pred['expected_goals'],

            over_under_2_5=supp.get('over_under', {}),
            both_teams_score=supp.get('btts', {}),
            clean_sheet_probability=supp.get('clean_sheet', {}),
            top_correct_scores=supp.get('correct_score_top5', []),

            confidence=conf,
            data_quality=quality,

            value_bets=self._identify_value_bets(),

            key_factors=key_factors,

            warnings=self.val['warnings'],
            data_sources_used=self._list_sources_used(),
            missing_data=self.data.get('_meta', {}).get('missing_data', [])
        )

        return output

    def _extract_key_factors(self) -> Dict[str, List[str]]:
        """Identify top 3 factors for each side"""
        features = self.data.get('processed_features', {})

        pro_home = []
        pro_away = []
        neutral = []

        # Form
        form_diff = features.get('home_form', 5) - features.get('away_form', 5)
        if form_diff > 2:
            pro_home.append(
                f"Superior recent form ({features.get('home_form', 5)}/10 "
                f"vs {features.get('away_form', 5)}/10)"
            )
        elif form_diff < -2:
            pro_away.append(
                f"Better form ({features.get('away_form', 5)}/10 "
                f"vs {features.get('home_form', 5)}/10)"
            )

        # Injuries
        home_absences = features.get('home_key_absences', 0)
        away_absences = features.get('away_key_absences', 0)

        if home_absences == 0 and away_absences >= 2:
            pro_home.append(
                f"Full strength squad vs {away_absences} key absences"
            )
        elif away_absences == 0 and home_absences >= 2:
            pro_away.append(
                f"No injuries vs {home_absences} missing key players"
            )

        # Home advantage
        home_adv = features.get('home_field_advantage', 6)
        if home_adv >= 7:
            pro_home.append("Strong home advantage (crowd support)")

        # Motivation
        motiv_diff = features.get('home_motivation', 5) - features.get('away_motivation', 5)
        if motiv_diff > 2:
            pro_home.append(
                f"Higher stakes motivation ({features.get('home_motivation', 5)}/10)"
            )
        elif motiv_diff < -2:
            pro_away.append(
                f"Greater motivation ({features.get('away_motivation', 5)}/10)"
            )

        # H2H
        h2h_adv = features.get('h2h_home_advantage', 0)
        if h2h_adv > 0.5:
            pro_home.append("Psychological edge from recent H2H dominance")
        elif h2h_adv < -0.5:
            pro_away.append("Historical dominance in this fixture")
        else:
            h2h_matches = features.get('h2h_matches', 0)
            if h2h_matches > 0:
                neutral.append(f"Balanced H2H record ({h2h_matches} matches)")

        # Tactical
        tactical = features.get('tactical_matchup_score', 0)
        if abs(tactical) < 0.2:
            neutral.append("Even tactical matchup")

        return {
            "pro_home": pro_home[:3],  # Top 3
            "pro_away": pro_away[:3],
            "neutral": neutral[:2]
        }

    def _identify_value_bets(self) -> List[Dict]:
        """Identify value bets vs market odds"""
        odds_data = self.data.get('odds', {}).get('data')

        if not odds_data:
            return []

        value_bets = []
        threshold = 0.05  # Minimum 5% edge

        probs = self.pred['probabilities']

        for outcome in ['1', 'X', '2']:
            our_prob = probs[outcome]
            market_prob = odds_data.get(f'implied_prob_{outcome}')

            if not market_prob:
                continue

            edge = our_prob - market_prob

            if edge > threshold:
                odds = odds_data.get(f'odds_{outcome}', 1.0)
                value_bets.append({
                    "outcome": outcome,
                    "our_probability": round(our_prob, 4),
                    "market_probability": round(market_prob, 4),
                    "edge": round(edge, 4),
                    "odds": odds,
                    "expected_value": round((our_prob * odds) - 1, 4)
                })

        return sorted(value_bets, key=lambda x: x['edge'], reverse=True)

    def _list_sources_used(self) -> List[str]:
        """List data sources actually used"""
        sources = set()

        for key, value in self.data.items():
            if isinstance(value, dict) and 'source' in value:
                source = value['source']
                if source and source != 'none':
                    sources.add(source)

        return sorted(list(sources))

    def _get_team_name(self, team_id: int) -> str:
        """Get team name from ID"""
        # In production: query database
        # For now: placeholder
        return f"Team_{team_id}"

    def _get_competition_name(self, comp_id: int) -> str:
        """Get competition name from ID"""
        competitions = {
            39: "Premier League",
            140: "La Liga",
            135: "Serie A",
            78: "Bundesliga",
            61: "Ligue 1",
            2: "UEFA Champions League",
        }
        return competitions.get(comp_id, f"Competition_{comp_id}")


def save_prediction(output: PredictionOutput, format: str = "json"):
    """
    Save prediction to file

    Args:
        output: PredictionOutput object
        format: 'json', 'markdown', or 'db'
    """
    predictions_dir = Path("predictions")
    predictions_dir.mkdir(exist_ok=True)

    if format == "json":
        filepath = predictions_dir / f"match_{output.match_id}.json"
        with open(filepath, "w") as f:
            f.write(output.model_dump_json(indent=2))
        logger.info(f"Saved JSON prediction to {filepath}")

    elif format == "markdown":
        filepath = predictions_dir / f"match_{output.match_id}.md"
        md_content = _generate_markdown_report(output)
        with open(filepath, "w") as f:
            f.write(md_content)
        logger.info(f"Saved Markdown report to {filepath}")

    elif format == "db":
        # Save to database
        _save_to_database(output)
        logger.info(f"Saved prediction to database (match_id={output.match_id})")


def _generate_markdown_report(output: PredictionOutput) -> str:
    """Generate Markdown report"""

    md = f"""
# Match Prediction Report

**{output.home_team} vs {output.away_team}**
*{output.competition} - {output.match_datetime.strftime('%Y-%m-%d %H:%M')}*

---

## 🎯 Prediction

| Outcome | Probability | Odds Equivalent |
|---------|-------------|-----------------|
| Home Win (1) | {output.probabilities['1']:.1%} | {1/output.probabilities['1']:.2f} |
| Draw (X) | {output.probabilities['X']:.1%} | {1/output.probabilities['X']:.2f} |
| Away Win (2) | {output.probabilities['2']:.1%} | {1/output.probabilities['2']:.2f} |

**Most Likely Result:** {output.most_likely_result}
**Most Likely Score:** {output.most_likely_score}
**Confidence:** {output.confidence:.1%} ({output.data_quality})

---

## 📊 Expected Goals

- **{output.home_team}:** {output.expected_goals['home']}
- **{output.away_team}:** {output.expected_goals['away']}

---

## 🔑 Key Factors

### Pro {output.home_team}
{chr(10).join(f'✅ {f}' for f in output.key_factors['pro_home']) if output.key_factors['pro_home'] else '*None identified*'}

### Pro {output.away_team}
{chr(10).join(f'✅ {f}' for f in output.key_factors['pro_away']) if output.key_factors['pro_away'] else '*None identified*'}

### Neutral Factors
{chr(10).join(f'⚖️ {f}' for f in output.key_factors['neutral']) if output.key_factors['neutral'] else '*None*'}

---

## 💰 Value Bets

{chr(10).join(f"- **{vb['outcome']}** @ {vb['odds']}: {vb['edge']:.1%} edge (EV: {vb['expected_value']:.2f})" for vb in output.value_bets) if output.value_bets else '*No value identified*'}

---

## 📈 Supplementary Markets

### Over/Under 2.5 Goals
- **Over 2.5:** {output.over_under_2_5.get('over_2.5', 0):.1%}
- **Under 2.5:** {output.over_under_2_5.get('under_2.5', 0):.1%}

### Both Teams To Score (BTTS)
- **Yes:** {output.both_teams_score.get('btts_yes', 0):.1%}
- **No:** {output.both_teams_score.get('btts_no', 0):.1%}

### Top 5 Most Likely Scores
{chr(10).join(f"{i+1}. **{score['score']}**: {score['probability']:.2%}" for i, score in enumerate(output.top_correct_scores[:5]))}

---

## ⚠️ Warnings

{chr(10).join(f'- {w}' for w in output.warnings) if output.warnings else '*None*'}

---

## 📡 Data Sources

{', '.join(output.data_sources_used) if output.data_sources_used else '*None*'}

---

*Generated by AI Prediction System v{output.model_version} at {output.generated_at.strftime('%Y-%m-%d %H:%M:%S')}*
"""

    return md


def _save_to_database(output: PredictionOutput):
    """Save prediction to database"""
    from database import get_db

    with get_db() as db:
        # Create prediction record
        from database.models import Prediction

        pred = Prediction(
            match_id=output.match_id,
            model_version=output.model_version,
            prob_home=output.probabilities['1'],
            prob_draw=output.probabilities['X'],
            prob_away=output.probabilities['2'],
            expected_goals_home=output.expected_goals['home'],
            expected_goals_away=output.expected_goals['away'],
            predicted_result=output.most_likely_result,
            predicted_score=output.most_likely_score,
            prob_over_2_5=output.over_under_2_5.get('over_2.5'),
            prob_under_2_5=output.over_under_2_5.get('under_2.5'),
            prob_btts_yes=output.both_teams_score.get('btts_yes'),
            prob_btts_no=output.both_teams_score.get('btts_no'),
            prob_home_clean_sheet=output.clean_sheet_probability.get('home_clean_sheet'),
            prob_away_clean_sheet=output.clean_sheet_probability.get('away_clean_sheet'),
            confidence=output.confidence,
            data_quality=output.data_quality,
            value_bets=output.value_bets if output.value_bets else None,
            input_features=output.raw_features,
        )

        db.add(pred)
        db.commit()

        logger.info(f"Saved prediction to database (ID: {pred.id})")
