import os, warnings
os.environ["MPLCONFIGDIR"] = r"C:\Users\Pavan Kumar P\AppData\Local\Temp"
warnings.filterwarnings("ignore")
import matplotlib; matplotlib.use("Agg")

import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import ListedColormap, BoundaryNorm

PROJECT_FOLDER = r"c:\Users\Pavan Kumar P\OneDrive\Desktop\5TH SEM\el"
DB_PATH = os.path.join(PROJECT_FOLDER, "InfraSense_Production.db")

RECO_MAP = {
  "road_density":           {"sdg":"SDG 9.1","area":"Infrastructure","action":"Invest in road expansion; prioritise rural connectivity corridors"},
  "rural_connectivity":     {"sdg":"SDG 9.1","area":"Infrastructure","action":"Accelerate PMGSY; target unconnected habitations"},
  "pt_coverage":            {"sdg":"SDG 11.2","area":"Infrastructure","action":"Expand bus routes to underserved areas"},
  "internet_penetration":   {"sdg":"SDG 9.c","area":"Digital Access","action":"Deploy BharatNet last-mile; subsidise household internet"},
  "broadband_per1k":        {"sdg":"SDG 9.c","area":"Digital Access","action":"Increase broadband infrastructure; promote CSC digital service points"},
  "msme_density":           {"sdg":"SDG 8.3","area":"Industry","action":"Strengthen MSME clusters; improve credit and market linkages"},
  "industrial_emp_rate":    {"sdg":"SDG 8.5","area":"Industry","action":"Promote skill development aligned to local MSME sectors"},
  "startup_rate":           {"sdg":"SDG 9.b","area":"Innovation","action":"Establish district startup incubators; link to Startup Karnataka"},
  "patent_rate":            {"sdg":"SDG 9.b","area":"Innovation","action":"Support IP awareness in colleges and research institutions"},
  "renewable_capacity":     {"sdg":"SDG 7.2","area":"Energy","action":"Expand solar and wind; promote rooftop solar"},
  "pm25":                   {"sdg":"SDG 11.6","area":"Environment","action":"Strengthen air quality monitoring; reduce industrial emissions"},
  "forest_cover_pct":       {"sdg":"SDG 15.2","area":"Environment","action":"Implement afforestation; protect existing green cover"},
  "waste_processing_pct":   {"sdg":"SDG 11.6","area":"Environment","action":"Upgrade waste processing plants; promote source segregation"},
  "literacy_rate":          {"sdg":"SDG 4.6","area":"Human Capital","action":"Expand adult literacy; improve secondary school retention"}
}

conn = sqlite3.connect(DB_PATH)

# ── Load data ──────────────────────────────────────────────────────────────────
ni = pd.read_sql("SELECT district_id, indicator_code, normalized_score FROM normalized_indicators", conn)
dm = pd.read_sql("SELECT district_id, district_name FROM district_master", conn)
im = pd.read_sql("SELECT indicator_code, indicator_name, dimension FROM indicator_master", conn)
ds = pd.read_sql(
    "SELECT district_id, cluster_label, cluster_name FROM district_clusters "
    "WHERE run_id = (SELECT MAX(run_id) FROM analysis_runs WHERE algorithm='K-Means')",
    conn
)

pivot = ni.pivot(index="district_id", columns="indicator_code", values="normalized_score")
indicator_list = pivot.columns.tolist()

# Cluster mean per indicator
cluster_means = {}
for cl_label in sorted(ds["cluster_label"].unique()):
    cl_districts = ds[ds["cluster_label"] == cl_label]["district_id"].tolist()
    cl_pivot = pivot.loc[[d for d in cl_districts if d in pivot.index]]
    cluster_means[cl_label] = cl_pivot.mean()

# ── 1 & 2. Priority + Cluster lag ─────────────────────────────────────────────
reco_rows = []  # for SQLite
district_recos = {}  # for report

for did in pivot.index:
    district_name = dm.loc[dm["district_id"] == did, "district_name"].values[0]
    row = pivot.loc[did]

    cl_row = ds[ds["district_id"] == did]
    cl_label = int(cl_row["cluster_label"].values[0]) if len(cl_row) > 0 else -1
    cl_mean = cluster_means.get(cl_label, pd.Series(dtype=float))

    high_priority = []
    medium_priority = []

    for ind in indicator_list:
        score = row[ind]
        if ind not in RECO_MAP:
            continue
        reco = RECO_MAP[ind]

        if score < 40:
            priority = "HIGH"
        elif score <= 60:
            priority = "MEDIUM"
        else:
            priority = "OK"

        # Flag if lags behind cluster average
        lags_cluster = ""
        if ind in cl_mean.index and score < cl_mean[ind]:
            lags_cluster = " [lags cluster peers]"

        action = reco["action"] + lags_cluster

        reco_rows.append((did, ind, float(score), priority, action, reco["sdg"], reco["area"]))

        if priority == "HIGH":
            high_priority.append((ind, score, reco["action"], reco["sdg"], lags_cluster))
        elif priority == "MEDIUM":
            medium_priority.append((ind, score, reco["action"], reco["sdg"], lags_cluster))

    district_recos[did] = {
        "name": district_name,
        "cluster": cl_label,
        "high": high_priority,
        "medium": medium_priority,
    }

# ── 3. Priority matrix (31 x 14 numeric) ──────────────────────────────────────
priority_num_map = {"HIGH": 3, "MEDIUM": 2, "OK": 1}
priority_df = pd.DataFrame(index=sorted(pivot.index), columns=indicator_list)
for did in sorted(pivot.index):
    for ind in indicator_list:
        score = pivot.loc[did, ind]
        if score < 40:
            priority_df.loc[did, ind] = 3
        elif score <= 60:
            priority_df.loc[did, ind] = 2
        else:
            priority_df.loc[did, ind] = 1
priority_df = priority_df.astype(int)

# ── 4. Per-district recommendation text already in district_recos ─────────────

# ── 5. SQLITE ─────────────────────────────────────────────────────────────────
cur = conn.cursor()
cur.execute("DROP TABLE IF EXISTS district_recommendations")
cur.execute("""
    CREATE TABLE district_recommendations (
        district_id TEXT,
        indicator_code TEXT,
        normalized_score REAL,
        priority_level TEXT,
        recommendation TEXT,
        sdg_link TEXT,
        area TEXT
    )
""")
cur.executemany("INSERT INTO district_recommendations VALUES (?,?,?,?,?,?,?)", reco_rows)
conn.commit()
print(f"Inserted {len(reco_rows)} rows into district_recommendations")

# ── 6. REPORT ─────────────────────────────────────────────────────────────────
lines = []
lines.append("*** SYNTHETIC DATA ***")
lines.append("=" * 80)
lines.append("IS_19 INFRASENSE RECOMMENDATIONS REPORT")
lines.append("=" * 80)
lines.append("")

for did in sorted(district_recos.keys()):
    info = district_recos[did]
    lines.append(f"\n{'='*70}")
    lines.append(f"District: {info['name']} ({did}) | Cluster: {info['cluster']}")
    lines.append(f"{'='*70}")

    # Up to 5 bullet points (prioritise HIGH, then MEDIUM)
    bullets = []
    for ind, score, action, sdg, lag in info["high"]:
        ind_name = im.loc[im["indicator_code"] == ind, "indicator_name"].values[0]
        bullets.append(f"  [HIGH] {ind_name} (Score: {score:.1f}): {action} [{sdg}]{lag}")
    for ind, score, action, sdg, lag in info["medium"][:max(0, 5 - len(info["high"]))]:
        ind_name = im.loc[im["indicator_code"] == ind, "indicator_name"].values[0]
        bullets.append(f"  [MED]  {ind_name} (Score: {score:.1f}): {action} [{sdg}]{lag}")

    if not bullets:
        lines.append("  • All indicators are performing above 60 — maintain current trajectory.")
    else:
        for b in bullets[:5]:
            lines.append(f"  • {b.strip()}")

report_path = os.path.join(PROJECT_FOLDER, "IS_19_recommendations_report.txt")
with open(report_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print(f"Saved IS_19_recommendations_report.txt ({os.path.getsize(report_path)} bytes)")

# ── 7. PLOT IS_13 — Priority Matrix Heatmap ───────────────────────────────────
district_names_ordered = [dm.loc[dm["district_id"] == d, "district_name"].values[0] for d in priority_df.index]

cmap = ListedColormap(["#4CAF50", "#FFC107", "#F44336"])  # 1=green, 2=amber, 3=red
norm = BoundaryNorm([0.5, 1.5, 2.5, 3.5], cmap.N)

fig, ax = plt.subplots(figsize=(18, 14))
im_plot = ax.imshow(priority_df.values, aspect="auto", cmap=cmap, norm=norm)
ax.set_xticks(range(len(indicator_list)))
ax.set_xticklabels(indicator_list, rotation=45, ha="right", fontsize=9)
ax.set_yticks(range(len(district_names_ordered)))
ax.set_yticklabels(district_names_ordered, fontsize=8)
ax.set_title("IS_13: District Priority Matrix\n(Green=OK, Amber=MEDIUM Priority, Red=HIGH Priority)", fontsize=13, fontweight="bold")

patches = [
    mpatches.Patch(color="#4CAF50", label="OK (score > 60)"),
    mpatches.Patch(color="#FFC107", label="MEDIUM (score 40–60)"),
    mpatches.Patch(color="#F44336", label="HIGH (score < 40)"),
]
ax.legend(handles=patches, loc="upper right", fontsize=9)
plt.tight_layout()
fig.savefig(os.path.join(PROJECT_FOLDER, "IS_13_priority_matrix.png"), dpi=120)
plt.close(fig)
print("Saved IS_13_priority_matrix.png")

conn.close()
print("\nStage 19 complete.")
