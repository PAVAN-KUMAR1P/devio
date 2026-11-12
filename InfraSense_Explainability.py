import os, warnings
os.environ["MPLCONFIGDIR"] = r"C:\Users\Pavan Kumar P\AppData\Local\Temp"
warnings.filterwarnings("ignore")
import matplotlib; matplotlib.use("Agg")

import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import TwoSlopeNorm

PROJECT_FOLDER = r"c:\Users\Pavan Kumar P\OneDrive\Desktop\5TH SEM\el"
DB_PATH = os.path.join(PROJECT_FOLDER, "InfraSense_Production.db")

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

# Pivot: rows=district, cols=indicator
pivot = ni.pivot(index="district_id", columns="indicator_code", values="normalized_score")

# Karnataka mean per indicator
ka_mean = pivot.mean()  # Series indexed by indicator_code

# Gap matrix
gap = pivot.subtract(ka_mean, axis=1)

# ── Dimension map ──────────────────────────────────────────────────────────────
dim_map = dict(zip(im["indicator_code"], im["dimension"]))
# Map indicator -> dimension
indicator_list = pivot.columns.tolist()

# ── 1. DISTRICT-LEVEL EXPLANATION ─────────────────────────────────────────────
district_explanations = []  # for SQLite

district_summaries = {}

for did in pivot.index:
    row = pivot.loc[did]
    gap_row = gap.loc[did]
    district_name = dm.loc[dm["district_id"] == did, "district_name"].values[0]

    # Rank all 14 indicators by score (highest = rank 1)
    ranked = row.rank(ascending=False).astype(int)

    # Top 3 strongest (highest score)
    top3 = row.nlargest(3).index.tolist()
    # Top 3 weakest (lowest score)
    bot3 = row.nsmallest(3).index.tolist()

    # Dimension that is dragging score down most: mean gap per dimension, pick most negative
    dim_gaps = {}
    for ind in indicator_list:
        d = dim_map.get(ind, "Unknown")
        dim_gaps.setdefault(d, []).append(gap_row[ind])
    dim_avg_gap = {d: np.mean(v) for d, v in dim_gaps.items()}
    lagging_dim = min(dim_avg_gap, key=dim_avg_gap.get)

    # Cluster
    cluster_row = ds[ds["district_id"] == did]
    cluster_label = int(cluster_row["cluster_label"].values[0]) if len(cluster_row) > 0 else -1
    cluster_name  = cluster_row["cluster_name"].values[0] if len(cluster_row) > 0 else "Unknown"

    district_summaries[did] = {
        "name": district_name,
        "top3": top3,
        "bot3": bot3,
        "lagging_dim": lagging_dim,
        "cluster_label": cluster_label,
        "cluster_name": cluster_name,
        "dim_avg_gap": dim_avg_gap,
    }

    # Rows for SQLite
    for ind in indicator_list:
        score = row[ind]
        mean  = ka_mean[ind]
        g     = gap_row[ind]
        rnk   = int(ranked[ind])
        is_str = 1 if ind in top3 else 0
        is_wk  = 1 if ind in bot3 else 0
        district_explanations.append((did, ind, float(score), float(mean), float(g), rnk, is_str, is_wk))

# ── 2. CLUSTER EXPLANATION ─────────────────────────────────────────────────────
cluster_narratives = {}
cluster_profiles = {}

for cl_label in sorted(ds["cluster_label"].unique()):
    cl_name = ds[ds["cluster_label"] == cl_label]["cluster_name"].values[0]
    cl_districts = ds[ds["cluster_label"] == cl_label]["district_id"].tolist()
    cl_pivot = pivot.loc[[d for d in cl_districts if d in pivot.index]]
    cl_mean = cl_pivot.mean()
    cluster_profiles[cl_label] = {"name": cl_name, "mean": cl_mean, "districts": cl_districts}

    # Distinguishing features: >15 pts above or below Karnataka mean
    above = [ind for ind in indicator_list if cl_mean[ind] - ka_mean[ind] > 15]
    below = [ind for ind in indicator_list if cl_mean[ind] - ka_mean[ind] < -15]

    n_districts = len(cl_districts)
    overall_mean = cl_mean.mean()

    # Build narrative
    above_names = [im.loc[im["indicator_code"] == ind, "indicator_name"].values[0] for ind in above] if above else []
    below_names = [im.loc[im["indicator_code"] == ind, "indicator_name"].values[0] for ind in below] if below else []

    para = (
        f"Cluster {cl_label} — '{cl_name}' comprises {n_districts} district(s) with "
        f"an average composite score of {overall_mean:.1f}/100. "
    )
    if above_names:
        para += f"These districts perform notably above the Karnataka average on: {', '.join(above_names)}. "
    if below_names:
        para += f"However, they lag significantly behind on: {', '.join(below_names)}. "
    if not above_names and not below_names:
        para += "This cluster shows broadly average performance across most indicators. "
    para += (
        f"Policy focus should address the weakest dimensions to elevate overall development outcomes. "
        f"Targeted interventions in the lagging areas can help this cluster converge towards "
        f"the state's best performers."
    )
    cluster_narratives[cl_label] = {"name": cl_name, "narrative": para, "above": above_names, "below": below_names}

# ── 3. INDICATOR CONTRIBUTION ANALYSIS ────────────────────────────────────────
indicator_std = pivot.std().sort_values(ascending=False)

# ── 4. PLOTS ──────────────────────────────────────────────────────────────────

# Plot 1: IS_10 — District Gap Heatmap (31 x 14)
fig, ax = plt.subplots(figsize=(18, 14))
gap_ordered = gap.loc[sorted(gap.index)]
district_names_ordered = [dm.loc[dm["district_id"] == d, "district_name"].values[0] for d in gap_ordered.index]

# Use TwoSlopeNorm centred at 0
vmax = max(abs(gap_ordered.values.max()), abs(gap_ordered.values.min()))
norm = TwoSlopeNorm(vmin=-vmax, vcenter=0, vmax=vmax)
im_plot = ax.imshow(gap_ordered.values, aspect="auto", cmap="RdYlGn", norm=norm)
ax.set_xticks(range(len(indicator_list)))
ax.set_xticklabels(gap_ordered.columns.tolist(), rotation=45, ha="right", fontsize=9)
ax.set_yticks(range(len(district_names_ordered)))
ax.set_yticklabels(district_names_ordered, fontsize=8)
ax.set_title("IS_10: District Gap from Karnataka Mean\n(Green = Above Mean, Red = Below Mean)", fontsize=13, fontweight="bold")
plt.colorbar(im_plot, ax=ax, label="Gap (District Score – Karnataka Mean)")
plt.tight_layout()
fig.savefig(os.path.join(PROJECT_FOLDER, "IS_10_district_gap_heatmap.png"), dpi=120)
plt.close(fig)
print("Saved IS_10_district_gap_heatmap.png")

# Plot 2: IS_11 — Cluster Profiles Comparison (dimension level)
# Compute dimension mean per cluster and Karnataka mean
dimensions = sorted(set(dim_map.values()))
ka_dim_means = {}
for dim in dimensions:
    inds = [i for i in indicator_list if dim_map.get(i) == dim]
    ka_dim_means[dim] = pivot[inds].mean().mean()

cluster_dim_means = {}
for cl_label, info in cluster_profiles.items():
    cl_pivot = pivot.loc[[d for d in info["districts"] if d in pivot.index]]
    dim_vals = {}
    for dim in dimensions:
        inds = [i for i in indicator_list if dim_map.get(i) == dim]
        dim_vals[dim] = cl_pivot[inds].mean().mean()
    cluster_dim_means[cl_label] = dim_vals

n_dims = len(dimensions)
x = np.arange(n_dims)
n_clusters = len(cluster_profiles)
width = 0.2
colors = ["#2196F3", "#4CAF50", "#FF9800", "#9C27B0"]

fig, ax = plt.subplots(figsize=(14, 7))
for i, (cl_label, dim_vals) in enumerate(cluster_dim_means.items()):
    vals = [dim_vals[d] for d in dimensions]
    cl_name = cluster_profiles[cl_label]["name"]
    bars = ax.bar(x + (i - n_clusters/2 + 0.5) * width, vals, width, label=f"Cluster {cl_label}: {cl_name}", color=colors[i % len(colors)], alpha=0.85)

# Karnataka mean as a line
ka_vals = [ka_dim_means[d] for d in dimensions]
ax.plot(x, ka_vals, "k--o", linewidth=2, label="Karnataka Average", zorder=5)
ax.set_xticks(x)
ax.set_xticklabels([d.replace(" & ", "\n& ") for d in dimensions], fontsize=10)
ax.set_ylabel("Mean Score (0–100)")
ax.set_title("IS_11: Cluster Dimension Profiles vs Karnataka Average", fontsize=13, fontweight="bold")
ax.legend(loc="upper right", fontsize=9)
ax.set_ylim(0, 100)
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
fig.savefig(os.path.join(PROJECT_FOLDER, "IS_11_cluster_profiles_comparison.png"), dpi=120)
plt.close(fig)
print("Saved IS_11_cluster_profiles_comparison.png")

# Plot 3: IS_12 — Indicator Variance Ranking (horizontal bar)
fig, ax = plt.subplots(figsize=(10, 8))
ind_std_sorted = indicator_std.sort_values()
colors_bar = plt.cm.plasma(np.linspace(0.2, 0.9, len(ind_std_sorted)))
bars = ax.barh(ind_std_sorted.index.tolist(), ind_std_sorted.values, color=colors_bar)
ax.set_xlabel("Standard Deviation of Normalized Scores Across Districts")
ax.set_title("IS_12: Indicator Contribution to Inter-District Variation\n(Ranked by Std Dev)", fontsize=12, fontweight="bold")
for bar, val in zip(bars, ind_std_sorted.values):
    ax.text(val + 0.3, bar.get_y() + bar.get_height()/2, f"{val:.2f}", va="center", fontsize=8)
ax.grid(axis="x", alpha=0.3)
plt.tight_layout()
fig.savefig(os.path.join(PROJECT_FOLDER, "IS_12_indicator_variance_ranking.png"), dpi=120)
plt.close(fig)
print("Saved IS_12_indicator_variance_ranking.png")

# ── 5. SAVE TO SQLITE ─────────────────────────────────────────────────────────
cur = conn.cursor()
cur.execute("DROP TABLE IF EXISTS district_explanations")
cur.execute("""
    CREATE TABLE district_explanations (
        district_id TEXT,
        indicator_code TEXT,
        normalized_score REAL,
        karnataka_mean REAL,
        gap REAL,
        rank_in_state INTEGER,
        is_strength INTEGER,
        is_weakness INTEGER
    )
""")
cur.executemany(
    "INSERT INTO district_explanations VALUES (?,?,?,?,?,?,?,?)",
    district_explanations
)
conn.commit()
print(f"Inserted {len(district_explanations)} rows into district_explanations")

# ── 6. PLAIN-TEXT REPORT ──────────────────────────────────────────────────────
lines = []
lines.append("*** SYNTHETIC DATA ***")
lines.append("=" * 80)
lines.append("IS_18 INFRASENSE EXPLAINABILITY REPORT")
lines.append("=" * 80)
lines.append("")

# (a) Per-district summary
lines.append("SECTION A: PER-DISTRICT SUMMARY")
lines.append("-" * 60)
for did in sorted(district_summaries.keys()):
    info = district_summaries[did]
    top3_names = [im.loc[im["indicator_code"] == i, "indicator_name"].values[0] for i in info["top3"]]
    bot3_names = [im.loc[im["indicator_code"] == i, "indicator_name"].values[0] for i in info["bot3"]]
    lines.append(f"\nDistrict: {info['name']} ({did})")
    lines.append(f"  Cluster: {info['cluster_label']} — {info['cluster_name']}")
    lines.append(f"  Top 3 Strongest Indicators : {', '.join(top3_names)}")
    lines.append(f"  Top 3 Weakest   Indicators : {', '.join(bot3_names)}")
    lines.append(f"  Most Lagging Dimension     : {info['lagging_dim']}")
    dim_gap_str = " | ".join([f"{d}: {v:+.1f}" for d, v in sorted(info["dim_avg_gap"].items())])
    lines.append(f"  Dimension Gap vs KA Mean   : {dim_gap_str}")

lines.append("")
lines.append("=" * 80)

# (b) Cluster profiles narrative
lines.append("")
lines.append("SECTION B: CLUSTER PROFILES NARRATIVE")
lines.append("-" * 60)
for cl_label in sorted(cluster_narratives.keys()):
    cn = cluster_narratives[cl_label]
    lines.append(f"\nCluster {cl_label} — {cn['name']}")
    lines.append(cn["narrative"])
    if cn["above"]:
        lines.append(f"  Distinguishing (above KA mean >15 pts): {', '.join(cn['above'])}")
    if cn["below"]:
        lines.append(f"  Distinguishing (below KA mean >15 pts): {', '.join(cn['below'])}")

lines.append("")
lines.append("=" * 80)

# (c) Top 5 most regionally variable indicators
lines.append("")
lines.append("SECTION C: TOP 5 MOST REGIONALLY VARIABLE INDICATORS")
lines.append("-" * 60)
top5_var = indicator_std.head(5)
for rank, (ind_code, std_val) in enumerate(top5_var.items(), 1):
    ind_name = im.loc[im["indicator_code"] == ind_code, "indicator_name"].values[0]
    dim = dim_map.get(ind_code, "Unknown")
    lines.append(f"  {rank}. {ind_name} ({ind_code}) — Std Dev: {std_val:.2f} — Dimension: {dim}")

lines.append("")
lines.append("=" * 80)
lines.append("END OF REPORT")

report_path = os.path.join(PROJECT_FOLDER, "IS_18_explainability_report.txt")
with open(report_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print(f"Saved IS_18_explainability_report.txt ({os.path.getsize(report_path)} bytes)")

conn.close()
print("\nStage 18 complete.")
