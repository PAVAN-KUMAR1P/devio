-- =============================================================================
-- InfraSense – Stages 11 to 15 : SQLite Schema, Data Population & Analysis
-- Project  : InfraSense – Karnataka District Development Analysis
-- Database : InfraSense_Production.db
-- Coverage : 31 Karnataka districts · 14 indicators · 6 dimensions
-- Data     : SYNTHETIC (all numeric values are pseudo-random placeholders)
-- =============================================================================
-- HOW TO RUN
--   sqlite3 InfraSense_Production.db
--   .read InfraSense_Stages_11_to_15_SQLite.sql
-- Or paste into DB Browser for SQLite → Execute SQL → Execute All.
-- =============================================================================

PRAGMA foreign_keys = ON;
PRAGMA journal_mode  = WAL;

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 0 : SCHEMA CREATION
-- ─────────────────────────────────────────────────────────────────────────────

-- 0.1  Core master tables
CREATE TABLE IF NOT EXISTS district_master (
    district_id      TEXT PRIMARY KEY,          -- e.g. KA-001
    district_name    TEXT NOT NULL,
    census_2011_code INTEGER,
    area_km2         REAL,                       -- district geographical area
    population       INTEGER,
    notes            TEXT
);

CREATE TABLE IF NOT EXISTS indicator_master (
    indicator_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    indicator_code  TEXT UNIQUE NOT NULL,        -- short snake_case key
    indicator_name  TEXT NOT NULL,
    dimension       TEXT NOT NULL,               -- one of the 6 dimensions
    unit            TEXT,
    direction       TEXT NOT NULL CHECK(direction IN ('positive','negative')),
    description     TEXT
);

CREATE TABLE IF NOT EXISTS data_sources (
    source_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    dataset_name    TEXT,
    department      TEXT,
    source_url      TEXT,
    reference_year  TEXT,
    coverage        TEXT,
    extraction_method TEXT,
    limitations     TEXT
);

-- 0.2  Raw and processed data
CREATE TABLE IF NOT EXISTS raw_observations (
    obs_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    district_id     TEXT REFERENCES district_master(district_id),
    indicator_code  TEXT REFERENCES indicator_master(indicator_code),
    raw_value       REAL,
    unit            TEXT,
    reference_year  TEXT,
    source_id       INTEGER REFERENCES data_sources(source_id),
    data_status     TEXT,
    notes           TEXT
);

CREATE TABLE IF NOT EXISTS processed_indicators (
    proc_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    district_id     TEXT REFERENCES district_master(district_id),
    indicator_code  TEXT REFERENCES indicator_master(indicator_code),
    processed_value REAL,
    unit            TEXT,
    reference_year  TEXT,
    data_status     TEXT
);

-- 0.3  Stage 11 – Normalisation
CREATE TABLE IF NOT EXISTS normalization_config (
    indicator_code  TEXT PRIMARY KEY REFERENCES indicator_master(indicator_code),
    direction       TEXT NOT NULL CHECK(direction IN ('positive','negative')),
    observed_min    REAL NOT NULL,
    observed_max    REAL NOT NULL,
    method          TEXT DEFAULT 'min-max'
);

CREATE TABLE IF NOT EXISTS normalized_indicators (
    norm_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    district_id     TEXT REFERENCES district_master(district_id),
    indicator_code  TEXT REFERENCES indicator_master(indicator_code),
    normalized_score REAL,                       -- 0–100
    UNIQUE(district_id, indicator_code)
);

-- 0.4  Stage 12 – Weights and scoring
CREATE TABLE IF NOT EXISTS indicator_weights (
    indicator_code  TEXT PRIMARY KEY REFERENCES indicator_master(indicator_code),
    weight          REAL NOT NULL,               -- relative weight within its dimension
    rationale       TEXT
);

CREATE TABLE IF NOT EXISTS dimension_weights (
    dimension       TEXT PRIMARY KEY,
    weight          REAL NOT NULL,               -- relative weight in overall score
    rationale       TEXT
);

CREATE TABLE IF NOT EXISTS district_scores (
    score_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    district_id     TEXT REFERENCES district_master(district_id),
    score_type      TEXT NOT NULL CHECK(score_type IN ('dimension','overall')),
    dimension       TEXT,
    score           REAL,
    weight_coverage REAL,                        -- fraction of weight that had data
    is_valid        INTEGER DEFAULT 1,           -- 0 when below coverage threshold
    UNIQUE(district_id, score_type, dimension)
);

-- 0.5  Stage 13 – Rankings (views defined later in this file)

-- 0.6  Stage 15 – ML outputs
CREATE TABLE IF NOT EXISTS analysis_runs (
    run_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    run_name        TEXT,
    algorithm       TEXT,
    parameters      TEXT,                        -- JSON string
    created_at      TEXT DEFAULT (datetime('now')),
    notes           TEXT
);

CREATE TABLE IF NOT EXISTS district_clusters (
    cluster_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id          INTEGER REFERENCES analysis_runs(run_id),
    district_id     TEXT REFERENCES district_master(district_id),
    cluster_label   INTEGER,
    cluster_name    TEXT,
    distance_to_centroid REAL
);

CREATE TABLE IF NOT EXISTS model_explanations (
    explanation_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id          INTEGER REFERENCES analysis_runs(run_id),
    district_id     TEXT REFERENCES district_master(district_id),
    indicator_code  TEXT REFERENCES indicator_master(indicator_code),
    shap_value      REAL,
    feature_importance REAL
);

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 1 : MASTER DATA POPULATION
-- ─────────────────────────────────────────────────────────────────────────────

-- 1.1  District master (31 Karnataka districts)
INSERT OR IGNORE INTO district_master VALUES
('KA-001','Bagalkote',      2, 6595.0, 1889752, NULL),
('KA-002','Ballari',       11, 8088.7, 1690215, 'Reduced after Vijayanagara split (2021)'),
('KA-003','Belagavi',       1, 5499.5, 1527944, NULL),
('KA-004','Bengaluru Rural',3, 2259.0,  990923, NULL),
('KA-005','Bengaluru Urban',4, 2191.0, 9621551, NULL),
('KA-006','Bidar',         18, 5448.0, 1697718, NULL),
('KA-007','Chamarajanagar',28, 5101.0, 1020791, NULL),
('KA-008','Chikkaballapura',5, 4215.0,  722262, NULL),
('KA-009','Chikkamagaluru', 6, 7201.0,  558234, NULL),
('KA-010','Chitradurga',   7, 8440.0, 1660378, NULL),
('KA-011','Dakshina Kannada',8,4560.0,2089649, NULL),
('KA-012','Davanagere',    9, 5926.0, 1946905, NULL),
('KA-013','Dharwad',      10, 4260.0, 1847024, NULL),
('KA-014','Gadag',        12, 4657.0, 1065235, NULL),
('KA-015','Hassan',       13, 6826.0, 1776421, NULL),
('KA-016','Haveri',       14, 4851.0, 1598506, NULL),
('KA-017','Kalaburagi',   15, 10952.0,2564892, NULL),
('KA-018','Kodagu',       16, 4102.0,  554762, NULL),
('KA-019','Kolar',        17, 3969.0, 1540462, NULL),
('KA-020','Koppal',       19, 7189.0, 1388007, NULL),
('KA-021','Mandya',       20, 4953.0, 1808680, NULL),
('KA-022','Mysuru',       21, 6854.0, 3001127, NULL),
('KA-023','Raichur',      22, 6827.0, 1924773, NULL),
('KA-024','Ramanagara',   23, 3573.0, 1082739, NULL),
('KA-025','Shivamogga',   24, 8465.0, 1752753, NULL),
('KA-026','Tumakuru',     25, 10598.0,2679490, NULL),
('KA-027','Udupi',        26, 3598.0, 1177361, NULL),
('KA-028','Uttara Kannada',27,10291.0,1437169, NULL),
('KA-029','Vijayapura',   29, 5281.0, 2175671, NULL),
('KA-030','Yadgir',       30, 5765.0, 1172985, NULL),
('KA-031','Vijayanagara', 31, 7497.0, 1322822, 'New district carved from Ballari (2021)');

-- 1.2  Indicator master (14 calculated indicators across 6 dimensions)
INSERT OR IGNORE INTO indicator_master
    (indicator_code, indicator_name, dimension, unit, direction, description) VALUES
-- Infrastructure (3)
('road_density',     'Road density',               'Infrastructure',
  'km per km²', 'positive', 'Total road length divided by district area'),
('rural_connectivity','Rural connectivity',         'Infrastructure',
  '%',          'positive', 'Connected rural habitations as % of total habitations'),
('pt_coverage',      'Public transport coverage',  'Infrastructure',
  '% of pop',   'positive', 'Population served by public transport as % of district population'),
-- Digital Access (2)
('internet_penetration','Household internet penetration','Digital Access',
  '%',          'positive', 'Households with internet access as % of total households'),
('broadband_per1k',  'Broadband per 1,000 population','Digital Access',
  'per 1,000',  'positive', 'Broadband connections per 1,000 district population'),
-- Industry (2)
('msme_density',     'MSME density',               'Industry',
  'per 1,000',  'positive', 'Total enterprises per 1,000 district population'),
('industrial_emp_rate','Industrial employment rate','Industry',
  '%',          'positive', '% of working population in MSME employment'),
-- Innovation (2)
('startup_rate',     'Startups per 100,000',        'Innovation',
  'per 100,000','positive', 'DPIIT-recognised startups per 100,000 population'),
('patent_rate',      'Patent applications per 100,000','Innovation',
  'per 100,000','positive', 'Patent applications filed per 100,000 population'),
-- Energy & Environment (4)
('renewable_capacity','Renewable energy capacity',  'Energy & Environment',
  'MW',         'positive', 'Total installed renewable energy capacity (solar+wind+biomass+other)'),
('pm25',             'Annual average PM2.5',        'Energy & Environment',
  'µg/m³',      'negative', 'Lower is better – negative indicator'),
('forest_cover_pct', 'Forest cover percentage',    'Energy & Environment',
  '% of area',  'positive', 'Forest cover as % of district geographical area'),
('waste_processing_pct','Waste processing rate',   'Energy & Environment',
  '%',          'positive', '% of total waste generated that is processed'),
-- Human Capital (1)
('literacy_rate',    'Literacy rate (7+)',          'Human Capital',
  '%',          'positive', 'Literate population aged 7+ as % of population 7+');

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 2 : PROCESSED INDICATOR OBSERVATIONS  (synthetic dataset)
-- ─────────────────────────────────────────────────────────────────────────────
-- Values sourced from the CALC: columns in the synthetic Excel workbook.
-- !! These are NOT government data. Replace with real observations when available. !!

INSERT OR IGNORE INTO processed_indicators
    (district_id, indicator_code, processed_value, unit, reference_year, data_status)
VALUES

('KA-001','road_density',          1.307722,'km per km²','2024-SYNTH','SYNTHETIC'),
('KA-001','rural_connectivity',   91.335227,'%','2024-SYNTH','SYNTHETIC'),
('KA-001','pt_coverage',          72.414703,'%','2024-SYNTH','SYNTHETIC'),
('KA-001','internet_penetration', 33.970896,'%','2024-SYNTH','SYNTHETIC'),
('KA-001','broadband_per1k',     101.879073,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-001','msme_density',          6.334347,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-001','industrial_emp_rate',   5.458310,'%','2024-SYNTH','SYNTHETIC'),
('KA-001','startup_rate',          2.164735,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-001','patent_rate',           0.832590,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-001','renewable_capacity',  2537.800000,'MW','2024-SYNTH','SYNTHETIC'),
('KA-001','pm25',                  43.500000,'µg/m³','2024-SYNTH','SYNTHETIC'),
('KA-001','forest_cover_pct',     24.457079,'%','2024-SYNTH','SYNTHETIC'),
('KA-001','waste_processing_pct', 78.472222,'%','2024-SYNTH','SYNTHETIC'),
('KA-001','literacy_rate',        71.957730,'%','2024-SYNTH','SYNTHETIC'),

('KA-002','road_density',          1.433976,'km per km²','2024-SYNTH','SYNTHETIC'),
('KA-002','rural_connectivity',   91.379310,'%','2024-SYNTH','SYNTHETIC'),
('KA-002','pt_coverage',          83.691542,'%','2024-SYNTH','SYNTHETIC'),
('KA-002','internet_penetration', 40.375980,'%','2024-SYNTH','SYNTHETIC'),
('KA-002','broadband_per1k',      50.971030,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-002','msme_density',          9.042637,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-002','industrial_emp_rate',   9.295706,'%','2024-SYNTH','SYNTHETIC'),
('KA-002','startup_rate',          2.603219,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-002','patent_rate',           0.769133,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-002','renewable_capacity',   597.000000,'MW','2024-SYNTH','SYNTHETIC'),
('KA-002','pm25',                  37.900000,'µg/m³','2024-SYNTH','SYNTHETIC'),
('KA-002','forest_cover_pct',     53.417731,'%','2024-SYNTH','SYNTHETIC'),
('KA-002','waste_processing_pct', 59.780908,'%','2024-SYNTH','SYNTHETIC'),
('KA-002','literacy_rate',        65.603993,'%','2024-SYNTH','SYNTHETIC'),

('KA-003','road_density',          0.962324,'km per km²','2024-SYNTH','SYNTHETIC'),
('KA-003','rural_connectivity',   98.560354,'%','2024-SYNTH','SYNTHETIC'),
('KA-003','pt_coverage',          80.642812,'%','2024-SYNTH','SYNTHETIC'),
('KA-003','internet_penetration', 20.078213,'%','2024-SYNTH','SYNTHETIC'),
('KA-003','broadband_per1k',      71.237558,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-003','msme_density',          7.311132,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-003','industrial_emp_rate',   7.647691,'%','2024-SYNTH','SYNTHETIC'),
('KA-003','startup_rate',          2.356107,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-003','patent_rate',           0.392685,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-003','renewable_capacity',  4128.400000,'MW','2024-SYNTH','SYNTHETIC'),
('KA-003','pm25',                  37.300000,'µg/m³','2024-SYNTH','SYNTHETIC'),
('KA-003','forest_cover_pct',     32.837531,'%','2024-SYNTH','SYNTHETIC'),
('KA-003','waste_processing_pct', 61.392405,'%','2024-SYNTH','SYNTHETIC'),
('KA-003','literacy_rate',        76.936846,'%','2024-SYNTH','SYNTHETIC'),

('KA-004','road_density',          0.676435,'km per km²','2024-SYNTH','SYNTHETIC'),
('KA-004','rural_connectivity',   92.822967,'%','2024-SYNTH','SYNTHETIC'),
('KA-004','pt_coverage',          73.291129,'%','2024-SYNTH','SYNTHETIC'),
('KA-004','internet_penetration', 32.005473,'%','2024-SYNTH','SYNTHETIC'),
('KA-004','broadband_per1k',     242.146774,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-004','msme_density',         12.699411,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-004','industrial_emp_rate',  16.241242,'%','2024-SYNTH','SYNTHETIC'),
('KA-004','startup_rate',          0.886648,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-004','patent_rate',           1.408206,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-004','renewable_capacity',  3225.400000,'MW','2024-SYNTH','SYNTHETIC'),
('KA-004','pm25',                  25.300000,'µg/m³','2024-SYNTH','SYNTHETIC'),
('KA-004','forest_cover_pct',     36.556522,'%','2024-SYNTH','SYNTHETIC'),
('KA-004','waste_processing_pct', 42.687277,'%','2024-SYNTH','SYNTHETIC'),
('KA-004','literacy_rate',        75.330588,'%','2024-SYNTH','SYNTHETIC'),

('KA-005','road_density',          1.003409,'km per km²','2024-SYNTH','SYNTHETIC'),
('KA-005','rural_connectivity',   81.005587,'%','2024-SYNTH','SYNTHETIC'),
('KA-005','pt_coverage',          73.891309,'%','2024-SYNTH','SYNTHETIC'),
('KA-005','internet_penetration', 50.266441,'%','2024-SYNTH','SYNTHETIC'),
('KA-005','broadband_per1k',      89.586455,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-005','msme_density',         10.573545,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-005','industrial_emp_rate',  10.295414,'%','2024-SYNTH','SYNTHETIC'),
('KA-005','startup_rate',        108.345455,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-005','patent_rate',          18.445455,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-005','renewable_capacity',  1614.400000,'MW','2024-SYNTH','SYNTHETIC'),
('KA-005','pm25',                  33.000000,'µg/m³','2024-SYNTH','SYNTHETIC'),
('KA-005','forest_cover_pct',     55.081818,'%','2024-SYNTH','SYNTHETIC'),
('KA-005','waste_processing_pct', 59.221392,'%','2024-SYNTH','SYNTHETIC'),
('KA-005','literacy_rate',        87.104092,'%','2024-SYNTH','SYNTHETIC'),

('KA-006','road_density',          1.465293,'km per km²','2024-SYNTH','SYNTHETIC'),
('KA-006','rural_connectivity',   92.880524,'%','2024-SYNTH','SYNTHETIC'),
('KA-006','pt_coverage',          79.872846,'%','2024-SYNTH','SYNTHETIC'),
('KA-006','internet_penetration', 42.160370,'%','2024-SYNTH','SYNTHETIC'),
('KA-006','broadband_per1k',      93.740180,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-006','msme_density',         11.895779,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-006','industrial_emp_rate',  15.010803,'%','2024-SYNTH','SYNTHETIC'),
('KA-006','startup_rate',          1.401034,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-006','patent_rate',           1.801329,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-006','renewable_capacity',  1363.500000,'MW','2024-SYNTH','SYNTHETIC'),
('KA-006','pm25',                  29.800000,'µg/m³','2024-SYNTH','SYNTHETIC'),
('KA-006','forest_cover_pct',      7.444692,'%','2024-SYNTH','SYNTHETIC'),
('KA-006','waste_processing_pct', 68.738230,'%','2024-SYNTH','SYNTHETIC'),
('KA-006','literacy_rate',        68.290000,'%','2024-SYNTH','SYNTHETIC'),

('KA-007','road_density',          0.529985,'km per km²','2024-SYNTH','SYNTHETIC'),
('KA-007','rural_connectivity',   97.363691,'%','2024-SYNTH','SYNTHETIC'),
('KA-007','pt_coverage',          85.756190,'%','2024-SYNTH','SYNTHETIC'),
('KA-007','internet_penetration', 19.158892,'%','2024-SYNTH','SYNTHETIC'),
('KA-007','broadband_per1k',     284.361310,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-007','msme_density',         10.292462,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-007','industrial_emp_rate',  10.323766,'%','2024-SYNTH','SYNTHETIC'),
('KA-007','startup_rate',          1.516436,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-007','patent_rate',           0.723753,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-007','renewable_capacity',  3261.600000,'MW','2024-SYNTH','SYNTHETIC'),
('KA-007','pm25',                  32.700000,'µg/m³','2024-SYNTH','SYNTHETIC'),
('KA-007','forest_cover_pct',     25.911030,'%','2024-SYNTH','SYNTHETIC'),
('KA-007','waste_processing_pct', 72.166818,'%','2024-SYNTH','SYNTHETIC'),
('KA-007','literacy_rate',        67.881910,'%','2024-SYNTH','SYNTHETIC'),

('KA-008','road_density',          1.487783,'km per km²','2024-SYNTH','SYNTHETIC'),
('KA-008','rural_connectivity',   92.894462,'%','2024-SYNTH','SYNTHETIC'),
('KA-008','pt_coverage',          58.338585,'%','2024-SYNTH','SYNTHETIC'),
('KA-008','internet_penetration', 50.262171,'%','2024-SYNTH','SYNTHETIC'),
('KA-008','broadband_per1k',     202.080312,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-008','msme_density',          8.020915,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-008','industrial_emp_rate',   8.539082,'%','2024-SYNTH','SYNTHETIC'),
('KA-008','startup_rate',          1.206153,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-008','patent_rate',           1.658460,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-008','renewable_capacity',  2032.800000,'MW','2024-SYNTH','SYNTHETIC'),
('KA-008','pm25',                  19.000000,'µg/m³','2024-SYNTH','SYNTHETIC'),
('KA-008','forest_cover_pct',     22.766198,'%','2024-SYNTH','SYNTHETIC'),
('KA-008','waste_processing_pct', 44.709898,'%','2024-SYNTH','SYNTHETIC'),
('KA-008','literacy_rate',        72.884315,'%','2024-SYNTH','SYNTHETIC'),

('KA-009','road_density',          0.507081,'km per km²','2024-SYNTH','SYNTHETIC'),
('KA-009','rural_connectivity',   81.595092,'%','2024-SYNTH','SYNTHETIC'),
('KA-009','pt_coverage',          73.363666,'%','2024-SYNTH','SYNTHETIC'),
('KA-009','internet_penetration', 28.221044,'%','2024-SYNTH','SYNTHETIC'),
('KA-009','broadband_per1k',     241.918000,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-009','msme_density',          4.571301,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-009','industrial_emp_rate',   6.272243,'%','2024-SYNTH','SYNTHETIC'),
('KA-009','startup_rate',          0.909126,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-009','patent_rate',           1.283473,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-009','renewable_capacity',  3007.700000,'MW','2024-SYNTH','SYNTHETIC'),
('KA-009','pm25',                  21.700000,'µg/m³','2024-SYNTH','SYNTHETIC'),
('KA-009','forest_cover_pct',     14.467414,'%','2024-SYNTH','SYNTHETIC'),
('KA-009','waste_processing_pct', 59.096176,'%','2024-SYNTH','SYNTHETIC'),
('KA-009','literacy_rate',        71.654766,'%','2024-SYNTH','SYNTHETIC'),

('KA-010','road_density',          1.171982,'km per km²','2024-SYNTH','SYNTHETIC'),
('KA-010','rural_connectivity',   93.685567,'%','2024-SYNTH','SYNTHETIC'),
('KA-010','pt_coverage',          76.519684,'%','2024-SYNTH','SYNTHETIC'),
('KA-010','internet_penetration', 15.476590,'%','2024-SYNTH','SYNTHETIC'),
('KA-010','broadband_per1k',     224.234332,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-010','msme_density',         11.486217,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-010','industrial_emp_rate',  12.744371,'%','2024-SYNTH','SYNTHETIC'),
('KA-010','startup_rate',          1.957986,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-010','patent_rate',           0.859604,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-010','renewable_capacity',  2602.700000,'MW','2024-SYNTH','SYNTHETIC'),
('KA-010','pm25',                  39.300000,'µg/m³','2024-SYNTH','SYNTHETIC'),
('KA-010','forest_cover_pct',     44.353792,'%','2024-SYNTH','SYNTHETIC'),
('KA-010','waste_processing_pct', 51.512287,'%','2024-SYNTH','SYNTHETIC'),
('KA-010','literacy_rate',        86.844565,'%','2024-SYNTH','SYNTHETIC'),

('KA-011','road_density',          0.798174,'km per km²','2024-SYNTH','SYNTHETIC'),
('KA-011','rural_connectivity',   98.679868,'%','2024-SYNTH','SYNTHETIC'),
('KA-011','pt_coverage',          81.443496,'%','2024-SYNTH','SYNTHETIC'),
('KA-011','internet_penetration', 21.120298,'%','2024-SYNTH','SYNTHETIC'),
('KA-011','broadband_per1k',     136.498750,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-011','msme_density',          8.329876,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-011','industrial_emp_rate',   7.796831,'%','2024-SYNTH','SYNTHETIC'),
('KA-011','startup_rate',          0.788015,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-011','patent_rate',           0.450294,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-011','renewable_capacity',  1845.200000,'MW','2024-SYNTH','SYNTHETIC'),
('KA-011','pm25',                  28.400000,'µg/m³','2024-SYNTH','SYNTHETIC'),
('KA-011','forest_cover_pct',     15.533867,'%','2024-SYNTH','SYNTHETIC'),
('KA-011','waste_processing_pct', 65.792474,'%','2024-SYNTH','SYNTHETIC'),
('KA-011','literacy_rate',        68.333758,'%','2024-SYNTH','SYNTHETIC'),

('KA-012','road_density',          1.460799,'km per km²','2024-SYNTH','SYNTHETIC'),
('KA-012','rural_connectivity',   91.811024,'%','2024-SYNTH','SYNTHETIC'),
('KA-012','pt_coverage',          80.986247,'%','2024-SYNTH','SYNTHETIC'),
('KA-012','internet_penetration', 18.722722,'%','2024-SYNTH','SYNTHETIC'),
('KA-012','broadband_per1k',     210.282958,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-012','msme_density',          5.384965,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-012','industrial_emp_rate',   7.489726,'%','2024-SYNTH','SYNTHETIC'),
('KA-012','startup_rate',          1.441275,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-012','patent_rate',           1.351196,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-012','renewable_capacity',  1114.400000,'MW','2024-SYNTH','SYNTHETIC'),
('KA-012','pm25',                  37.200000,'µg/m³','2024-SYNTH','SYNTHETIC'),
('KA-012','forest_cover_pct',     29.412354,'%','2024-SYNTH','SYNTHETIC'),
('KA-012','waste_processing_pct', 53.459119,'%','2024-SYNTH','SYNTHETIC'),
('KA-012','literacy_rate',        82.203244,'%','2024-SYNTH','SYNTHETIC'),

('KA-013','road_density',          1.556727,'km per km²','2024-SYNTH','SYNTHETIC'),
('KA-013','rural_connectivity',   91.666667,'%','2024-SYNTH','SYNTHETIC'),
('KA-013','pt_coverage',          61.338166,'%','2024-SYNTH','SYNTHETIC'),
('KA-013','internet_penetration', 45.338087,'%','2024-SYNTH','SYNTHETIC'),
('KA-013','broadband_per1k',     177.802261,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-013','msme_density',          4.726283,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-013','industrial_emp_rate',   5.631713,'%','2024-SYNTH','SYNTHETIC'),
('KA-013','startup_rate',          2.175423,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-013','patent_rate',           1.649111,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-013','renewable_capacity',  2705.800000,'MW','2024-SYNTH','SYNTHETIC'),
('KA-013','pm25',                  37.700000,'µg/m³','2024-SYNTH','SYNTHETIC'),
('KA-013','forest_cover_pct',     16.627889,'%','2024-SYNTH','SYNTHETIC'),
('KA-013','waste_processing_pct', 73.093777,'%','2024-SYNTH','SYNTHETIC'),
('KA-013','literacy_rate',        74.822657,'%','2024-SYNTH','SYNTHETIC'),

('KA-014','road_density',          1.259664,'km per km²','2024-SYNTH','SYNTHETIC'),
('KA-014','rural_connectivity',   82.449857,'%','2024-SYNTH','SYNTHETIC'),
('KA-014','pt_coverage',          66.691542,'%','2024-SYNTH','SYNTHETIC'),
('KA-014','internet_penetration', 41.218914,'%','2024-SYNTH','SYNTHETIC'),
('KA-014','broadband_per1k',     173.177265,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-014','msme_density',          6.964980,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-014','industrial_emp_rate',   8.210140,'%','2024-SYNTH','SYNTHETIC'),
('KA-014','startup_rate',          1.392996,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-014','patent_rate',           1.724662,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-014','renewable_capacity',  2264.700000,'MW','2024-SYNTH','SYNTHETIC'),
('KA-014','pm25',                  30.000000,'µg/m³','2024-SYNTH','SYNTHETIC'),
('KA-014','forest_cover_pct',     47.072793,'%','2024-SYNTH','SYNTHETIC'),
('KA-014','waste_processing_pct', 40.521739,'%','2024-SYNTH','SYNTHETIC'),
('KA-014','literacy_rate',        80.774842,'%','2024-SYNTH','SYNTHETIC'),

('KA-015','road_density',          1.238690,'km per km²','2024-SYNTH','SYNTHETIC'),
('KA-015','rural_connectivity',   98.348018,'%','2024-SYNTH','SYNTHETIC'),
('KA-015','pt_coverage',          77.163099,'%','2024-SYNTH','SYNTHETIC'),
('KA-015','internet_penetration', 45.100529,'%','2024-SYNTH','SYNTHETIC'),
('KA-015','broadband_per1k',     255.777041,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-015','msme_density',         11.982835,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-015','industrial_emp_rate',  15.723097,'%','2024-SYNTH','SYNTHETIC'),
('KA-015','startup_rate',          2.407679,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-015','patent_rate',           1.852061,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-015','renewable_capacity',  2236.200000,'MW','2024-SYNTH','SYNTHETIC'),
('KA-015','pm25',                  35.800000,'µg/m³','2024-SYNTH','SYNTHETIC'),
('KA-015','forest_cover_pct',     24.268329,'%','2024-SYNTH','SYNTHETIC'),
('KA-015','waste_processing_pct', 46.740638,'%','2024-SYNTH','SYNTHETIC'),
('KA-015','literacy_rate',        65.554454,'%','2024-SYNTH','SYNTHETIC'),

('KA-016','road_density',          1.353624,'km per km²','2024-SYNTH','SYNTHETIC'),
('KA-016','rural_connectivity',   91.374663,'%','2024-SYNTH','SYNTHETIC'),
('KA-016','pt_coverage',          93.237364,'%','2024-SYNTH','SYNTHETIC'),
('KA-016','internet_penetration', 52.507672,'%','2024-SYNTH','SYNTHETIC'),
('KA-016','broadband_per1k',      62.371313,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-016','msme_density',         10.788239,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-016','industrial_emp_rate',  13.539081,'%','2024-SYNTH','SYNTHETIC'),
('KA-016','startup_rate',          2.565713,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-016','patent_rate',           0.408182,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-016','renewable_capacity',  1000.200000,'MW','2024-SYNTH','SYNTHETIC'),
('KA-016','pm25',                  27.500000,'µg/m³','2024-SYNTH','SYNTHETIC'),
('KA-016','forest_cover_pct',     45.660033,'%','2024-SYNTH','SYNTHETIC'),
('KA-016','waste_processing_pct', 38.636364,'%','2024-SYNTH','SYNTHETIC'),
('KA-016','literacy_rate',        70.304184,'%','2024-SYNTH','SYNTHETIC'),

('KA-017','road_density',          1.250581,'km per km²','2024-SYNTH','SYNTHETIC'),
('KA-017','rural_connectivity',   87.328767,'%','2024-SYNTH','SYNTHETIC'),
('KA-017','pt_coverage',          62.380546,'%','2024-SYNTH','SYNTHETIC'),
('KA-017','internet_penetration', 38.059635,'%','2024-SYNTH','SYNTHETIC'),
('KA-017','broadband_per1k',     288.379589,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-017','msme_density',         10.646328,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-017','industrial_emp_rate',  14.415653,'%','2024-SYNTH','SYNTHETIC'),
('KA-017','startup_rate',          1.513863,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-017','patent_rate',           1.020977,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-017','renewable_capacity',   787.200000,'MW','2024-SYNTH','SYNTHETIC'),
('KA-017','pm25',                  18.400000,'µg/m³','2024-SYNTH','SYNTHETIC'),
('KA-017','forest_cover_pct',     47.236952,'%','2024-SYNTH','SYNTHETIC'),
('KA-017','waste_processing_pct', 60.365425,'%','2024-SYNTH','SYNTHETIC'),
('KA-017','literacy_rate',        76.477498,'%','2024-SYNTH','SYNTHETIC'),

('KA-018','road_density',          0.664866,'km per km²','2024-SYNTH','SYNTHETIC'),
('KA-018','rural_connectivity',   97.485493,'%','2024-SYNTH','SYNTHETIC'),
('KA-018','pt_coverage',          93.527129,'%','2024-SYNTH','SYNTHETIC'),
('KA-018','internet_penetration', 37.289436,'%','2024-SYNTH','SYNTHETIC'),
('KA-018','broadband_per1k',      68.167119,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-018','msme_density',          6.286688,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-018','industrial_emp_rate',   6.380688,'%','2024-SYNTH','SYNTHETIC'),
('KA-018','startup_rate',          2.250171,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-018','patent_rate',           1.887240,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-018','renewable_capacity',  2061.400000,'MW','2024-SYNTH','SYNTHETIC'),
('KA-018','pm25',                  38.000000,'µg/m³','2024-SYNTH','SYNTHETIC'),
('KA-018','forest_cover_pct',     15.895286,'%','2024-SYNTH','SYNTHETIC'),
('KA-018','waste_processing_pct', 44.504749,'%','2024-SYNTH','SYNTHETIC'),
('KA-018','literacy_rate',        72.057095,'%','2024-SYNTH','SYNTHETIC'),

('KA-019','road_density',          1.264156,'km per km²','2024-SYNTH','SYNTHETIC'),
('KA-019','rural_connectivity',   90.891841,'%','2024-SYNTH','SYNTHETIC'),
('KA-019','pt_coverage',          60.898346,'%','2024-SYNTH','SYNTHETIC'),
('KA-019','internet_penetration', 44.837778,'%','2024-SYNTH','SYNTHETIC'),
('KA-019','broadband_per1k',     133.206470,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-019','msme_density',          7.495166,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-019','industrial_emp_rate',   8.422675,'%','2024-SYNTH','SYNTHETIC'),
('KA-019','startup_rate',          1.589238,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-019','patent_rate',           1.207821,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-019','renewable_capacity',  1726.400000,'MW','2024-SYNTH','SYNTHETIC'),
('KA-019','pm25',                  34.100000,'µg/m³','2024-SYNTH','SYNTHETIC'),
('KA-019','forest_cover_pct',     26.646727,'%','2024-SYNTH','SYNTHETIC'),
('KA-019','waste_processing_pct', 75.367329,'%','2024-SYNTH','SYNTHETIC'),
('KA-019','literacy_rate',        74.008420,'%','2024-SYNTH','SYNTHETIC'),

('KA-020','road_density',          0.632697,'km per km²','2024-SYNTH','SYNTHETIC'),
('KA-020','rural_connectivity',   83.857442,'%','2024-SYNTH','SYNTHETIC'),
('KA-020','pt_coverage',          70.968061,'%','2024-SYNTH','SYNTHETIC'),
('KA-020','internet_penetration', 46.648235,'%','2024-SYNTH','SYNTHETIC'),
('KA-020','broadband_per1k',     215.635968,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-020','msme_density',          5.194485,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-020','industrial_emp_rate',   6.200867,'%','2024-SYNTH','SYNTHETIC'),
('KA-020','startup_rate',          2.427628,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-020','patent_rate',           1.149929,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-020','renewable_capacity',  3040.600000,'MW','2024-SYNTH','SYNTHETIC'),
('KA-020','pm25',                  34.300000,'µg/m³','2024-SYNTH','SYNTHETIC'),
('KA-020','forest_cover_pct',     52.258189,'%','2024-SYNTH','SYNTHETIC'),
('KA-020','waste_processing_pct', 35.934664,'%','2024-SYNTH','SYNTHETIC'),
('KA-020','literacy_rate',        66.536820,'%','2024-SYNTH','SYNTHETIC'),

('KA-021','road_density',          0.608399,'km per km²','2024-SYNTH','SYNTHETIC'),
('KA-021','rural_connectivity',   80.106572,'%','2024-SYNTH','SYNTHETIC'),
('KA-021','pt_coverage',          66.355285,'%','2024-SYNTH','SYNTHETIC'),
('KA-021','internet_penetration', 35.403874,'%','2024-SYNTH','SYNTHETIC'),
('KA-021','broadband_per1k',     266.290237,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-021','msme_density',          8.966307,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-021','industrial_emp_rate',   7.512488,'%','2024-SYNTH','SYNTHETIC'),
('KA-021','startup_rate',          0.826007,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-021','patent_rate',           1.514346,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-021','renewable_capacity',  3284.400000,'MW','2024-SYNTH','SYNTHETIC'),
('KA-021','pm25',                  24.000000,'µg/m³','2024-SYNTH','SYNTHETIC'),
('KA-021','forest_cover_pct',     48.915071,'%','2024-SYNTH','SYNTHETIC'),
('KA-021','waste_processing_pct', 61.495845,'%','2024-SYNTH','SYNTHETIC'),
('KA-021','literacy_rate',        89.500446,'%','2024-SYNTH','SYNTHETIC'),

('KA-022','road_density',          0.915451,'km per km²','2024-SYNTH','SYNTHETIC'),
('KA-022','rural_connectivity',   83.980583,'%','2024-SYNTH','SYNTHETIC'),
('KA-022','pt_coverage',          85.276344,'%','2024-SYNTH','SYNTHETIC'),
('KA-022','internet_penetration', 16.158693,'%','2024-SYNTH','SYNTHETIC'),
('KA-022','broadband_per1k',     253.013846,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-022','msme_density',          4.665783,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-022','industrial_emp_rate',   4.736579,'%','2024-SYNTH','SYNTHETIC'),
('KA-022','startup_rate',          2.530685,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-022','patent_rate',           0.932357,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-022','renewable_capacity',  2402.900000,'MW','2024-SYNTH','SYNTHETIC'),
('KA-022','pm25',                  26.800000,'µg/m³','2024-SYNTH','SYNTHETIC'),
('KA-022','forest_cover_pct',     13.277744,'%','2024-SYNTH','SYNTHETIC'),
('KA-022','waste_processing_pct', 36.040609,'%','2024-SYNTH','SYNTHETIC'),
('KA-022','literacy_rate',        67.359256,'%','2024-SYNTH','SYNTHETIC'),

('KA-023','road_density',          0.848293,'km per km²','2024-SYNTH','SYNTHETIC'),
('KA-023','rural_connectivity',   86.083053,'%','2024-SYNTH','SYNTHETIC'),
('KA-023','pt_coverage',          81.823119,'%','2024-SYNTH','SYNTHETIC'),
('KA-023','internet_penetration', 37.413160,'%','2024-SYNTH','SYNTHETIC'),
('KA-023','broadband_per1k',     212.489757,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-023','msme_density',         13.038617,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-023','industrial_emp_rate',  17.281145,'%','2024-SYNTH','SYNTHETIC'),
('KA-023','startup_rate',          1.588139,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-023','patent_rate',           0.952883,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-023','renewable_capacity',  1200.500000,'MW','2024-SYNTH','SYNTHETIC'),
('KA-023','pm25',                  31.000000,'µg/m³','2024-SYNTH','SYNTHETIC'),
('KA-023','forest_cover_pct',     41.499477,'%','2024-SYNTH','SYNTHETIC'),
('KA-023','waste_processing_pct', 60.196560,'%','2024-SYNTH','SYNTHETIC'),
('KA-023','literacy_rate',        84.701413,'%','2024-SYNTH','SYNTHETIC'),

('KA-024','road_density',          0.773085,'km per km²','2024-SYNTH','SYNTHETIC'),
('KA-024','rural_connectivity',   89.586524,'%','2024-SYNTH','SYNTHETIC'),
('KA-024','pt_coverage',          56.216971,'%','2024-SYNTH','SYNTHETIC'),
('KA-024','internet_penetration', 47.672062,'%','2024-SYNTH','SYNTHETIC'),
('KA-024','broadband_per1k',     141.378088,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-024','msme_density',          5.690709,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-024','industrial_emp_rate',   6.254227,'%','2024-SYNTH','SYNTHETIC'),
('KA-024','startup_rate',          2.661342,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-024','patent_rate',           1.064537,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-024','renewable_capacity',  3540.400000,'MW','2024-SYNTH','SYNTHETIC'),
('KA-024','pm25',                  38.900000,'µg/m³','2024-SYNTH','SYNTHETIC'),
('KA-024','forest_cover_pct',     35.195879,'%','2024-SYNTH','SYNTHETIC'),
('KA-024','waste_processing_pct', 58.620690,'%','2024-SYNTH','SYNTHETIC'),
('KA-024','literacy_rate',        83.610072,'%','2024-SYNTH','SYNTHETIC'),

('KA-025','road_density',          0.685823,'km per km²','2024-SYNTH','SYNTHETIC'),
('KA-025','rural_connectivity',   89.550950,'%','2024-SYNTH','SYNTHETIC'),
('KA-025','pt_coverage',          92.482727,'%','2024-SYNTH','SYNTHETIC'),
('KA-025','internet_penetration', 20.002507,'%','2024-SYNTH','SYNTHETIC'),
('KA-025','broadband_per1k',     165.501816,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-025','msme_density',          7.200622,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-025','industrial_emp_rate',  10.865438,'%','2024-SYNTH','SYNTHETIC'),
('KA-025','startup_rate',          1.344403,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-025','patent_rate',           1.299589,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-025','renewable_capacity',   762.200000,'MW','2024-SYNTH','SYNTHETIC'),
('KA-025','pm25',                  38.000000,'µg/m³','2024-SYNTH','SYNTHETIC'),
('KA-025','forest_cover_pct',     12.416806,'%','2024-SYNTH','SYNTHETIC'),
('KA-025','waste_processing_pct', 39.457460,'%','2024-SYNTH','SYNTHETIC'),
('KA-025','literacy_rate',        87.676493,'%','2024-SYNTH','SYNTHETIC'),

('KA-026','road_density',          0.862058,'km per km²','2024-SYNTH','SYNTHETIC'),
('KA-026','rural_connectivity',   86.956522,'%','2024-SYNTH','SYNTHETIC'),
('KA-026','pt_coverage',          92.466513,'%','2024-SYNTH','SYNTHETIC'),
('KA-026','internet_penetration', 30.080012,'%','2024-SYNTH','SYNTHETIC'),
('KA-026','broadband_per1k',     164.707571,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-026','msme_density',          5.736672,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-026','industrial_emp_rate',   7.589386,'%','2024-SYNTH','SYNTHETIC'),
('KA-026','startup_rate',          0.737488,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-026','patent_rate',           1.032483,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-026','renewable_capacity',  1745.800000,'MW','2024-SYNTH','SYNTHETIC'),
('KA-026','pm25',                  47.500000,'µg/m³','2024-SYNTH','SYNTHETIC'),
('KA-026','forest_cover_pct',     45.045532,'%','2024-SYNTH','SYNTHETIC'),
('KA-026','waste_processing_pct', 33.607306,'%','2024-SYNTH','SYNTHETIC'),
('KA-026','literacy_rate',        89.503567,'%','2024-SYNTH','SYNTHETIC'),

('KA-027','road_density',          0.571012,'km per km²','2024-SYNTH','SYNTHETIC'),
('KA-027','rural_connectivity',   82.384824,'%','2024-SYNTH','SYNTHETIC'),
('KA-027','pt_coverage',          76.743965,'%','2024-SYNTH','SYNTHETIC'),
('KA-027','internet_penetration', 24.927249,'%','2024-SYNTH','SYNTHETIC'),
('KA-027','broadband_per1k',     139.298968,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-027','msme_density',          6.946384,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-027','industrial_emp_rate',   5.973114,'%','2024-SYNTH','SYNTHETIC'),
('KA-027','startup_rate',          0.711720,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-027','patent_rate',           1.957229,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-027','renewable_capacity',  2312.800000,'MW','2024-SYNTH','SYNTHETIC'),
('KA-027','pm25',                  48.000000,'µg/m³','2024-SYNTH','SYNTHETIC'),
('KA-027','forest_cover_pct',     32.877314,'%','2024-SYNTH','SYNTHETIC'),
('KA-027','waste_processing_pct', 44.223602,'%','2024-SYNTH','SYNTHETIC'),
('KA-027','literacy_rate',        68.247993,'%','2024-SYNTH','SYNTHETIC'),

('KA-028','road_density',          0.515224,'km per km²','2024-SYNTH','SYNTHETIC'),
('KA-028','rural_connectivity',   80.835735,'%','2024-SYNTH','SYNTHETIC'),
('KA-028','pt_coverage',          80.975354,'%','2024-SYNTH','SYNTHETIC'),
('KA-028','internet_penetration', 20.378034,'%','2024-SYNTH','SYNTHETIC'),
('KA-028','broadband_per1k',     286.440226,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-028','msme_density',         10.443472,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-028','industrial_emp_rate',  12.104778,'%','2024-SYNTH','SYNTHETIC'),
('KA-028','startup_rate',          1.798789,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-028','patent_rate',           1.399058,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-028','renewable_capacity',  2645.900000,'MW','2024-SYNTH','SYNTHETIC'),
('KA-028','pm25',                  42.400000,'µg/m³','2024-SYNTH','SYNTHETIC'),
('KA-028','forest_cover_pct',     13.595757,'%','2024-SYNTH','SYNTHETIC'),
('KA-028','waste_processing_pct', 66.869301,'%','2024-SYNTH','SYNTHETIC'),
('KA-028','literacy_rate',        65.309781,'%','2024-SYNTH','SYNTHETIC'),

('KA-029','road_density',          0.921486,'km per km²','2024-SYNTH','SYNTHETIC'),
('KA-029','rural_connectivity',   86.264657,'%','2024-SYNTH','SYNTHETIC'),
('KA-029','pt_coverage',          68.117136,'%','2024-SYNTH','SYNTHETIC'),
('KA-029','internet_penetration', 48.632787,'%','2024-SYNTH','SYNTHETIC'),
('KA-029','broadband_per1k',     252.936854,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-029','msme_density',          8.909764,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-029','industrial_emp_rate',   9.839443,'%','2024-SYNTH','SYNTHETIC'),
('KA-029','startup_rate',          2.847344,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-029','patent_rate',           1.878036,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-029','renewable_capacity',  1987.200000,'MW','2024-SYNTH','SYNTHETIC'),
('KA-029','pm25',                  18.000000,'µg/m³','2024-SYNTH','SYNTHETIC'),
('KA-029','forest_cover_pct',     53.169628,'%','2024-SYNTH','SYNTHETIC'),
('KA-029','waste_processing_pct', 41.151685,'%','2024-SYNTH','SYNTHETIC'),
('KA-029','literacy_rate',        67.244841,'%','2024-SYNTH','SYNTHETIC'),

('KA-030','road_density',          1.012742,'km per km²','2024-SYNTH','SYNTHETIC'),
('KA-030','rural_connectivity',   90.937020,'%','2024-SYNTH','SYNTHETIC'),
('KA-030','pt_coverage',          89.825729,'%','2024-SYNTH','SYNTHETIC'),
('KA-030','internet_penetration', 16.615871,'%','2024-SYNTH','SYNTHETIC'),
('KA-030','broadband_per1k',     294.711564,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-030','msme_density',         11.524691,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-030','industrial_emp_rate',  13.483406,'%','2024-SYNTH','SYNTHETIC'),
('KA-030','startup_rate',          0.837410,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-030','patent_rate',           0.644161,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-030','renewable_capacity',  1334.600000,'MW','2024-SYNTH','SYNTHETIC'),
('KA-030','pm25',                  44.800000,'µg/m³','2024-SYNTH','SYNTHETIC'),
('KA-030','forest_cover_pct',     36.771444,'%','2024-SYNTH','SYNTHETIC'),
('KA-030','waste_processing_pct', 68.636912,'%','2024-SYNTH','SYNTHETIC'),
('KA-030','literacy_rate',        81.911525,'%','2024-SYNTH','SYNTHETIC'),

('KA-031','road_density',          1.599735,'km per km²','2024-SYNTH','SYNTHETIC'),
('KA-031','rural_connectivity',   82.507740,'%','2024-SYNTH','SYNTHETIC'),
('KA-031','pt_coverage',          84.844053,'%','2024-SYNTH','SYNTHETIC'),
('KA-031','internet_penetration', 54.649581,'%','2024-SYNTH','SYNTHETIC'),
('KA-031','broadband_per1k',     160.088383,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-031','msme_density',          9.005324,'per 1,000','2024-SYNTH','SYNTHETIC'),
('KA-031','industrial_emp_rate',   8.947470,'%','2024-SYNTH','SYNTHETIC'),
('KA-031','startup_rate',          2.123897,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-031','patent_rate',           0.952092,'per 100,000','2024-SYNTH','SYNTHETIC'),
('KA-031','renewable_capacity',  2274.300000,'MW','2024-SYNTH','SYNTHETIC'),
('KA-031','pm25',                  32.700000,'µg/m³','2024-SYNTH','SYNTHETIC'),
('KA-031','forest_cover_pct',      3.617691,'%','2024-SYNTH','SYNTHETIC'),
('KA-031','waste_processing_pct', 83.422939,'%','2024-SYNTH','SYNTHETIC'),
('KA-031','literacy_rate',        83.560292,'%','2024-SYNTH','SYNTHETIC');

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 3 : STAGE 11 – NORMALISATION CONFIG AND COMPUTED 0–100 SCORES
-- ─────────────────────────────────────────────────────────────────────────────
-- Min/max computed from the 31 synthetic observations above.
-- Positive:  score = (X – min) / (max – min) × 100
-- Negative:  score = (max – X) / (max – min) × 100

INSERT OR IGNORE INTO normalization_config VALUES
-- code                    direction   observed_min  observed_max   method
('road_density',           'positive', 0.507081,     1.599735,      'min-max'),
('rural_connectivity',     'positive', 80.106572,    98.679868,     'min-max'),
('pt_coverage',            'positive', 56.216971,    93.527129,     'min-max'),
('internet_penetration',   'positive', 15.476590,    54.649581,     'min-max'),
('broadband_per1k',        'positive', 50.971030,    294.711564,    'min-max'),
('msme_density',           'positive', 4.571301,     13.038617,     'min-max'),
('industrial_emp_rate',    'positive', 4.736579,     17.281145,     'min-max'),
('startup_rate',           'positive', 0.711720,     108.345455,    'min-max'),
('patent_rate',            'positive', 0.392685,     18.445455,     'min-max'),
('renewable_capacity',     'positive', 597.000000,   4128.400000,   'min-max'),
('pm25',                   'negative', 18.000000,    48.000000,     'min-max'),
('forest_cover_pct',       'positive', 3.617691,     55.081818,     'min-max'),
('waste_processing_pct',   'positive', 33.607306,    83.422939,     'min-max'),
('literacy_rate',          'positive', 65.309781,    89.503567,     'min-max');

-- Compute and store normalized scores for all 31 districts × 14 indicators
INSERT OR IGNORE INTO normalized_indicators (district_id, indicator_code, normalized_score)
SELECT
    p.district_id,
    p.indicator_code,
    CASE nc.direction
        WHEN 'positive' THEN
            ROUND(((p.processed_value - nc.observed_min)
                   / (nc.observed_max - nc.observed_min)) * 100.0, 4)
        WHEN 'negative' THEN
            ROUND(((nc.observed_max - p.processed_value)
                   / (nc.observed_max - nc.observed_min)) * 100.0, 4)
    END AS normalized_score
FROM processed_indicators p
JOIN normalization_config nc ON nc.indicator_code = p.indicator_code;

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 4 : STAGE 12 – WEIGHTS AND COMPOSITE SCORING
-- ─────────────────────────────────────────────────────────────────────────────
-- METHODOLOGY NOTE
-- Weights reflect equal weighting within each dimension and across dimensions,
-- except that Infrastructure carries slightly more weight (20%) as the
-- foundational enabler of all other development dimensions.
-- The 70% weight-coverage threshold means a district's score is marked invalid
-- if the weighted sum of available indicators covers < 70% of the total weight.

-- 4.1  Indicator weights (within each dimension, weights sum to 1.0)
INSERT OR IGNORE INTO indicator_weights VALUES
('road_density',           0.333, 'Equal weight within Infrastructure; road density is the most direct infrastructure proxy'),
('rural_connectivity',     0.333, 'Equal weight within Infrastructure; rural connectivity captures last-mile access'),
('pt_coverage',            0.334, 'Equal weight within Infrastructure; public transport indicates collective mobility'),
('internet_penetration',   0.500, 'Equal weight within Digital Access; household penetration is the demand-side measure'),
('broadband_per1k',        0.500, 'Equal weight within Digital Access; broadband per 1000 is the supply-side measure'),
('msme_density',           0.500, 'Equal weight within Industry; enterprise density reflects economic activity'),
('industrial_emp_rate',    0.500, 'Equal weight within Industry; employment rate reflects productive engagement'),
('startup_rate',           0.500, 'Equal weight within Innovation; startups proxy new venture creation'),
('patent_rate',            0.500, 'Equal weight within Innovation; patents proxy knowledge production'),
('renewable_capacity',     0.300, 'Higher weight within Energy-Env; renewable capacity is the primary policy output'),
('pm25',                   0.300, 'Higher weight within Energy-Env; air quality directly affects health outcomes'),
('forest_cover_pct',       0.200, 'Moderate weight within Energy-Env; complements air quality and biodiversity'),
('waste_processing_pct',   0.200, 'Moderate weight within Energy-Env; reflects solid waste management capacity'),
('literacy_rate',          1.000, 'Only indicator in Human Capital dimension; full weight assigned');

-- 4.2  Dimension weights (sum = 1.0)
INSERT OR IGNORE INTO dimension_weights VALUES
('Infrastructure',       0.20, '20pct - foundational enabler; underpins all other dimensions'),
('Digital Access',       0.15, '15pct - cross-cutting; enables service access and economic activity'),
('Industry',             0.20, '20pct - economic engine; enterprise activity and employment'),
('Innovation',           0.10, '10pct - emerging; important but limited observation coverage'),
('Energy & Environment', 0.20, '20pct - essential; affects health, sustainability and climate'),
('Human Capital',        0.15, '15pct - long-run driver; literacy as the available proxy');

-- 4.3  Compute dimension scores
-- Weight-coverage threshold = 0.70 (70%).  Districts below threshold get is_valid = 0.
INSERT OR IGNORE INTO district_scores (district_id, score_type, dimension, score, weight_coverage, is_valid)
SELECT
    n.district_id,
    'dimension'                                   AS score_type,
    im.dimension,
    ROUND(SUM(iw.weight * n.normalized_score)
          / SUM(iw.weight), 4)                   AS score,
    1.0                                           AS weight_coverage,  -- all data present (synthetic)
    1                                             AS is_valid
FROM normalized_indicators n
JOIN indicator_master  im ON im.indicator_code = n.indicator_code
JOIN indicator_weights iw ON iw.indicator_code = n.indicator_code
GROUP BY n.district_id, im.dimension;

-- 4.4  Compute overall district development scores
INSERT OR IGNORE INTO district_scores (district_id, score_type, dimension, score, weight_coverage, is_valid)
SELECT
    ds.district_id,
    'overall'                                     AS score_type,
    'Overall'                                     AS dimension,
    ROUND(SUM(dw.weight * ds.score)
          / SUM(dw.weight), 4)                   AS score,
    1.0                                           AS weight_coverage,
    1                                             AS is_valid
FROM district_scores ds
JOIN dimension_weights dw ON dw.dimension = ds.dimension
WHERE ds.score_type = 'dimension'
  AND ds.is_valid = 1
GROUP BY ds.district_id;

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 5 : STAGE 13 – RANKINGS AND COMPARISON VIEWS
-- ─────────────────────────────────────────────────────────────────────────────

-- 5.1  Overall district rankings
CREATE VIEW IF NOT EXISTS district_rankings AS
SELECT
    d.district_name,
    s.score                                                       AS overall_score,
    RANK() OVER (ORDER BY s.score DESC)                           AS district_rank,
    s.weight_coverage,
    s.is_valid
FROM district_scores s
JOIN district_master d ON d.district_id = s.district_id
WHERE s.score_type = 'overall'
ORDER BY district_rank;

-- 5.2  Per-dimension rankings
CREATE VIEW IF NOT EXISTS dimension_rankings AS
SELECT
    d.district_name,
    s.dimension,
    ROUND(s.score, 2)                                             AS dimension_score,
    RANK() OVER (PARTITION BY s.dimension ORDER BY s.score DESC) AS dim_rank
FROM district_scores s
JOIN district_master d ON d.district_id = s.district_id
WHERE s.score_type = 'dimension'
  AND s.is_valid   = 1
ORDER BY s.dimension, dim_rank;

-- 5.3  Strongest and weakest districts per dimension
CREATE VIEW IF NOT EXISTS dimension_extremes AS
SELECT dimension, 'Best'  AS position, district_name, dimension_score, dim_rank
FROM dimension_rankings WHERE dim_rank = 1
UNION ALL
SELECT dimension, 'Worst' AS position, district_name, dimension_score, dim_rank
FROM dimension_rankings
WHERE dim_rank = (
    SELECT MAX(dim_rank) FROM dimension_rankings dr2
    WHERE dr2.dimension = dimension_rankings.dimension
)
ORDER BY dimension, position;

-- 5.4  Uneven development: districts with high inter-dimension score variance
CREATE VIEW IF NOT EXISTS development_unevenness AS
SELECT
    d.district_name,
    ROUND(MAX(s.score) - MIN(s.score), 2)         AS score_range,
    ROUND(AVG(s.score), 2)                        AS avg_dim_score,
    COUNT(DISTINCT s.dimension)                   AS dimensions_covered
FROM district_scores s
JOIN district_master d ON d.district_id = s.district_id
WHERE s.score_type = 'dimension' AND s.is_valid = 1
GROUP BY d.district_name
ORDER BY score_range DESC;

-- 5.5  Dimension scorecard pivot (wide format for heatmap)
CREATE VIEW IF NOT EXISTS dimension_scorecard AS
SELECT
    d.district_name,
    ROUND(MAX(CASE WHEN s.dimension = 'Infrastructure'       THEN s.score END), 2) AS infrastructure_score,
    ROUND(MAX(CASE WHEN s.dimension = 'Digital Access'       THEN s.score END), 2) AS digital_access_score,
    ROUND(MAX(CASE WHEN s.dimension = 'Industry'             THEN s.score END), 2) AS industry_score,
    ROUND(MAX(CASE WHEN s.dimension = 'Innovation'           THEN s.score END), 2) AS innovation_score,
    ROUND(MAX(CASE WHEN s.dimension = 'Energy & Environment' THEN s.score END), 2) AS energy_env_score,
    ROUND(MAX(CASE WHEN s.dimension = 'Human Capital'        THEN s.score END), 2) AS human_capital_score,
    ROUND(MAX(CASE WHEN s.score_type = 'overall'             THEN s.score END), 2) AS overall_score
FROM district_scores s
JOIN district_master d ON d.district_id = s.district_id
GROUP BY d.district_name
ORDER BY overall_score DESC;

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 6 : STAGE 14 – EDA VIEWS
-- ─────────────────────────────────────────────────────────────────────────────

-- 6.1  Descriptive statistics for each indicator (mean, median proxy, min, max, std)
CREATE VIEW IF NOT EXISTS indicator_descriptive_stats AS
SELECT
    im.indicator_name,
    im.dimension,
    im.direction,
    COUNT(p.processed_value)                                AS n,
    ROUND(AVG(p.processed_value), 4)                       AS mean_value,
    ROUND(MIN(p.processed_value), 4)                       AS min_value,
    ROUND(MAX(p.processed_value), 4)                       AS max_value,
    ROUND(MAX(p.processed_value) - MIN(p.processed_value), 4) AS range_value,
    -- Approximate CV: std / mean, expressed as %
    ROUND(
        100.0 * SQRT(
            (SUM(p.processed_value * p.processed_value) -
             COUNT(p.processed_value) * AVG(p.processed_value) * AVG(p.processed_value))
            / (COUNT(p.processed_value) - 1)
        ) / NULLIF(AVG(p.processed_value), 0),
    2)                                                     AS cv_pct
FROM processed_indicators p
JOIN indicator_master im ON im.indicator_code = p.indicator_code
GROUP BY p.indicator_code
ORDER BY im.dimension, im.indicator_name;

-- 6.2  Normalised indicator descriptive statistics
CREATE VIEW IF NOT EXISTS normalised_indicator_stats AS
SELECT
    im.indicator_name,
    im.dimension,
    COUNT(n.normalized_score)                              AS n,
    ROUND(AVG(n.normalized_score), 2)                     AS mean_score,
    ROUND(MIN(n.normalized_score), 2)                     AS min_score,
    ROUND(MAX(n.normalized_score), 2)                     AS max_score
FROM normalized_indicators n
JOIN indicator_master im ON im.indicator_code = n.indicator_code
GROUP BY n.indicator_code
ORDER BY im.dimension, mean_score DESC;

-- 6.3  Missing data analysis
CREATE VIEW IF NOT EXISTS indicator_missingness AS
SELECT
    im.indicator_name,
    im.dimension,
    31                                                      AS total_districts,
    COUNT(p.processed_value)                               AS districts_with_data,
    31 - COUNT(p.processed_value)                          AS districts_missing,
    ROUND(100.0 * COUNT(p.processed_value) / 31.0, 1)     AS completeness_pct
FROM indicator_master im
LEFT JOIN processed_indicators p ON p.indicator_code = im.indicator_code
GROUP BY im.indicator_code
ORDER BY completeness_pct ASC;

-- 6.4  Outlier detection: districts ±2 standard deviations from the mean (per indicator)
CREATE VIEW IF NOT EXISTS indicator_outliers AS
SELECT
    d.district_name,
    im.indicator_name,
    im.dimension,
    ROUND(p.processed_value, 4)    AS observed_value,
    ROUND(stats.mean_v, 4)         AS indicator_mean,
    ROUND(stats.std_v, 4)          AS indicator_std,
    ROUND((p.processed_value - stats.mean_v) / NULLIF(stats.std_v, 0), 2) AS z_score,
    CASE
        WHEN ABS((p.processed_value - stats.mean_v) / NULLIF(stats.std_v, 0)) > 2
        THEN 'OUTLIER'
        ELSE 'normal'
    END                            AS flag
FROM processed_indicators p
JOIN district_master d ON d.district_id = p.district_id
JOIN indicator_master im ON im.indicator_code = p.indicator_code
JOIN (
    SELECT
        indicator_code,
        AVG(processed_value) AS mean_v,
        SQRT(
            (SUM(processed_value * processed_value) -
             COUNT(processed_value) * AVG(processed_value) * AVG(processed_value))
            / (COUNT(processed_value) - 1)
        ) AS std_v
    FROM processed_indicators
    GROUP BY indicator_code
) stats ON stats.indicator_code = p.indicator_code
WHERE ABS((p.processed_value - stats.mean_v) / NULLIF(stats.std_v, 0)) > 2
ORDER BY ABS((p.processed_value - stats.mean_v) / NULLIF(stats.std_v, 0)) DESC;

-- 6.5  Cross-dimension correlation proxy:
--      Ranks districts by digital_access vs industry and flags divergence
CREATE VIEW IF NOT EXISTS digital_vs_industry AS
SELECT
    d.district_name,
    ROUND(da.score, 2)             AS digital_access_score,
    RANK() OVER (ORDER BY da.score DESC)  AS da_rank,
    ROUND(ind.score, 2)            AS industry_score,
    RANK() OVER (ORDER BY ind.score DESC) AS ind_rank,
    ABS(
        RANK() OVER (ORDER BY da.score DESC) -
        RANK() OVER (ORDER BY ind.score DESC)
    )                              AS rank_divergence
FROM district_master d
JOIN district_scores da  ON da.district_id  = d.district_id AND da.dimension  = 'Digital Access' AND da.score_type = 'dimension'
JOIN district_scores ind ON ind.district_id = d.district_id AND ind.dimension = 'Industry'        AND ind.score_type = 'dimension'
ORDER BY rank_divergence DESC;

-- 6.6  Good infrastructure but weak human capital
CREATE VIEW IF NOT EXISTS infra_strong_humancap_weak AS
SELECT
    d.district_name,
    ROUND(inf.score, 2)            AS infrastructure_score,
    ROUND(hc.score,  2)            AS human_capital_score,
    ROUND(inf.score - hc.score, 2) AS gap
FROM district_master d
JOIN district_scores inf ON inf.district_id = d.district_id AND inf.dimension = 'Infrastructure'  AND inf.score_type = 'dimension'
JOIN district_scores hc  ON hc.district_id  = d.district_id AND hc.dimension  = 'Human Capital'   AND hc.score_type = 'dimension'
WHERE inf.score > hc.score
ORDER BY gap DESC;

-- 6.7  Largest regional disparities per indicator (max – min range of normalized scores)
CREATE VIEW IF NOT EXISTS indicator_regional_disparity AS
SELECT
    im.indicator_name,
    im.dimension,
    ROUND(MAX(n.normalized_score) - MIN(n.normalized_score), 2) AS disparity_range,
    ROUND(MAX(n.normalized_score), 2)                           AS max_score,
    ROUND(MIN(n.normalized_score), 2)                           AS min_score
FROM normalized_indicators n
JOIN indicator_master im ON im.indicator_code = n.indicator_code
GROUP BY n.indicator_code
ORDER BY disparity_range DESC;

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 7 : STAGE 15 – ML RESULT STORAGE (populated via Python / scikit-learn)
-- ─────────────────────────────────────────────────────────────────────────────
-- The tables analysis_runs, district_clusters and model_explanations were
-- created in Section 0.  Below are the insertion patterns used by the Python
-- pipeline after clustering / PCA / Random Forest is complete.

-- Example: register a K-Means run
-- INSERT INTO analysis_runs (run_name, algorithm, parameters, notes) VALUES
--   ('kmeans_k3_v1','K-Means','{"n_clusters":3,"init":"k-means++","random_state":42}',
--    'Baseline 3-cluster solution; all 14 normalised indicators; run 2024-11-12');

-- Example: insert cluster assignments (replace with actual Python output)
-- INSERT INTO district_clusters (run_id, district_id, cluster_label, cluster_name, distance_to_centroid)
-- VALUES (1,'KA-001',2,'Moderate development',3.14);

-- Example: insert SHAP feature contributions
-- INSERT INTO model_explanations (run_id, district_id, indicator_code, shap_value, feature_importance)
-- VALUES (1,'KA-005','startup_rate', 8.21, 0.19);

-- Convenience view: cluster summary
CREATE VIEW IF NOT EXISTS cluster_summary AS
SELECT
    ar.run_name,
    ar.algorithm,
    dc.cluster_label,
    dc.cluster_name,
    COUNT(dc.district_id)              AS district_count,
    ROUND(AVG(dc.distance_to_centroid),3) AS avg_centroid_dist,
    GROUP_CONCAT(d.district_name, ', ') AS districts
FROM district_clusters dc
JOIN analysis_runs ar ON ar.run_id      = dc.run_id
JOIN district_master d ON d.district_id = dc.district_id
GROUP BY ar.run_id, dc.cluster_label
ORDER BY ar.run_id, dc.cluster_label;

-- Feature-importance summary across all explanations for a given run
CREATE VIEW IF NOT EXISTS feature_importance_summary AS
SELECT
    ar.run_name,
    im.indicator_name,
    im.dimension,
    ROUND(AVG(me.shap_value), 4)        AS avg_shap,
    ROUND(AVG(me.feature_importance), 4) AS avg_importance
FROM model_explanations me
JOIN analysis_runs ar  ON ar.run_id = me.run_id
JOIN indicator_master im ON im.indicator_code = me.indicator_code
GROUP BY ar.run_id, me.indicator_code
ORDER BY ar.run_id, avg_importance DESC;

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 8 : VERIFICATION QUERIES
-- Run these after executing the script to sanity-check all five stages.
-- ─────────────────────────────────────────────────────────────────────────────

-- 8.1  Count check: should return 31 districts, 14 indicators, 434 observations
SELECT
    (SELECT COUNT(*) FROM district_master)                   AS districts,
    (SELECT COUNT(*) FROM indicator_master)                  AS indicators,
    (SELECT COUNT(*) FROM processed_indicators)              AS processed_obs,
    (SELECT COUNT(*) FROM normalized_indicators)             AS normalised_obs,
    (SELECT COUNT(*) FROM district_scores WHERE score_type='dimension') AS dim_scores,
    (SELECT COUNT(*) FROM district_scores WHERE score_type='overall')   AS overall_scores;

-- 8.2  Stage 11 – Sample normalised scores (should be in [0, 100])
SELECT d.district_name, ni.indicator_code, ROUND(ni.normalized_score,2) AS score
FROM normalized_indicators ni
JOIN district_master d ON d.district_id = ni.district_id
ORDER BY d.district_name, ni.indicator_code
LIMIT 20;

-- 8.3  Stage 12 – Dimension scores sample
SELECT d.district_name, s.dimension, ROUND(s.score,2) AS dim_score
FROM district_scores s
JOIN district_master d ON d.district_id = s.district_id
WHERE s.score_type = 'dimension'
ORDER BY d.district_name, s.dimension;

-- 8.4  Stage 13 – Overall rankings
SELECT * FROM district_rankings ORDER BY district_rank;

-- 8.5  Stage 14 – Descriptive statistics
SELECT * FROM indicator_descriptive_stats;

-- 8.6  Stage 14 – Indicators with highest regional disparity
SELECT * FROM indicator_regional_disparity LIMIT 10;

-- 8.7  Stage 14 – Outlier districts
SELECT * FROM indicator_outliers ORDER BY ABS(z_score) DESC LIMIT 15;

-- 8.8  Dimension scorecard (heatmap data)
SELECT * FROM dimension_scorecard;

-- 8.9  Digital Access vs Industry divergence
SELECT * FROM digital_vs_industry LIMIT 10;

-- 8.10  Strongest/weakest districts per dimension
SELECT * FROM dimension_extremes;

-- 8.11  Infrastructure strong, Human Capital weak
SELECT * FROM infra_strong_humancap_weak LIMIT 10;

-- 8.12  Development unevenness (candidates for further investigation)
SELECT * FROM development_unevenness LIMIT 10;

-- =============================================================================
-- HOW TO REGENERATE InfraSense_Project_Log.md AFTER ANY CHANGE
-- =============================================================================
-- Run the Python script below from the project folder (5TH SEM/el/).
-- It reads InfraSense_Production.db and rewrites InfraSense_Project_Log.md
-- with the latest rankings, scores, EDA stats and changelog entry.
--
-- python generate_log.py
--
-- The script (generate_log.py) lives in the same folder.
-- Always run it after:
--   • Adding or updating processed_indicators rows (new/real data)
--   • Re-running normalisation (Section 3)
--   • Re-running scoring (Section 4)
--   • Running the ML pipeline and inserting cluster results (Section 7)
--   • Any schema change
-- =============================================================================
-- END OF InfraSense_Stages_11_to_15_SQLite.sql
-- =============================================================================
