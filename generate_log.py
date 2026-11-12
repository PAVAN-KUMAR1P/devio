import sqlite3

db_path   = r'c:\Users\Pavan Kumar P\OneDrive\Desktop\5TH SEM\el\InfraSense_Production.db'
log_path  = r'c:\Users\Pavan Kumar P\OneDrive\Desktop\5TH SEM\el\InfraSense_Project_Log.md'

con = sqlite3.connect(db_path)
cur = con.cursor()

cur.execute('SELECT district_name, overall_score, district_rank FROM district_rankings ORDER BY district_rank')
rankings = cur.fetchall()

cur.execute('SELECT district_name, infrastructure_score, digital_access_score, industry_score, innovation_score, energy_env_score, human_capital_score, overall_score FROM dimension_scorecard ORDER BY overall_score DESC')
scorecard = cur.fetchall()

cur.execute('SELECT indicator_name, dimension, direction, n, mean_value, min_value, max_value, range_value, cv_pct FROM indicator_descriptive_stats')
stats = cur.fetchall()

cur.execute('SELECT indicator_name, disparity_range, max_score, min_score FROM indicator_regional_disparity ORDER BY disparity_range DESC')
disparity = cur.fetchall()

cur.execute('SELECT district_name, indicator_name, observed_value, indicator_mean, z_score FROM indicator_outliers ORDER BY ABS(z_score) DESC')
outliers = cur.fetchall()

cur.execute('SELECT district_name, score_range, avg_dim_score FROM development_unevenness ORDER BY score_range DESC')
unevenness = cur.fetchall()

cur.execute('SELECT dimension, position, district_name, dimension_score FROM dimension_extremes ORDER BY dimension, position')
extremes = cur.fetchall()

cur.execute('SELECT district_name, digital_access_score, industry_score, rank_divergence FROM digital_vs_industry ORDER BY rank_divergence DESC LIMIT 10')
dig_ind = cur.fetchall()

cur.execute('SELECT district_name, infrastructure_score, human_capital_score, gap FROM infra_strong_humancap_weak ORDER BY gap DESC LIMIT 10')
infra_hc = cur.fetchall()

cur.execute("SELECT COUNT(*) FROM district_master");        nd = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM indicator_master");       ni = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM processed_indicators");   nobs = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM normalized_indicators");  nnorm = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM district_scores WHERE score_type='dimension'"); ndim = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM district_scores WHERE score_type='overall'");  nov = cur.fetchone()[0]
con.close()

# ─── build content ───────────────────────────────────────────────────────────
parts = []

parts.append("""\
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
""")

parts.append("| Table | Purpose | Records |")
parts.append("|-------|---------|---------|")
parts.append(f"| `district_master` | 31 Karnataka districts | {nd} |")
parts.append(f"| `indicator_master` | 14 indicator definitions | {ni} |")
parts.append("| `data_sources` | Source metadata | 0 (populate when real data sourced) |")
parts.append("| `raw_observations` | Original pre-calculated field values | 0 (populate when real data sourced) |")
parts.append(f"| `processed_indicators` | Calculated CALC: indicator values | {nobs} |")
parts.append(f"| `normalization_config` | Min/max and direction per indicator | {ni} |")
parts.append(f"| `normalized_indicators` | 0–100 scores (district × indicator) | {nnorm} |")
parts.append(f"| `indicator_weights` | Within-dimension indicator weights | {ni} |")
parts.append("| `dimension_weights` | Weight of each of the 6 dimensions | 6 |")
parts.append(f"| `district_scores` | Dimension and overall scores | {ndim + nov} |")
parts.append("| `analysis_runs` | ML experiment metadata | 0 (populate via Python) |")
parts.append("| `district_clusters` | Cluster assignments from ML runs | 0 (populate via Python) |")
parts.append("| `model_explanations` | SHAP feature contributions | 0 (populate via Python) |")

parts.append("""
---

## Stage 11 – Normalisation

**Formulae:**
- Positive indicator: `score = (X - X_min) / (X_max - X_min) × 100`
- Negative indicator: `score = (X_max - X) / (X_max - X_min) × 100`

**Only negative indicator:** `pm25` (Annual average PM2.5 µg/m³) — lower is better.

### Observed Min / Max for each Indicator
""")

parts.append("| Indicator | Dimension | Direction | Min | Max |")
parts.append("|-----------|-----------|-----------|----:|----:|")
for s in stats:
    name, dim, direc, n_val, mean_v, min_v, max_v, range_v, cv = s
    parts.append(f"| {name} | {dim} | {direc} | {min_v:.4f} | {max_v:.4f} |")

parts.append("""
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
|:----:|----------|:-------------:|""")

for r in rankings:
    parts.append(f"| {r[2]} | {r[0]} | {r[1]:.2f} |")

parts.append("""
### Dimension Scorecard

| District | Infra | Digital | Industry | Innovation | E&Env | HumanCap | **Overall** |
|----------|:-----:|:-------:|:--------:|:----------:|:-----:|:--------:|:-----------:|""")

for r in scorecard:
    name, inf, dig, ind, inn, een, hc, ov = r
    parts.append(f"| {name} | {inf:.1f} | {dig:.1f} | {ind:.1f} | {inn:.1f} | {een:.1f} | {hc:.1f} | **{ov:.2f}** |")

parts.append("""
### Best and Worst District per Dimension

| Dimension | Position | District | Score |
|-----------|:--------:|----------|:-----:|""")

for r in extremes:
    dim, pos, dist, sc = r
    parts.append(f"| {dim} | {pos} | {dist} | {sc:.2f} |")

parts.append("""
### Most Uneven Development (highest dimension-score range)

| Rank | District | Score Range | Avg Dimension Score |
|:----:|----------|:-----------:|:-------------------:|""")

for i, r in enumerate(unevenness, 1):
    parts.append(f"| {i} | {r[0]} | {r[1]:.2f} | {r[2]:.2f} |")

parts.append("""
---

## Stage 14 – Exploratory Data Analysis

### Descriptive Statistics (raw / processed values)

| Indicator | Dimension | Direction | Mean | Min | Max | Range | CV% |
|-----------|-----------|:---------:|-----:|----:|----:|------:|----:|""")

for s in stats:
    name, dim, direc, n_val, mean_v, min_v, max_v, range_v, cv = s
    cv_str = f"{cv:.1f}" if cv is not None else "N/A"
    parts.append(f"| {name} | {dim} | {direc} | {mean_v:.3f} | {min_v:.3f} | {max_v:.3f} | {range_v:.3f} | {cv_str} |")

parts.append("""
### Regional Disparity (normalised score range per indicator)

| Indicator | Disparity Range | Max Score | Min Score |
|-----------|:--------------:|:---------:|:---------:|""")

for r in disparity:
    parts.append(f"| {r[0]} | {r[1]:.2f} | {r[2]:.2f} | {r[3]:.2f} |")

parts.append("""
### Outlier Districts (|z-score| > 2.0)
""")

if outliers:
    parts.append("| District | Indicator | Observed | Mean | Z-Score |")
    parts.append("|----------|-----------|:--------:|:----:|:-------:|")
    for r in outliers:
        parts.append(f"| {r[0]} | {r[1]} | {r[2]:.4f} | {r[3]:.4f} | {r[4]:.2f} |")
else:
    parts.append("*No outliers detected (|z-score| > 2.0) in this synthetic dataset.*")

parts.append("""
### Digital Access vs Industry – Rank Divergence

| District | Digital Score | Industry Score | Rank Divergence |
|----------|:-------------:|:--------------:|:---------------:|""")

for r in dig_ind:
    parts.append(f"| {r[0]} | {r[1]:.2f} | {r[2]:.2f} | {r[3]} |")

parts.append("""
### Strong Infrastructure, Weak Human Capital

| District | Infrastructure | Human Capital | Gap |
|----------|:--------------:|:-------------:|:---:|""")

for r in infra_hc:
    parts.append(f"| {r[0]} | {r[1]:.2f} | {r[2]:.2f} | {r[3]:.2f} |")

parts.append("""
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
""")

content = '\n'.join(parts)
with open(log_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Log written — {len(content):,} characters, {len(parts)} lines")
print(f"Path: {log_path}")
