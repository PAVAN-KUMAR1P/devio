# InfraSense — Stage 1: Data Authenticity and Methodology Audit Report
**File:** `DATA_VALIDATION_REPORT.md`  
**Date of Audit:** 12 November 2026  
**Audit Scope:** Verification of data authenticity, indicator definitions, administrative boundaries, normalization mechanics, weighting schemas, and recommendation algorithms across the InfraSense analytical warehouse.

---

> [!CAUTION]
> ### Critical Audit Finding: Prototype / Synthetic Status
> The current production database (`InfraSense_Production.db`) and master dataset (`InfraSense_Karnataka_Master_Dataset_SYNTHETIC.xlsx`) contain **100% synthetic (pseudo-random) placeholder observations**.
> 
> Tables `data_sources` and `raw_observations` in SQLite currently contain **0 records**.
> 
> Therefore, all **district rankings, ML cluster assignments, PCA components, and policy recommendations are prototype outputs and proof-of-concept pipeline deliverables**, not actual empirical Karnataka development findings. They must not be cited for public policy, governance, or benchmarking until replaced with validated government statistics.

---

## 1. Data Authenticity & Source Verification

### 1.1 Source Ingestion Audit

| Storage Layer | Entity / Table | Record Count | Data Status | Authenticity Verdict |
|---|---|:---:|---|---|
| **SQLite DB** | `data_sources` | 0 | Unpopulated | No primary sources registered |
| **SQLite DB** | `raw_observations` | 0 | Unpopulated | No primary observations recorded |
| **SQLite DB** | `processed_indicators` | 434 | Synthetic | Derived from synthetic workbook |
| **Excel Workbook** | `README` Sheet | — | Synthetic | Explicit disclaimer logged: *"ALL NUMERIC VALUES IN THIS WORKBOOK ARE SYNTHETIC"* |
| **Excel Workbook** | `All_Indicators_Wide` | 31 rows | Synthetic | Directly observed real values: 0; Synthetic values: 100% |

### 1.2 Verification of the 14 Indicators Against Source Records

The audit confirmed the specific architecture of the 14 indicators:
- **13 Formula-Calculated Indicators:** Derived dynamically via formulas from base synthetic fields (e.g., Road density = Road length / Area; Literacy rate = Literate 7+ / Population 7+).
- **1 Raw Pass-Through Indicator (PM2.5):** Annual average PM2.5 ($\mu\text{g}/\text{m}^3$) is not derived from a mathematical ratio of components in the workbook; rather, Column `BB2` (`CALC: Annual average PM2.5`) is a direct 1:1 cell reference (`=AD2`) to the raw synthetic input column `AD2`.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ Indicator Classification: 13 Derived Ratios + 1 Raw Direct Input                       │
├────────────────────┬───────────────────────┬───────────────────────────────────────────┤
│ Indicator Code     │ Excel Formula Column  │ Underlying Derivation                     │
├────────────────────┼───────────────────────┼───────────────────────────────────────────┤
│ road_density       │ CALC: (=E2/AM2)       │ Total road length / District area         │
│ rural_connectivity │ CALC: (=G2/F2*100)    │ Connected habitations / Total habitations │
│ pt_coverage        │ CALC: (=J2/AN2*100)   │ Served population / Total population      │
│ internet_penetr... │ CALC: (=L2/K2*100)    │ Internet households / Total households    │
│ broadband_per1k    │ CALC: (=M2/AN2*1000)  │ Broadband connections / Total pop * 1,000 │
│ msme_density       │ CALC: (=Q2/AN2*1000)  │ Total enterprises / Total pop * 1,000     │
│ industrial_emp_... │ CALC: (=U2/V2*100)    │ MSME employment / Working population      │
│ startup_rate       │ CALC: (=W2/AN2*100000)│ DPIIT startups / Total pop * 100,000      │
│ patent_rate        │ CALC: (=X2/AN2*100000)│ Patent filings / Total pop * 100,000      │
│ renewable_capacity │ CALC: (=Z2+AA2+AB2+AC2│ Solar + Wind + Biomass + Other renewables │
│ pm25               │ PASS-THROUGH (=AD2)   │ Direct raw PM2.5 observation (unmodified) │
│ forest_cover_pct   │ CALC: (=AF2/AM2*100)  │ Forest cover area / District area         │
│ waste_processing...│ CALC: (=AJ2/AI2*100)  │ Processed waste / Total generated waste   │
│ literacy_rate      │ CALC: (=AL2/AK2*100)  │ Literate pop 7+ / Total pop 7+            │
└────────────────────┴───────────────────────┴───────────────────────────────────────────┘
```

---

## 2. Administrative Boundaries, District Names & Codes

### 2.1 District Names and Total Count
- **Count:** Exactly 31 districts exist in `district_master`.
- **District Identifiers:** Keyed with standard synthetic prefixes `KA-001` through `KA-031`.

### 2.2 Local Government Directory (LGD) Codes
- **Finding:** LGD codes are **completely absent** from the SQLite schema (`PRAGMA table_info(district_master)` has columns: `['district_id', 'district_name', 'census_2011_code', 'area_km2', 'population', 'notes']`).
- **Excel Audit:** In `InfraSense_Karnataka_Master_Dataset_SYNTHETIC.xlsx`, column `LGD_Code` exists in `District_Master` and `All_Indicators_Wide`, but all 31 entries are set to `None`/blank with the note: *"LGD codes are left BLANK (NULL) because they were not verified"*.
- **Remediation Required:** Prior to production ingestion of government records, the schema should add an `lgd_code INTEGER` column and populate verified codes from `lgdirectory.gov.in`.

### 2.3 Historical District Boundaries & Bifurcations
- **Vijayanagara Bifurcation (2021):**
  - Vijayanagara (`KA-031`) was officially established on 2 October 2021 by carving out 6 taluks from Ballari (`KA-002`).
  - In `district_master`, Ballari has the note: `"Reduced after Vijayanagara split (2021)"`, and Vijayanagara has: `"New district carved from Ballari (2021)"`.
  - **Census 2011 Limitation:** Because Vijayanagara did not exist in the 2011 Census, official 2011 Census tables do not contain discrete entries for Vijayanagara. In the SQLite database, an artificial code `31` was assigned to Vijayanagara for tabular continuity.
  - **Area and Population Placeholder Warning:** The synthetic table lists Belagavi area as 5,499.5 km² (Census 2011 actual was 13,415 km²). Similarly, Ballari (8,088.7 km²) and Vijayanagara (7,497.0 km²) are synthetic representations.

---

## 3. Mathematical Normalization Audit

### 3.1 Normalization Mechanics
The database implements Min-Max rescaling onto a 0–100 interval:
- **Positive indicators (Higher = Better):**
  $$\text{Score} = \frac{X - X_{\min}}{X_{\max} - X_{\min}} \times 100$$
- **Negative indicators (Lower = Better):**
  $$\text{Score} = \frac{X_{\max} - X}{X_{\max} - X_{\min}} \times 100$$

### 3.2 Polarity & Boundary Verification
- **Negative Polarity Indicator:** `pm25` is correctly flagged as `direction = 'negative'` in `normalization_config` and `indicator_master`.
- **Boundary Verification:** 100% of observed minimums and maximums stored in `normalization_config` strictly match the exact min and max from `processed_indicators`.

### 3.3 Calculation Precision Check
- Tested all 434 records in `normalized_indicators` against the theoretical formula.
- **Mismatches ($>0.01$):** 0
- **Maximum Absolute Discrepancy:** $0.00004975$ (attributable to floating-point rounding).
- **Result:** **PASSED with 100% mathematical fidelity.**

---

## 4. Indicator & Dimension Weighting Audit

### 4.1 Weight Normalization Checks
1. **Dimension Weights:**
   - Infrastructure: $0.20$
   - Digital Access: $0.15$
   - Industry: $0.20$
   - Innovation: $0.10$
   - Energy & Environment: $0.20$
   - Human Capital: $0.15$
   - **Sum:** Exactly $1.000$ ($100\%$).
2. **Indicator Weights (Within Dimension):**
   - Infrastructure: Road density (0.333), Rural connectivity (0.333), PT coverage (0.334) $\implies$ Sum = $1.000$.
   - Digital Access: Internet penetration (0.500), Broadband per 1k (0.500) $\implies$ Sum = $1.000$.
   - Industry: MSME density (0.500), Industrial employment rate (0.500) $\implies$ Sum = $1.000$.
   - Innovation: Startup rate (0.500), Patent rate (0.500) $\implies$ Sum = $1.000$.
   - Energy & Environment: Renewable capacity (0.300), PM2.5 (0.300), Forest cover (0.200), Waste processing (0.200) $\implies$ Sum = $1.000$.
   - Human Capital: Literacy rate (1.000) $\implies$ Sum = $1.000$.

### 4.2 Composite Score Replication Check
- Re-calculated all 186 dimension scores in `district_scores`: Max difference from stored score $< 0.000050$.
- Re-calculated all 31 overall district scores: Max difference from stored score $< 0.000050$.
- **Result:** **PASSED with 100% mathematical fidelity.**

---

## 5. Missing Data Handling & Coverage Thresholds

- **Methodology Rule:** A district dimension score is flagged as invalid (`is_valid = 0`) if available indicators represent less than $70\%$ of the dimension's total indicator weight.
- **Audit Result:**
  - In the current synthetic database, missing values = 0 across all 434 records.
  - Weight coverage = $1.000$ ($100\%$) across all districts.
  - `is_valid` flag is $1$ for all 31 districts.
  - **Verdict:** Pipeline handles coverage rules correctly; fallback tests in Stage 2 confirm graceful degradation when records are absent.

---

## 6. Rankings & Recommendation Engine Audit

### 6.1 District Rankings
- Overall scores range from **60.18** (Bengaluru Urban) to **21.50** (Udupi).
- District ranks are strictly monotonic ($1$ to $31$) with zero gaps or tie-breaking failures.

### 6.2 Policy Recommendations & Priority Logic
- **Priority Tiering:**
  - $\text{Score} < 40 \implies \textbf{HIGH Priority}$ (219 interventions statewide)
  - $40 \le \text{Score} \le 60 \implies \textbf{MEDIUM Priority}$ (73 interventions statewide)
  - $\text{Score} > 60 \implies \textbf{OK / STRENGTH}$ (142 indicators statewide)
- **Cluster Peer Comparison:** Automatically appends `[lags cluster peers]` when an indicator score falls below the cluster mean.
- **UN SDG Mapping Verification:** All 14 indicators map to valid Sustainable Development Goals:
  - *SDG 4.6 (Literacy), SDG 7.2 (Renewable Energy), SDG 8.3 & 8.5 (Industry & Employment), SDG 9.1, 9.b, 9.c (Infrastructure, Digital, Innovation), SDG 11.2 & 11.6 (Transport & Clean Air), SDG 15.2 (Forest Cover).*

---

## 7. Audit Checklist Summary

| Verification Item | Requirement | Status | Notes |
|---|---|:---:|---|
| **Data Authenticity** | Real vs. Synthetic verification | **CONFIRMED SYNTHETIC** | Tables `data_sources` & `raw_observations` are empty. |
| **Indicator Types** | Derived vs. Raw verification | **VERIFIED** | 13 formula-calculated indicators, 1 raw input pass-through (PM2.5). |
| **Administrative Units** | 31 Karnataka Districts | **VERIFIED** | All 31 present, including Vijayanagara split noted. |
| **LGD Codes** | Verification against standard | **BLANK / ABSENT** | Schema lacks LGD column; Excel entries blank. |
| **Normalization** | Positive & Negative min-max formulas | **VERIFIED (100%)** | Max error $< 0.00005$; PM2.5 inverted correctly. |
| **Weighting Schema** | Within-dimension and cross-dimension | **VERIFIED (100%)** | All dimensions sum to 1.0; all indicators sum to 1.0. |
| **Coverage Rules** | 70% threshold enforcement | **VERIFIED** | Current coverage is 100% across all districts. |
| **Recommendations** | Priority thresholds and SDG links | **VERIFIED** | 434 records populated with correct tiers and SDG tags. |
