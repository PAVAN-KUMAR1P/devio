# InfraSense — Frontend Architecture & UI/UX Design Specification
**File:** `FRONTEND_ARCHITECTURE.md`  
**Project:** InfraSense – Karnataka District Development Analytics Platform  
**Target Stack:** React 18+ (TypeScript), Tailwind CSS, Recharts / Lucide Icons, FastAPI (Backend), SQLite (Storage).  
**Design Paradigm:** Modern GovTech Analytical Portal (inspired by NITI Aayog Aspirational Blocks Programme, DISHA Dashboard, and Urban Cerebro).

---

## 1. Design System & Visual Identity

### 1.1 Color Palette
- **Primary / Slate Core:** `#0f172a` (Slate 900 - Background dark), `#1e293b` (Slate 800 - Card surfaces), `#334155` (Slate 700 - Borders).
- **Brand / Accent Blue:** `#2563eb` (Blue 600 - Primary actions), `#3b82f6` (Blue 500 - Highlights), `#60a5fa` (Blue 400 - Light accents).
- **Semantic Tiering & Performance:**
  - **High Performance / Low Need:** `#10b981` (Emerald 500 - Scores 60–100, "STRENGTH")
  - **Moderate / Emerging:** `#f59e0b` (Amber 500 - Scores 40–59, "MEDIUM Priority")
  - **Critical Gap / High Need:** `#ef4444` (Rose 500 - Scores 0–39, "HIGH Priority / Deficit")
  - **Special Polarity (PM2.5):** Inverted color scaling (lower PM2.5 is cleaner / green).

### 1.2 Typography & Grid
- **Font Stack:** Inter / Roboto / System sans-serif for high tabular density and metric legibility.
- **Layout Architecture:** Fixed collapsible sidebar navigation (260px) + fluid responsive main content canvas (min 1280px desktop optimized) + top contextual navbar.

---

## 2. Page Architecture & Routing (11 Dedicated Views)

```
InfraSense Web Application
├── / (Home / Executive Overview Dashboard)
├── /map (Karnataka Choropleth Interactive Map)
├── /rankings (Composite & Dimension District Rankings)
├── /district/:id (Individual District Profile & Diagnostic Deep-Dive)
├── /indicators (14 Indicators Explorer & Descriptive Statistics)
├── /compare (Multi-District Side-by-Side Comparison Matrix)
├── /clusters (Unsupervised Machine Learning & K-Means Clusters)
├── /pca (Principal Component Analysis & Biplot Visualization)
├── /explainability (State Benchmark Gap & Divergence Analytics)
├── /recommendations (SDG-Mapped Action Prioritization Matrix)
└── /methodology (Audit Transparency, Formulas, Weights & Data Dictionary)
```

---

## 3. Wireframes & Layout Blueprint

### 3.1 Overview / Main Dashboard (`/`)

```
+-----------------------------------------------------------------------------------------------+
| [LOGO] InfraSense Karnataka               [Search District...]   [API Status: Connected (v1.0)] |
+-----------------------------------------------------------------------------------------------+
| [Sidebar] | [KPI 1: 31 Districts]   [KPI 2: 44.5 State Avg]   [KPI 3: Top: BLR Urban]   [KPI 4: Lag: Udupi]  |
|           +-----------------------------------------------------------------------------------+
| * Overview| [ Karnataka Interactive Choropleth Map ]     [ 6-Dimension Macro Radar / Summary ]  |
| * Map     | - Color-coded by Overall Composite Score     | - Infrastructure: 51.4            |
| * Rankings| - Hover: District Name, Rank, Score          | - Digital Access: 49.3            |
| * Profile | - Click: Direct navigate to District Page    | - Industry: 39.8                  |
| * Compare |                                              | - Innovation: 8.4                 |
| * Cluster |                                              | - Energy & Env: 47.9              |
| * PCA     |                                              | - Human Capital: 42.6             |
| * Explains+-----------------------------------------------------------------------------------+
| * Recos   | [ Top 5 vs Bottom 5 Performance Bar ]        | [ Quick Action Policy Priorities ]|
| * Settings| - Top: BLR Urban, Raichur, Chitradurga...    | - Critical districts in Digital   |
|           | - Lag: Udupi, Mysuru, Chikkamagaluru...      | - Top MSME growth clusters        |
+-----------------------------------------------------------------------------------------------+
```

### 3.2 Individual District Profile (`/district/:id`)

```
+-----------------------------------------------------------------------------------------------+
| < Back to Rankings     DISTRICT: Bengaluru Urban (KA-005)              Cluster: 0 (Urban Core)|
+-----------------------------------------------------------------------------------------------+
| [ Overall Score: 60.18 / 100 ]   [ State Rank: #1 of 31 ]   [ Area: 2,191 km² ]  [ Pop: 9.62M ]  |
+-------------------------------------------------------+---------------------------------------+
| [ Six-Dimension Radar Profile ]                       | [ Top Strengths & Deficits vs State ] |
|                Infrastructure (32.6)                  | + STRENGTH: Innovation (+94.2 vs KA)  |
|                         /\                            | + STRENGTH: Human Capital (+47.5 vs KA)|
|    Human Cap (90.1)    /  \    Digital Access (52.3)  | + STRENGTH: Industry (+14.9 vs KA)    |
|             \         /    \          /               | - DEFICIT:  Infrastructure (-17.6)    |
|              \       /      \        /                | - DEFICIT:  Renewable Energy (-19.2)  |
|       E & Env \_____/________\______/ Industry (57.6) |                                       |
|        (53.9)       \        /                        +---------------------------------------+
|                      \      /                         | [ Cluster Benchmark Peer Context ]   |
|                       \    /                          | - Distance to Centroid: 1.42          |
|                    Innovation (100.0)                 | - Urban Core high-tech profile        |
+-------------------------------------------------------+---------------------------------------+
| [ 14 Indicators Scorecard & Raw Values Table ]                                                |
| Indicator Name              Raw Value    Norm Score    State Avg    Gap vs State   Priority   |
| Road density                0.86 km/km²  32.6 / 100    1.01 km/km²  -0.15          HIGH       |
| Startups per 100,000        108.3        100.0 / 100   5.16         +103.18        OK         |
| Broadband per 1,000         89.4         15.8 / 100    182.59       -93.19         HIGH       |
+-----------------------------------------------------------------------------------------------+
| [ Tailored Policy Interventions & SDG Mapping ]                                               |
| - [HIGH] Accelerate PMGSY; target unconnected habitations [SDG 9.1]                          |
| - [HIGH] Expand rooftop solar and decentralized renewable microgrids [SDG 7.2]                |
| - [HIGH] Expand broadband infrastructure and public CSC points [SDG 9.c]                      |
+-----------------------------------------------------------------------------------------------+
```

### 3.3 District Comparison Matrix (`/compare`)

```
+-----------------------------------------------------------------------------------------------+
| Select Districts to Compare: [x] Bengaluru Urban  [x] Raichur  [x] Mysuru   [+ Add District]  |
+-----------------------------------------------------------------------------------------------+
| Metric                      | Bengaluru Urban (KA-005) | Raichur (KA-023)    | Mysuru (KA-022)   |
+-----------------------------+--------------------------+---------------------+-------------------+
| Overall Rank & Score        | #1 (60.18)               | #2 (59.70)          | #30 (25.30)       |
| Cluster Assignment          | Cluster 0 (Urban Core)   | Cluster 1 (Moderate)| Cluster 2 (Lags)  |
| Infrastructure Score        | 32.6                     | 44.0                | 45.4              |
| Digital Access Score        | 52.3                     | 61.1                | 42.3              |
| Industry Score              | 57.6                     | 100.0               | 0.6               |
| Innovation Score            | 100.0                    | 2.0                 | 2.3               |
| Energy & Environment Score  | 53.9                     | 47.5                | 41.3              |
| Human Capital Score         | 90.1                     | 80.2                | 8.5               |
+-----------------------------+--------------------------+---------------------+-------------------+
| [ Grouped Bar Chart: Side-by-Side Dimension Comparison across Selected Districts ]            |
| [ Grouped Radar Chart: Multi-district Overlay ]                                               |
+-----------------------------------------------------------------------------------------------+
```

---

## 4. Frontend Component Hierarchy

```
frontend/src/
├── main.tsx                           # Application entry point
├── App.tsx                            # Root component with routing and global layout
├── index.css                          # Global styles, Tailwind directives & CSS variables
├── types/
│   └── api.ts                         # TypeScript interfaces matching backend Pydantic models
├── services/
│   └── api.ts                         # Central API client (fetch/axios) with error handling
├── components/
│   ├── layout/
│   │   ├── Sidebar.tsx                # Fixed collapsible navigation with active route highlights
│   │   ├── Navbar.tsx                 # Header with title, live backend status badge & search
│   │   └── Footer.tsx                 # Methodology disclaimer and copyright
│   ├── common/
│   │   ├── MetricCard.tsx             # Stat summary card with icon, delta, and subtitle
│   │   ├── Badge.tsx                  # Semantic priority pill (High, Medium, OK, Positive/Negative)
│   │   ├── LoadingSpinner.tsx         # Unified skeleton / loading animation
│   │   ├── ErrorAlert.tsx             # Friendly error boundary with retry trigger
│   │   └── SearchBar.tsx              # Autocomplete district search input
│   ├── charts/
│   │   ├── KarnatakaMap.tsx           # Interactive SVG Choropleth Map with hover & click handlers
│   │   ├── DimensionRadar.tsx         # 6-axis Recharts radar chart for dimension scores
│   │   ├── GroupedBarChart.tsx        # Comparative bar charts for multi-district comparisons
│   │   ├── PCABiplotChart.tsx         # 2D Scatter plot for PC1 vs PC2 with cluster coloring
│   │   ├── PriorityMatrixGrid.tsx     # District × Indicator priority heatmap table
│   │   └── CorrelationHeatmap.tsx     # Indicator inter-correlation matrix display
├── pages/
│   ├── OverviewPage.tsx               # Main Dashboard with KPIs, Map, Summary & Top/Bottom
│   ├── MapPage.tsx                    # Full-screen Karnataka choropleth with dimension filters
│   ├── RankingsPage.tsx               # Sortable, filterable 31-district ranking scorecard
│   ├── DistrictProfilePage.tsx        # Deep-dive per district (radar, 14 indicators, recos)
│   ├── IndicatorsPage.tsx             # Catalog of 14 indicators and descriptive statistics
│   ├── ComparePage.tsx                # Side-by-side comparison of 2 to 5 districts
│   ├── ClustersPage.tsx               # K-Means clusters and hierarchical groupings
│   ├── PCAPage.tsx                    # Dimensionality reduction and variance scree view
│   ├── ExplainabilityPage.tsx         # Divergence from state benchmark gap analysis
│   ├── RecommendationsPage.tsx        # Actionable recommendations & SDG alignment explorer
│   └── MethodologyPage.tsx            # Transparency report, formulas, weights & audit records
```

---

## 5. API Service Layer Architecture

The frontend integrates with the seven FastAPI routers via a centralized, typed client:

```typescript
// services/api.ts
const API_BASE = 'http://localhost:8000';

export async function fetchAllDistricts(): Promise<DistrictSummary[]> { ... }
export async function fetchDistrictProfile(districtId: string): Promise<DistrictProfile> { ... }
export async function fetchIndicators(): Promise<IndicatorInfo[]> { ... }
export async function fetchIndicatorStats(): Promise<IndicatorStats[]> { ... }
export async function fetchOverallRankings(): Promise<RankingEntry[]> { ... }
export async function fetchDimensionRankings(dim: string): Promise<DimensionRankingEntry[]> { ... }
export async function fetchClusters(): Promise<ClusterSummaryEntry[]> { ... }
export async function fetchClusterDistricts(clusterId: number): Promise<ClusterDetail[]> { ... }
export async function fetchDistrictComparison(districtIds: string[]): Promise<CompareEntry[]> { ... }
export async function fetchRecommendations(districtId: string): Promise<RecommendationEntry[]> { ... }
export async function fetchRegionalDisparity(): Promise<EDADisparityEntry[]> { ... }
export async function fetchOutliers(): Promise<EDAOutlierEntry[]> { ... }
export async function fetchDevelopmentUnevenness(): Promise<EDAUnevennessEntry[]> { ... }
```

---

## 6. Interactive Karnataka Choropleth Map Implementation

- An interactive SVG map component renders all 31 districts with accurate geographic positioning.
- Each district path is color-coded using an interpolated color ramp ($0 \to 100$) based on the currently selected metric (Overall Composite Score or any of the 6 individual dimensions).
- Hovering surfaces district name, rank, and score.
- Clicking navigates directly to that district's dedicated profile page (`/district/:id`).

---

## 7. Audit Disclaimer Integration

Every page and header includes an explicit GovTech transparency badge:
> **Notice:** Prototype Pipeline — Running on synthetic baseline observations. Values demonstrate analytical workflows and must be substituted with validated departmental data prior to administrative adoption.
