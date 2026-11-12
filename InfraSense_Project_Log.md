# InfraSense – Karnataka District Development Analysis
## Project Log & Process Record

> **WARNING:** All numeric values are **SYNTHETIC** (pseudo-random placeholders generated
> on 12 Nov 2026). They are not government data. Replace with real observations before
> drawing any real-world conclusions.

---

## Project Overview

| Item | Detail |
|------|--------|
| Project Name | InfraSense – Karnataka District Development Analysis |
| Scope | 31 Karnataka districts · 14 indicators · 6 development dimensions |
| Data status | SYNTHETIC (pseudo-random, internally consistent) |
| Database file | `InfraSense_Production.db` (SQLite 3) |
| SQL schema file | `InfraSense_Stages_11_to_15_SQLite.sql` |
| Dataset file | `InfraSense_Karnataka_Master_Dataset_SYNTHETIC.xlsx` |
| Folder | `5TH SEM/el/` on Desktop |

---

## Changelog

### Session 1 — 12 Nov 2026, 14:57 IST

**What was done:**
- Synthetic Excel dataset generated (`InfraSense_Karnataka_Master_Dataset_SYNTHETIC.xlsx`).
- Workbook contains 13 sheets: README, District_Master, 6 dimension sheets,
  All_Indicators_Wide, All_Indicators_Long, Source_Registry, Missing_Data, District_Mapping.
- 31 districts populated with pseudo-random but internally consistent values
  (connected ≤ total habitations; wet + dry = total waste; literate ≤ population 7+).
- 14 calculated (CALC:) indicator columns derived from raw fields.

### Session 2 — 12 Nov 2026, 15:19 IST

**What was done:**
- **Stage 11** — Normalisation config built from observed min/max across 31 districts.
  All 14 indicators converted to 0–100. PM2.5 treated as negative (lower = better).
- **Stage 12** — Indicator weights (within-dimension) and dimension weights documented
  and inserted. Composite dimension and overall district scores computed.
- **Stage 13** — Five ranking/comparison views created:
  `district_rankings`, `dimension_rankings`, `dimension_extremes`,
  `development_unevenness`, `dimension_scorecard`.
- **Stage 14** — Seven EDA views created: descriptive stats, missingness, outlier detection,
  regional disparity, digital-vs-industry cross-dimension, infra-vs-humancap, scorecard.
- **Stage 15** — ML result tables (`analysis_runs`, `district_clusters`,
  `model_explanations`) and two summary views created. Ready for Python pipeline.
- Full SQL file written and tested; `InfraSense_Production.db` created and verified.

**Files created this session:**
- `InfraSense_Stages_11_to_15_SQLite.sql`
- `InfraSense_Production.db`
- `InfraSense_Project_Log.md` ← this file

---

## Database Schema Summary

| Table | Purpose | Records |
|-------|---------|---------|
| `district_master` | 31 Karnataka districts | 31 |
| `indicator_master` | 14 indicator definitions | 14 |
| `data_sources` | Source metadata | 0 (populate when real data sourced) |
| `raw_observations` | Original pre-calculated field values | 0 (populate when real data sourced) |
| `processed_indicators` | Calculated CALC: indicator values | 434 |
| `normalization_config` | Min/max and direction per indicator | 14 |
| `normalized_indicators` | 0–100 scores (district × indicator) | 434 |
| `indicator_weights` | Within-dimension indicator weights | 14 |
| `dimension_weights` | Weight of each of the 6 dimensions | 6 |
| `district_scores` | Dimension and overall scores | 217 |
| `analysis_runs` | ML experiment metadata | 0 (populate via Python) |
| `district_clusters` | Cluster assignments from ML runs | 0 (populate via Python) |
| `model_explanations` | SHAP feature contributions | 0 (populate via Python) |

---

## Stage 11 – Normalisation

**Formulae:**
- Positive indicator: `score = (X - X_min) / (X_max - X_min) × 100`
- Negative indicator: `score = (X_max - X) / (X_max - X_min) × 100`

**Only negative indicator:** `pm25` (Annual average PM2.5 µg/m³) — lower is better.

### Observed Min / Max for each Indicator

| Indicator | Dimension | Direction | Min | Max |
|-----------|-----------|-----------|----:|----:|
| Broadband per 1,000 population | Digital Access | positive | 50.9710 | 294.7116 |
| Household internet penetration | Digital Access | positive | 15.4766 | 54.6496 |
| Annual average PM2.5 | Energy & Environment | negative | 18.0000 | 48.0000 |
| Forest cover percentage | Energy & Environment | positive | 3.6177 | 55.0818 |
| Renewable energy capacity | Energy & Environment | positive | 597.0000 | 4128.4000 |
| Waste processing rate | Energy & Environment | positive | 33.6073 | 83.4229 |
| Literacy rate (7+) | Human Capital | positive | 65.3098 | 89.5036 |
| Industrial employment rate | Industry | positive | 4.7366 | 17.2811 |
| MSME density | Industry | positive | 4.5713 | 13.0386 |
| Public transport coverage | Infrastructure | positive | 56.2170 | 93.5271 |
| Road density | Infrastructure | positive | 0.5071 | 1.5997 |
| Rural connectivity | Infrastructure | positive | 80.1066 | 98.6799 |
| Patent applications per 100,000 | Innovation | positive | 0.3927 | 18.4455 |
| Startups per 100,000 | Innovation | positive | 0.7117 | 108.3455 |

---

## Stage 12 – Weight Assignment

### Dimension Weights

| Dimension | Weight | Rationale |
|-----------|:------:|-----------|
| Infrastructure | 0.20 | Foundational enabler; underpins all other dimensions |
| Digital Access | 0.15 | Cross-cutting; enables service access and economic activity |
| Industry | 0.20 | Economic engine; enterprise activity and employment |
| Innovation | 0.10 | Emerging; important but limited coverage with 31 districts |
| Energy & Environment | 0.20 | Affects health, sustainability and climate outcomes |
| Human Capital | 0.15 | Long-run driver; literacy as the available proxy |

### Indicator Weights (within dimension)

| Indicator | Dimension | Weight | Rationale |
|-----------|-----------|:------:|-----------|
| Road density | Infrastructure | 0.333 | Most direct infrastructure proxy |
| Rural connectivity | Infrastructure | 0.333 | Captures last-mile access |
| Public transport coverage | Infrastructure | 0.334 | Collective mobility indicator |
| Household internet penetration | Digital Access | 0.500 | Demand-side measure |
| Broadband per 1,000 | Digital Access | 0.500 | Supply-side measure |
| MSME density | Industry | 0.500 | Enterprise density reflects economic activity |
| Industrial employment rate | Industry | 0.500 | Productive engagement in MSME sector |
| Startups per 100,000 | Innovation | 0.500 | New venture creation proxy |
| Patent applications per 100,000 | Innovation | 0.500 | Knowledge production proxy |
| Renewable energy capacity | Energy & Env | 0.300 | Primary policy output |
| Annual average PM2.5 | Energy & Env | 0.300 | Direct health impact (negative indicator) |
| Forest cover % | Energy & Env | 0.200 | Biodiversity and carbon sink |
| Waste processing % | Energy & Env | 0.200 | Solid waste management capacity |
| Literacy rate (7+) | Human Capital | 1.000 | Sole indicator; full weight |

> **Coverage threshold:** A district score is marked invalid when available indicator
> weights cover < 70% of the dimension total. All 31 districts have 100% data
> coverage in this synthetic run.

---

## Stage 13 – District Rankings

### Full Overall Rankings (all 31 districts)

| Rank | District | Overall Score |
|:----:|----------|:-------------:|
| 1 | Bengaluru Urban | 60.18 |
| 2 | Raichur | 59.70 |
| 3 | Chitradurga | 55.73 |
| 4 | Bengaluru Rural | 55.26 |
| 5 | Kalaburagi | 53.66 |
| 6 | Vijayanagara | 53.54 |
| 7 | Yadgir | 53.54 |
| 8 | Hassan | 52.75 |
| 9 | Mandya | 50.72 |
| 10 | Haveri | 49.27 |
| 11 | Bidar | 48.25 |
| 12 | Chikkaballapura | 45.05 |
| 13 | Chamarajanagar | 44.85 |
| 14 | Vijayapura | 43.15 |
| 15 | Gadag | 41.94 |
| 16 | Tumakuru | 41.51 |
| 17 | Shivamogga | 40.93 |
| 18 | Belagavi | 40.75 |
| 19 | Davanagere | 40.54 |
| 20 | Ramanagara | 39.41 |
| 21 | Kolar | 39.37 |
| 22 | Dharwad | 38.12 |
| 23 | Ballari | 36.66 |
| 24 | Dakshina Kannada | 34.99 |
| 25 | Uttara Kannada | 34.11 |
| 26 | Bagalkote | 33.30 |
| 27 | Kodagu | 32.90 |
| 28 | Koppal | 29.60 |
| 29 | Chikkamagaluru | 29.58 |
| 30 | Mysuru | 25.30 |
| 31 | Udupi | 21.50 |

### Dimension Scorecard

| District | Infra | Digital | Industry | Innovation | E&Env | HumanCap | **Overall** |
|----------|:-----:|:-------:|:--------:|:----------:|:-----:|:--------:|:-----------:|
| Bengaluru Urban | 32.6 | 52.3 | 57.6 | 100.0 | 53.9 | 90.1 | **60.18** |
| Raichur | 44.0 | 61.1 | 100.0 | 2.0 | 47.5 | 80.2 | **59.70** |
| Chitradurga | 62.8 | 35.5 | 72.8 | 1.9 | 48.8 | 89.0 | **55.73** |
| Bengaluru Rural | 43.2 | 60.3 | 93.8 | 2.9 | 61.5 | 41.4 | **55.26** |
| Kalaburagi | 41.1 | 77.5 | 74.5 | 2.1 | 58.9 | 46.2 | **53.66** |
| Yadgir | 64.9 | 51.5 | 75.9 | 0.8 | 36.4 | 68.6 | **53.54** |
| Vijayanagara | 63.2 | 72.4 | 43.0 | 2.2 | 49.5 | 75.4 | **53.54** |
| Hassan | 73.8 | 79.8 | 87.6 | 4.8 | 39.4 | 1.0 | **52.75** |
| Mandya | 12.2 | 69.6 | 37.0 | 3.2 | 75.6 | 100.0 | **50.72** |
| Haveri | 79.1 | 49.6 | 71.8 | 0.9 | 42.3 | 20.6 | **49.27** |
| Bidar | 73.3 | 42.8 | 84.2 | 4.2 | 40.3 | 12.3 | **48.25** |
| Chikkaballapura | 54.7 | 75.4 | 35.5 | 3.7 | 53.1 | 31.3 | **45.05** |
| Chamarajanagar | 58.1 | 52.6 | 56.0 | 1.3 | 62.1 | 10.6 | **44.85** |
| Vijayapura | 34.3 | 83.8 | 46.0 | 5.1 | 64.1 | 8.0 | **43.15** |
| Gadag | 36.5 | 57.9 | 28.0 | 4.0 | 51.8 | 63.9 | **41.94** |
| Tumakuru | 55.5 | 42.0 | 18.2 | 1.8 | 26.4 | 100.0 | **41.51** |
| Shivamogga | 54.9 | 29.3 | 40.0 | 2.8 | 17.2 | 92.5 | **40.93** |
| Belagavi | 68.8 | 10.0 | 27.8 | 0.8 | 63.2 | 48.1 | **40.75** |
| Davanagere | 72.2 | 36.8 | 15.8 | 3.0 | 33.2 | 69.8 | **40.54** |
| Ramanagara | 25.1 | 59.6 | 12.7 | 2.8 | 56.4 | 75.6 | **39.41** |
| Kolar | 46.6 | 54.4 | 32.0 | 2.7 | 49.2 | 36.0 | **39.37** |
| Dharwad | 57.3 | 64.1 | 4.5 | 4.2 | 49.1 | 39.3 | **38.12** |
| Ballari | 73.0 | 31.8 | 44.6 | 1.9 | 40.0 | 1.2 | **36.66** |
| Dakshina Kannada | 64.8 | 24.8 | 34.4 | 0.2 | 47.8 | 12.5 | **34.99** |
| Uttara Kannada | 23.7 | 54.6 | 64.0 | 3.3 | 40.2 | 0.0 | **34.11** |
| Bagalkote | 59.0 | 34.0 | 13.3 | 1.9 | 47.1 | 27.5 | **33.30** |
| Kodagu | 69.4 | 31.4 | 16.7 | 4.8 | 31.6 | 27.9 | **32.90** |
| Koppal | 23.8 | 73.6 | 9.5 | 2.9 | 54.3 | 5.1 | **29.60** |
| Chikkamagaluru | 18.0 | 55.4 | 6.1 | 2.6 | 61.2 | 26.2 | **29.58** |
| Mysuru | 45.4 | 42.3 | 0.6 | 2.3 | 41.3 | 8.5 | **25.30** |
| Udupi | 24.4 | 30.2 | 18.9 | 4.3 | 30.2 | 12.1 | **21.50** |

### Best and Worst District per Dimension

| Dimension | Position | District | Score |
|-----------|:--------:|----------|:-----:|
| Digital Access | Best | Vijayapura | 83.75 |
| Digital Access | Worst | Belagavi | 10.03 |
| Energy & Environment | Best | Mandya | 75.63 |
| Energy & Environment | Worst | Shivamogga | 17.17 |
| Human Capital | Best | Tumakuru | 100.00 |
| Human Capital | Worst | Uttara Kannada | 0.00 |
| Industry | Best | Raichur | 100.00 |
| Industry | Worst | Mysuru | 0.56 |
| Infrastructure | Best | Haveri | 79.14 |
| Infrastructure | Worst | Mandya | 12.16 |
| Innovation | Best | Bengaluru Urban | 100.00 |
| Innovation | Worst | Dakshina Kannada | 0.20 |

### Most Uneven Development (highest dimension-score range)

| Rank | District | Score Range | Avg Dimension Score |
|:----:|----------|:-----------:|:-------------------:|
| 1 | Tumakuru | 98.22 | 40.65 |
| 2 | Raichur | 98.04 | 55.80 |
| 3 | Mandya | 96.83 | 49.59 |
| 4 | Bengaluru Rural | 90.96 | 50.53 |
| 5 | Shivamogga | 89.64 | 39.42 |
| 6 | Chitradurga | 87.14 | 51.79 |
| 7 | Hassan | 86.54 | 47.73 |
| 8 | Bidar | 79.98 | 42.86 |
| 9 | Vijayapura | 78.64 | 40.21 |
| 10 | Haveri | 78.24 | 44.06 |
| 11 | Kalaburagi | 75.41 | 50.05 |
| 12 | Yadgir | 75.17 | 49.68 |
| 13 | Vijayanagara | 73.23 | 50.96 |
| 14 | Ramanagara | 72.87 | 38.70 |
| 15 | Ballari | 71.84 | 32.08 |
| 16 | Chikkaballapura | 71.66 | 42.30 |
| 17 | Koppal | 70.67 | 28.18 |
| 18 | Davanagere | 69.23 | 38.47 |
| 19 | Belagavi | 68.06 | 36.45 |
| 20 | Bengaluru Urban | 67.44 | 64.42 |
| 21 | Dakshina Kannada | 64.56 | 30.72 |
| 22 | Kodagu | 64.51 | 30.29 |
| 23 | Uttara Kannada | 64.04 | 30.98 |
| 24 | Chamarajanagar | 60.79 | 40.12 |
| 25 | Dharwad | 59.97 | 36.42 |
| 26 | Gadag | 59.92 | 40.36 |
| 27 | Chikkamagaluru | 58.67 | 28.27 |
| 28 | Bagalkote | 57.14 | 30.47 |
| 29 | Kolar | 51.68 | 36.79 |
| 30 | Mysuru | 44.85 | 23.39 |
| 31 | Udupi | 25.88 | 20.04 |

---

## Stage 14 – Exploratory Data Analysis

### Descriptive Statistics (raw / processed values)

| Indicator | Dimension | Direction | Mean | Min | Max | Range | CV% |
|-----------|-----------|:---------:|-----:|----:|----:|------:|----:|
| Broadband per 1,000 population | Digital Access | positive | 182.591 | 50.971 | 294.712 | 243.740 | 41.1 |
| Household internet penetration | Digital Access | positive | 34.669 | 15.477 | 54.650 | 39.173 | 36.1 |
| Annual average PM2.5 | Energy & Environment | negative | 33.323 | 18.000 | 48.000 | 30.000 | 24.5 |
| Forest cover percentage | Energy & Environment | positive | 31.429 | 3.618 | 55.082 | 51.464 | 48.9 |
| Renewable energy capacity | Energy & Environment | positive | 2149.819 | 597.000 | 4128.400 | 3531.400 | 41.3 |
| Waste processing rate | Energy & Environment | positive | 55.675 | 33.607 | 83.423 | 49.816 | 25.1 |
| Literacy rate (7+) | Human Capital | positive | 75.619 | 65.310 | 89.504 | 24.194 | 10.6 |
| Industrial employment rate | Industry | positive | 9.685 | 4.737 | 17.281 | 12.545 | 36.8 |
| MSME density | Industry | positive | 8.457 | 4.571 | 13.039 | 8.467 | 30.6 |
| Public transport coverage | Infrastructure | positive | 76.824 | 56.217 | 93.527 | 37.310 | 13.9 |
| Road density | Infrastructure | positive | 1.011 | 0.507 | 1.600 | 1.093 | 34.6 |
| Rural connectivity | Infrastructure | positive | 89.246 | 80.107 | 98.680 | 18.573 | 6.4 |
| Patent applications per 100,000 | Innovation | positive | 1.758 | 0.393 | 18.445 | 18.053 | 178.1 |
| Startups per 100,000 | Innovation | positive | 5.158 | 0.712 | 108.346 | 107.634 | 371.5 |

### Regional Disparity (normalised score range per indicator)

| Indicator | Disparity Range | Max Score | Min Score |
|-----------|:--------------:|:---------:|:---------:|
| Waste processing rate | 100.00 | 100.00 | 0.00 |
| Startups per 100,000 | 100.00 | 100.00 | 0.00 |
| Rural connectivity | 100.00 | 100.00 | 0.00 |
| Road density | 100.00 | 100.00 | 0.00 |
| Renewable energy capacity | 100.00 | 100.00 | 0.00 |
| Public transport coverage | 100.00 | 100.00 | 0.00 |
| Annual average PM2.5 | 100.00 | 100.00 | 0.00 |
| Patent applications per 100,000 | 100.00 | 100.00 | 0.00 |
| MSME density | 100.00 | 100.00 | 0.00 |
| Literacy rate (7+) | 100.00 | 100.00 | 0.00 |
| Household internet penetration | 100.00 | 100.00 | 0.00 |
| Industrial employment rate | 100.00 | 100.00 | 0.00 |
| Forest cover percentage | 100.00 | 100.00 | 0.00 |
| Broadband per 1,000 population | 100.00 | 100.00 | 0.00 |

### Outlier Districts (|z-score| > 2.0)

| District | Indicator | Observed | Mean | Z-Score |
|----------|-----------|:--------:|:----:|:-------:|
| Bengaluru Urban | Startups per 100,000 | 108.3455 | 5.1583 | 5.38 |
| Bengaluru Urban | Patent applications per 100,000 | 18.4455 | 1.7582 | 5.33 |
| Belagavi | Renewable energy capacity | 4128.4000 | 2149.8194 | 2.23 |
| Raichur | Industrial employment rate | 17.2811 | 9.6847 | 2.13 |

### Digital Access vs Industry – Rank Divergence

| District | Digital Score | Industry Score | Rank Divergence |
|----------|:-------------:|:--------------:|:---------------:|
| Koppal | 73.57 | 9.52 | 23 |
| Dharwad | 64.13 | 4.48 | 22 |
| Chitradurga | 35.54 | 72.75 | 17 |
| Ramanagara | 59.64 | 12.66 | 16 |
| Chikkamagaluru | 55.44 | 6.12 | 16 |
| Bidar | 42.83 | 84.20 | 16 |
| Shivamogga | 29.27 | 39.95 | 14 |
| Chikkaballapura | 75.40 | 35.53 | 13 |
| Yadgir | 51.45 | 75.92 | 13 |
| Ballari | 31.78 | 44.58 | 13 |

### Strong Infrastructure, Weak Human Capital

| District | Infrastructure | Human Capital | Gap |
|----------|:--------------:|:-------------:|:---:|
| Hassan | 73.75 | 1.01 | 72.74 |
| Ballari | 73.05 | 1.22 | 71.84 |
| Bidar | 73.28 | 12.32 | 60.96 |
| Haveri | 79.14 | 20.64 | 58.50 |
| Dakshina Kannada | 64.75 | 12.50 | 52.26 |
| Chamarajanagar | 58.08 | 10.63 | 47.45 |
| Kodagu | 69.37 | 27.89 | 41.48 |
| Mysuru | 45.41 | 8.47 | 36.93 |
| Bagalkote | 59.03 | 27.48 | 31.55 |
| Vijayapura | 34.32 | 8.00 | 26.33 |

---

## Stage 15 – Machine Learning (Pending Python Pipeline)

| Method | Priority | Status |
|--------|----------|--------|
| K-Means clustering (k=3) | High | Pending |
| Hierarchical clustering | High | Pending |
| PCA (dimensionality reduction) | Medium | Pending |
| Random Forest (exploratory) | Medium | Pending |
| SHAP feature explanations | Later | Pending |

### Python ML Snippet

```python
import sqlite3, pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

con = sqlite3.connect('InfraSense_Production.db')
df = pd.read_sql(
    'SELECT district_id, indicator_code, normalized_score FROM normalized_indicators', con
).pivot(index='district_id', columns='indicator_code', values='normalized_score')

X = StandardScaler().fit_transform(df.fillna(df.mean()))
km = KMeans(n_clusters=3, init='k-means++', random_state=42, n_init=10)
labels = km.fit_predict(X)

cluster_names = {0: 'Development gaps', 1: 'Moderate development', 2: 'High development'}

run_id = con.execute(
    "INSERT INTO analysis_runs (run_name, algorithm, parameters, notes) VALUES (?,?,?,?)",
    ('kmeans_k3_v1', 'K-Means', '{"n_clusters":3,"init":"k-means++","random_state":42}',
     'Baseline 3-cluster run; all 14 normalised indicators')
).lastrowid
con.commit()

for dist_id, label, dist in zip(df.index, labels, km.transform(X).min(axis=1)):
    con.execute(
        "INSERT INTO district_clusters "
        "(run_id, district_id, cluster_label, cluster_name, distance_to_centroid) "
        "VALUES (?,?,?,?,?)",
        (run_id, dist_id, int(label), cluster_names[int(label)], round(float(dist), 4))
    )
con.commit()
con.close()
```

---

## EDA Views Quick Reference

```sql
SELECT * FROM district_rankings;             -- Overall rankings
SELECT * FROM dimension_rankings;            -- Per-dimension rankings
SELECT * FROM dimension_extremes;            -- Best/worst per dimension
SELECT * FROM development_unevenness;        -- Uneven development
SELECT * FROM dimension_scorecard;           -- Heatmap source (wide)
SELECT * FROM indicator_descriptive_stats;   -- Mean, min, max, CV
SELECT * FROM normalised_indicator_stats;    -- 0-100 distribution
SELECT * FROM indicator_missingness;         -- Completeness check
SELECT * FROM indicator_outliers;            -- z > 2 flagged
SELECT * FROM indicator_regional_disparity;  -- Largest gaps
SELECT * FROM digital_vs_industry;           -- Cross-dimension divergence
SELECT * FROM infra_strong_humancap_weak;    -- Specific mismatch
SELECT * FROM cluster_summary;              -- ML cluster results
SELECT * FROM feature_importance_summary;   -- SHAP contributions
```

---

## Next Steps

- [ ] Replace SYNTHETIC values with real government data
      (Census 2011, PMGSY, Udyam, CPCB, MoSPI, Startup India, IPO)
- [ ] Record source URLs and download dates in `data_sources`
- [ ] Record raw field values in `raw_observations`
- [ ] Re-run normalisation with updated min/max from real data
- [ ] Review and adjust dimension/indicator weights if needed
- [ ] Run Python ML pipeline (K-Means, hierarchical, PCA)
- [ ] Save ML results to `district_clusters` and `model_explanations`
- [ ] Validate cluster stability (elbow curve, silhouette score)
- [ ] Build visualisations (heatmap, PCA biplot, cluster scatter)

---

## Files in Project Folder

| File | Description | Last Updated |
|------|-------------|-------------|
| `InfraSense_Karnataka_Master_Dataset_SYNTHETIC.xlsx` | Master dataset (synthetic) | 12 Nov 2026 14:57 IST |
| `InfraSense_Stages_11_to_15_SQLite.sql` | Full SQL schema, data, and views | 12 Nov 2026 15:27 IST |
| `InfraSense_Production.db` | Live SQLite database | 12 Nov 2026 15:28 IST |
| `InfraSense_Project_Log.md` | This file – project log and results | 12 Nov 2026 15:30 IST |

---
*Log auto-generated from `InfraSense_Production.db`. Update this file after every session.*
