-- Football Prediction System Database Schema
-- PostgreSQL 14+

-- Drop existing tables if they exist
DROP TABLE IF EXISTS prediction_results CASCADE;
DROP TABLE IF EXISTS predictions CASCADE;
DROP TABLE IF EXISTS player_availability CASCADE;
DROP TABLE IF EXISTS team_stats CASCADE;
DROP TABLE IF EXISTS matches CASCADE;
DROP TABLE IF EXISTS team_rivalries CASCADE;
DROP TABLE IF EXISTS stadiums CASCADE;
DROP TABLE IF EXISTS teams CASCADE;
DROP TABLE IF EXISTS competitions CASCADE;

-- Competitions table
CREATE TABLE competitions (
    id SERIAL PRIMARY KEY,
    external_id INT UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    country VARCHAR(50),
    type VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Teams table
CREATE TABLE teams (
    id SERIAL PRIMARY KEY,
    external_id INT UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    short_name VARCHAR(50),
    country VARCHAR(50),
    founded INT,
    logo_url TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Stadiums table
CREATE TABLE stadiums (
    id SERIAL PRIMARY KEY,
    team_id INT UNIQUE REFERENCES teams(id) ON DELETE CASCADE,
    name VARCHAR(100),
    latitude NUMERIC(9,6),
    longitude NUMERIC(9,6),
    capacity INT,
    avg_attendance_pct NUMERIC(4,3),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Team rivalries (pre-populated)
CREATE TABLE team_rivalries (
    id SERIAL PRIMARY KEY,
    team_a_id INT NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    team_b_id INT NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    rivalry_level INT CHECK (rivalry_level BETWEEN 1 AND 10),
    rivalry_name VARCHAR(100),
    UNIQUE(team_a_id, team_b_id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Matches table
CREATE TABLE matches (
    match_id BIGINT PRIMARY KEY,
    home_team_id INT NOT NULL REFERENCES teams(id),
    away_team_id INT NOT NULL REFERENCES teams(id),
    competition_id INT REFERENCES competitions(id),
    match_datetime TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20),
    home_score INT,
    away_score INT,
    venue VARCHAR(100),
    referee VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Team statistics
CREATE TABLE team_stats (
    id SERIAL PRIMARY KEY,
    team_id INT NOT NULL REFERENCES teams(id),
    match_id BIGINT REFERENCES matches(match_id),
    season VARCHAR(10),

    -- Goals
    xg NUMERIC(4,2),
    xga NUMERIC(4,2),
    goals_scored INT,
    goals_conceded INT,

    -- Possession & Passing
    possession NUMERIC(4,1),
    passes_completed INT,
    passes_attempted INT,
    pass_accuracy NUMERIC(4,1),

    -- Shots
    shots INT,
    shots_on_target INT,
    shots_off_target INT,

    -- Defensive
    tackles INT,
    interceptions INT,
    ppda NUMERIC(5,2),

    -- Metadata
    data_source VARCHAR(50),
    confidence NUMERIC(3,2),
    fetched_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(team_id, match_id)
);

-- Player availability (injuries/suspensions)
CREATE TABLE player_availability (
    id SERIAL PRIMARY KEY,
    player_id BIGINT NOT NULL,
    player_name VARCHAR(100),
    team_id INT NOT NULL REFERENCES teams(id),
    match_id BIGINT REFERENCES matches(match_id),
    status VARCHAR(20), -- 'injured', 'suspended', 'doubtful', 'available'
    injury_type VARCHAR(100),
    importance_score NUMERIC(3,1) CHECK (importance_score BETWEEN 1.0 AND 10.0),
    expected_return DATE,
    data_source VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Predictions
CREATE TABLE predictions (
    id SERIAL PRIMARY KEY,
    match_id BIGINT NOT NULL REFERENCES matches(match_id),

    -- Probabilities
    prob_home NUMERIC(4,3) CHECK (prob_home BETWEEN 0 AND 1),
    prob_draw NUMERIC(4,3) CHECK (prob_draw BETWEEN 0 AND 1),
    prob_away NUMERIC(4,3) CHECK (prob_away BETWEEN 0 AND 1),

    -- Expected goals
    predicted_score_home NUMERIC(3,1),
    predicted_score_away NUMERIC(3,1),

    -- Most likely
    most_likely_result VARCHAR(1),
    most_likely_score VARCHAR(10),

    -- Quality metrics
    confidence NUMERIC(3,2),
    data_quality VARCHAR(10),

    -- Model info
    model_version VARCHAR(20),
    ensemble_method VARCHAR(50),

    -- Raw data (JSON)
    raw_features JSONB,
    warnings JSONB,

    created_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT prob_sum_check CHECK (
        ABS((prob_home + prob_draw + prob_away) - 1.0) < 0.01
    )
);

-- Prediction results (post-match evaluation)
CREATE TABLE prediction_results (
    id SERIAL PRIMARY KEY,
    prediction_id INT NOT NULL REFERENCES predictions(id) ON DELETE CASCADE,

    -- Actual outcome
    actual_result VARCHAR(1), -- '1', 'X', '2'
    actual_score VARCHAR(10),

    -- Evaluation
    predicted_result VARCHAR(1),
    correct_result BOOLEAN,
    probability_actual NUMERIC(4,3),

    -- Accuracy metrics
    brier_score NUMERIC(5,4), -- Probability accuracy metric
    log_loss NUMERIC(6,4),

    -- Analysis
    factors_review JSONB,

    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(prediction_id)
);

-- Indexes for performance
CREATE INDEX idx_matches_datetime ON matches(match_datetime);
CREATE INDEX idx_matches_status ON matches(status);
CREATE INDEX idx_matches_competition ON matches(competition_id);
CREATE INDEX idx_matches_teams ON matches(home_team_id, away_team_id);

CREATE INDEX idx_team_stats_team ON team_stats(team_id);
CREATE INDEX idx_team_stats_match ON team_stats(match_id);
CREATE INDEX idx_team_stats_season ON team_stats(season);

CREATE INDEX idx_player_availability_team ON player_availability(team_id);
CREATE INDEX idx_player_availability_match ON player_availability(match_id);
CREATE INDEX idx_player_availability_status ON player_availability(status);

CREATE INDEX idx_predictions_match ON predictions(match_id);
CREATE INDEX idx_predictions_created ON predictions(created_at DESC);

CREATE INDEX idx_prediction_results_prediction ON prediction_results(prediction_id);
CREATE INDEX idx_prediction_results_correct ON prediction_results(correct_result);

-- Views for common queries

-- View: Recent prediction accuracy
CREATE VIEW v_recent_prediction_accuracy AS
SELECT
    DATE_TRUNC('week', pr.created_at) as week,
    COUNT(*) as total_predictions,
    SUM(CASE WHEN pr.correct_result THEN 1 ELSE 0 END) as correct_predictions,
    ROUND(AVG(CASE WHEN pr.correct_result THEN 1.0 ELSE 0.0 END), 3) as accuracy,
    ROUND(AVG(pr.brier_score), 4) as avg_brier_score
FROM prediction_results pr
GROUP BY DATE_TRUNC('week', pr.created_at)
ORDER BY week DESC;

-- View: Team performance summary
CREATE VIEW v_team_performance AS
SELECT
    t.id,
    t.name,
    COUNT(DISTINCT ts.match_id) as matches_analyzed,
    ROUND(AVG(ts.xg), 2) as avg_xg,
    ROUND(AVG(ts.xga), 2) as avg_xga,
    ROUND(AVG(ts.possession), 1) as avg_possession,
    ROUND(AVG(ts.pass_accuracy), 1) as avg_pass_accuracy
FROM teams t
JOIN team_stats ts ON t.id = ts.team_id
GROUP BY t.id, t.name;

-- Comments
COMMENT ON TABLE matches IS 'Stores football match information';
COMMENT ON TABLE predictions IS 'AI-generated predictions for matches';
COMMENT ON TABLE prediction_results IS 'Post-match evaluation of prediction accuracy';
COMMENT ON TABLE team_stats IS 'Team statistics from various sources';
COMMENT ON TABLE player_availability IS 'Player injury and suspension tracking';
