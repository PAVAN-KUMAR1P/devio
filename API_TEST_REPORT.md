# InfraSense — Stage 2: Backend Testing & API Validation Report
**File:** `API_TEST_REPORT.md`  
**Test Suite Directory:** [`backend/tests/`](file:///c:/Users/Pavan%20Kumar%20P/OneDrive/Desktop/5TH%20SEM/el/backend/tests/)  
**OpenAPI Specification:** [`backend/openapi.json`](file:///c:/Users/Pavan%20Kumar%20P/OneDrive/Desktop/5TH%20SEM/el/backend/openapi.json)  
**Execution Engine:** `pytest 9.2.0` | `Python 3.14.2` | `FastAPI 0.115+` | `Pydantic 2.x`  
**Status:** **56 / 56 PASSED (100% Success Rate)**

---

## 1. Executive Summary

A comprehensive automated test suite has been implemented in [`backend/tests/`](file:///c:/Users/Pavan%20Kumar%20P/OneDrive/Desktop/5TH%20SEM/el/backend/tests/) covering all **7 API routers**, **14 endpoints**, **13 Pydantic response models**, and rigorous **edge-case/error-handling conditions**.

```
============================= test session starts =============================
platform win32 -- Python 3.14.2, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\Users\Pavan Kumar P\OneDrive\Desktop\5TH SEM\el
plugins: anyio-4.12.1
collected 56 items

backend/tests/test_clusters.py .............. PASSED [5/5]
backend/tests/test_compare.py ............... PASSED [6/6]
backend/tests/test_districts.py ............. PASSED [5/5]
backend/tests/test_eda.py ................... PASSED [3/3]
backend/tests/test_errors_and_edge_cases.py . PASSED [24/24]
backend/tests/test_indicators.py ............ PASSED [2/2]
backend/tests/test_pydantic_schemas.py ...... PASSED [4/4]
backend/tests/test_rankings.py .............. PASSED [4/4]
backend/tests/test_recommendations.py ....... PASSED [3/3]

============================= 56 passed in 1.91s ==============================
```

---

## 2. Router Testing & Validation Breakdown

### 2.1 Districts Router ([`test_districts.py`](file:///c:/Users/Pavan%20Kumar%20P/OneDrive/Desktop/5TH%20SEM/el/backend/tests/test_districts.py))
- **`GET /districts`:**
  - Verifies exact return of all 31 districts.
  - Confirms mandatory fields: `district_id` (starts with `KA-`), `district_name`, `area_km2`, and `population`.
  - Asserts strict alphabetical ordering by `district_name`.
- **`GET /districts/{district_id}`:**
  - Parameterized testing across diverse districts (`KA-001` Bagalkote, `KA-005` Bengaluru Urban, and `KA-031` Vijayanagara).
  - Validates overall score ($0 \le \text{score} \le 100$), overall rank ($1 \le \text{rank} \le 31$), and cluster assignments.
  - Verifies that all 6 dimension scores and all 14 normalized indicator scores are present and bounded.
- **Error Handling:** Nonexistent ID (`KA-999`) correctly raises `HTTPException 404` with detail: `"District KA-999 not found"`.

### 2.2 Indicators Router ([`test_indicators.py`](file:///c:/Users/Pavan%20Kumar%20P/OneDrive/Desktop/5TH%20SEM/el/backend/tests/test_indicators.py))
- **`GET /indicators`:**
  - Verifies full catalog of all 14 indicators across the 6 dimensions.
  - Validates indicator codes, names, units, and directions.
  - Confirms that `pm25` is the single indicator with `negative` polarity, while the remaining 13 are `positive`.
- **`GET /indicators/stats`:**
  - Verifies descriptive statistical moments for all 14 indicators.
  - Confirms sample size $n = 31$ for each indicator.
  - Asserts mathematical consistency: $\min \le \mu \le \max$, $\text{range} = \max - \min$, and $\text{CV}\% > 0$.

### 2.3 Rankings Router ([`test_rankings.py`](file:///c:/Users/Pavan%20Kumar%20P/OneDrive/Desktop/5TH%20SEM/el/backend/tests/test_rankings.py))
- **`GET /rankings/overall`:**
  - Validates all 31 district ranks from Rank 1 down to Rank 31.
  - Verifies monotonic non-increasing overall scores (Top: Bengaluru Urban - 60.18; Bottom: Udupi - 21.50).
  - Asserts `weight_coverage = 1.0` and `is_valid = 1`.
- **`GET /rankings/dimension/{dimension}`:**
  - Validates rankings across each of the 6 dimensions (`Infrastructure`, `Digital Access`, `Industry`, `Innovation`, `Energy & Environment`, `Human Capital`).
  - Confirms case-insensitive query matching (e.g. `infrastructure`, `INFRASTRUCTURE`, `Infrastructure`).
- **Error Handling:** Invalid dimension strings (e.g. `NonExistentDimension`) trigger `HTTPException 400` with list of valid options.

### 2.4 Clusters Router ([`test_clusters.py`](file:///c:/Users/Pavan%20Kumar%20P/OneDrive/Desktop/5TH%20SEM/el/backend/tests/test_clusters.py))
- **`GET /clusters`:**
  - Validates summary of $k=3$ K-Means clusters (Clusters 0, 1, and 2).
  - Asserts total district membership sums to exactly 31.
  - Confirms non-negative average distance to centroids and concatenated district lists.
- **`GET /clusters/{cluster_id}`:**
  - Parameterized tests on Cluster 0, Cluster 1, and Cluster 2.
  - Validates sorting by descending overall score.
- **Error Handling:** Nonexistent cluster ID (`999`) correctly raises `HTTPException 404` (`"No districts found for cluster 999"`).

### 2.5 Compare Router ([`test_compare.py`](file:///c:/Users/Pavan%20Kumar%20P/OneDrive/Desktop/5TH%20SEM/el/backend/tests/test_compare.py))
- **`GET /compare?districts=KA-001,KA-005`:**
  - Side-by-side comparison across 2 and 3 districts.
  - Verifies presence of all 14 indicator scores per district.
- **Error Handling:**
  - Fewer than 2 districts (`KA-001`) raises `HTTPException 400` (`"Provide at least 2 district IDs..."`).
  - More than 10 districts raises `HTTPException 400` (`"Cannot compare more than 10 districts at once."`).
  - All invalid IDs (`KA-998,KA-999`) raises `HTTPException 404` (`"None of the specified districts were found."`).
  - Mixed valid and invalid IDs gracefully returns the valid district slice.

### 2.6 Recommendations Router ([`test_recommendations.py`](file:///c:/Users/Pavan%20Kumar%20P/OneDrive/Desktop/5TH%20SEM/el/backend/tests/test_recommendations.py))
- **`GET /recommendations/{district_id}`:**
  - Returns 14 prioritised recommendations mapped to the 14 indicators.
  - Validates priority sorting: `HIGH` $\to$ `MEDIUM` $\to$ `OK`.
  - Verifies UN SDG references across all recommendations.
- **Error Handling:** Nonexistent district (`KA-999`) correctly raises `HTTPException 404`.

### 2.7 EDA Router ([`test_eda.py`](file:///c:/Users/Pavan%20Kumar%20P/OneDrive/Desktop/5TH%20SEM/el/backend/tests/test_eda.py))
- **`GET /eda/disparity`:** Validates 14 indicators ranked by inter-district spread.
- **`GET /eda/outliers`:** Validates 4 statistical outliers ($|z| > 2.0$), verified with `flag = 'OUTLIER'`.
- **`GET /eda/unevenness`:** Validates 31 districts ranked by internal dimension score range.

---

## 3. Parameterized Error Handling & Edge Cases

File: [`backend/tests/test_errors_and_edge_cases.py`](file:///c:/Users/Pavan%20Kumar%20P/OneDrive/Desktop/5TH%20SEM/el/backend/tests/test_errors_and_edge_cases.py)

| Test Category | Injected Inputs | Expected Behavior | Result |
|---|---|---|:---:|
| **Invalid District IDs** | `""`, `"   "`, `"KA-999"`, `"INVALID"`, `"KA-000"`, `"BENGALURU"` | `HTTPException 404` | **PASSED (6/6)** |
| **Invalid Dimensions** | `""`, `"123"`, `"Economy"`, `"Health"`, `"Education"`, `"unknown"` | `HTTPException 400` | **PASSED (6/6)** |
| **Invalid Cluster IDs** | `-1`, `3`, `4`, `10`, `999` | `HTTPException 404` | **PASSED (5/5)** |
| **Malformed Compare Strings** | `""`, `"   "`, `"KA-001"`, `"KA-001,"`, `",KA-001"`, `"KA-001,   "`, `",,,"` | `HTTPException 400 / 404` | **PASSED (7/7)** |

---

## 4. Pydantic Response Schema Validation

File: [`backend/tests/test_pydantic_schemas.py`](file:///c:/Users/Pavan%20Kumar%20P/OneDrive/Desktop/5TH%20SEM/el/backend/tests/test_pydantic_schemas.py)

All 13 Pydantic schemas in [`backend/models.py`](file:///c:/Users/Pavan%20Kumar%20P/OneDrive/Desktop/5TH%20SEM/el/backend/models.py) were tested against live data and invalid payload injection:
1. `StatusResponse`
2. `DistrictSummary`
3. `DistrictProfile`
4. `DimensionScore`
5. `NormalizedScore`
6. `IndicatorInfo`
7. `IndicatorStats`
8. `RankingEntry`
9. `DimensionRankingEntry`
10. `ClusterSummaryEntry`
11. `ClusterDetail`
12. `CompareEntry`
13. `RecommendationEntry`
14. `EDADisparityEntry`, `EDAOutlierEntry`, `EDAUnevennessEntry`

**Result:** Zero schema mismatch errors. All responses adhere strictly to typed response models.

---

## 5. OpenAPI Specification Generation

The OpenAPI 3.1.0 specification has been compiled and saved to [`backend/openapi.json`](file:///c:/Users/Pavan%20Kumar%20P/OneDrive/Desktop/5TH%20SEM/el/backend/openapi.json).

### Route Inventory (14 Endpoints)

| Method | Path | Summary / Tag |
|---|---|---|
| `GET` | `/` | Health check and API metadata (`root`) |
| `GET` | `/districts` | List all 31 districts (`districts`) |
| `GET` | `/districts/{district_id}` | Full district development profile (`districts`) |
| `GET` | `/indicators` | List 14 indicators with metadata (`indicators`) |
| `GET` | `/indicators/stats` | Indicator descriptive statistics (`indicators`) |
| `GET` | `/rankings/overall` | Overall composite rankings (`rankings`) |
| `GET` | `/rankings/dimension/{dimension}` | Dimension-specific rankings (`rankings`) |
| `GET` | `/clusters` | K-Means cluster summary (`clusters`) |
| `GET` | `/clusters/{cluster_id}` | District list for specific cluster (`clusters`) |
| `GET` | `/compare` | Side-by-side district comparison (`compare`) |
| `GET` | `/recommendations/{district_id}` | Prioritised policy interventions (`recommendations`) |
| `GET` | `/eda/disparity` | Regional disparity metrics (`eda`) |
| `GET` | `/eda/outliers` | Indicator outlier detection (`eda`) |
| `GET` | `/eda/unevenness` | Intra-district unevenness (`eda`) |

---

## 6. Test File Structure

```
backend/
├── openapi.json                                # Generated OpenAPI 3.1.0 specification
└── tests/
    ├── __init__.py                             # Test package indicator
    ├── conftest.py                             # Pytest fixtures and DB setup
    ├── test_districts.py                       # Districts router test cases
    ├── test_indicators.py                      # Indicators router test cases
    ├── test_rankings.py                        # Rankings router test cases
    ├── test_clusters.py                        # Clusters router test cases
    ├── test_compare.py                         # Compare router test cases
    ├── test_recommendations.py                 # Recommendations router test cases
    ├── test_eda.py                             # EDA router test cases
    ├── test_errors_and_edge_cases.py           # Negative and edge-case testing
    └── test_pydantic_schemas.py                # Schema validation tests
```
