"""
InfraSense – Stage 15 : Full Machine Learning Pipeline
=======================================================
Runs on InfraSense_Production.db (must be in the same folder).
Outputs:
  • Plots saved as PNG files in the same folder
  • ML results written back into the SQLite database
  • Console summary of every step
"""

import os, json, warnings
os.environ["MPLCONFIGDIR"] = r"C:\Users\Pavan Kumar P\AppData\Local\Temp"
warnings.filterwarnings("ignore")

import sqlite3
import numpy  as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")          # non-interactive; saves PNGs without a display
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.gridspec import GridSpec
import matplotlib.patches as mpatches

from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
from scipy.spatial.distance  import pdist

from sklearn.preprocessing   import StandardScaler
from sklearn.cluster         import KMeans
from sklearn.decomposition   import PCA
from sklearn.metrics         import silhouette_score, silhouette_samples
from sklearn.impute          import SimpleImputer

# ─── paths ───────────────────────────────────────────────────────────────────
FOLDER  = r"c:\Users\Pavan Kumar P\OneDrive\Desktop\5TH SEM\el"
DB_PATH = os.path.join(FOLDER, "InfraSense_Production.db")

def fig_path(name): return os.path.join(FOLDER, name)

print("=" * 70)
print("InfraSense Stage 15 – ML Pipeline")
print("=" * 70)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1 : PREPARE THE ML DATASET
# ─────────────────────────────────────────────────────────────────────────────
print("\n[1] Loading normalised indicators from SQLite …")

con = sqlite3.connect(DB_PATH)

raw = pd.read_sql("""
    SELECT ni.district_id, dm.district_name, ni.indicator_code, ni.normalized_score
    FROM   normalized_indicators ni
    JOIN   district_master dm ON dm.district_id = ni.district_id
""", con)

# Pivot: one row per district, one column per indicator
df_wide = raw.pivot(index="district_id", columns="indicator_code",
                    values="normalized_score")

# Keep district names for labels
district_names = (raw[["district_id","district_name"]]
                  .drop_duplicates()
                  .set_index("district_id")["district_name"])

print(f"  Shape: {df_wide.shape}  ({df_wide.shape[0]} districts × {df_wide.shape[1]} indicators)")
print(f"  Missing values: {df_wide.isnull().sum().sum()} total")

# 1a. Missing-value report
miss = df_wide.isnull().sum()
miss = miss[miss > 0]
if miss.empty:
    print("  ✓ No missing values – all 31 × 14 cells populated")
else:
    print("  Missing per indicator:")
    for col, cnt in miss.items():
        print(f"    {col}: {cnt}")
    # Impute with column mean (preserves scale)
    imp = SimpleImputer(strategy="mean")
    df_wide[:] = imp.fit_transform(df_wide)
    print("  → Imputed with column mean")

# 1b. Correlation analysis
print("\n[1b] Correlation matrix – highly correlated pairs (|r| ≥ 0.80) …")
corr = df_wide.corr()
high_corr_pairs = []
cols = corr.columns.tolist()
for i in range(len(cols)):
    for j in range(i+1, len(cols)):
        r = corr.iloc[i, j]
        if abs(r) >= 0.80:
            high_corr_pairs.append((cols[i], cols[j], round(r, 3)))
            print(f"  {cols[i]:<35s} ↔ {cols[j]:<35s}  r = {r:.3f}")
if not high_corr_pairs:
    print("  No pairs with |r| ≥ 0.80 found.")

# Save correlation heatmap
fig, ax = plt.subplots(figsize=(12, 10))
short = {c: c.replace("_", "\n") for c in cols}
mat   = corr.values
im    = ax.imshow(mat, cmap="RdYlGn", vmin=-1, vmax=1, aspect="auto")
ax.set_xticks(range(len(cols))); ax.set_xticklabels([short[c] for c in cols], fontsize=7, rotation=45, ha="right")
ax.set_yticks(range(len(cols))); ax.set_yticklabels([short[c] for c in cols], fontsize=7)
for i in range(len(cols)):
    for j in range(len(cols)):
        ax.text(j, i, f"{mat[i,j]:.2f}", ha="center", va="center",
                fontsize=5.5, color="black" if abs(mat[i,j]) < 0.7 else "white")
plt.colorbar(im, ax=ax, fraction=0.03)
ax.set_title("InfraSense – Indicator Correlation Matrix (normalised 0–100 scores)", fontsize=11, pad=12)
plt.tight_layout()
plt.savefig(fig_path("IS_01_correlation_heatmap.png"), dpi=150, bbox_inches="tight")
plt.close()
print("  → Saved IS_01_correlation_heatmap.png")

# Feature matrix for ML (pure numeric, district_id as index)
X_raw = df_wide.values                   # (31, 14)  already in [0, 100]
scaler = StandardScaler()
X      = scaler.fit_transform(X_raw)    # z-score for clustering / PCA

district_ids   = df_wide.index.tolist()
district_labels= [district_names[d] for d in district_ids]

print(f"\n  Feature matrix ready: {X.shape}")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 2 : K-MEANS – ELBOW + SILHOUETTE
# ─────────────────────────────────────────────────────────────────────────────
print("\n[2] K-Means – elbow method and silhouette scores (k = 2 … 8) …")

inertias, sil_scores = [], []
K_RANGE = range(2, 9)

for k in K_RANGE:
    km = KMeans(n_clusters=k, init="k-means++", n_init=50,
                random_state=42, max_iter=500)
    km.fit(X)
    inertias.append(km.inertia_)
    sil_scores.append(silhouette_score(X, km.labels_))
    print(f"  k={k}  inertia={km.inertia_:,.1f}  silhouette={silhouette_score(X, km.labels_):.4f}")

# Elbow + Silhouette combined plot
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

ax1.plot(list(K_RANGE), inertias, "o-", color="#2b7cb7", lw=2)
ax1.set_xlabel("Number of clusters (k)", fontsize=11)
ax1.set_ylabel("Inertia (within-cluster SSE)", fontsize=11)
ax1.set_title("Elbow Method", fontsize=12)
ax1.set_xticks(list(K_RANGE))
ax1.grid(alpha=0.3)

ax2.plot(list(K_RANGE), sil_scores, "s-", color="#e06c3c", lw=2)
ax2.set_xlabel("Number of clusters (k)", fontsize=11)
ax2.set_ylabel("Average silhouette score", fontsize=11)
ax2.set_title("Silhouette Score", fontsize=12)
ax2.set_xticks(list(K_RANGE))
ax2.grid(alpha=0.3)

best_k = list(K_RANGE)[int(np.argmax(sil_scores))]
ax2.axvline(best_k, color="green", ls="--", lw=1.5, label=f"Best k={best_k}")
ax2.legend(fontsize=10)

fig.suptitle("InfraSense – K-Means Cluster Selection", fontsize=13, y=1.01)
plt.tight_layout()
plt.savefig(fig_path("IS_02_kmeans_elbow_silhouette.png"), dpi=150, bbox_inches="tight")
plt.close()
print(f"\n  Best k by silhouette = {best_k}")
print("  → Saved IS_02_kmeans_elbow_silhouette.png")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 3 : FINAL K-MEANS (k=3 and best_k)
# ─────────────────────────────────────────────────────────────────────────────
# Always compute k=3 for interpretability; also run best_k if different
K_FINAL = 3
print(f"\n[3] Final K-Means  k={K_FINAL} …")

km_final = KMeans(n_clusters=K_FINAL, init="k-means++", n_init=100,
                  random_state=42, max_iter=1000)
km_final.fit(X)
labels_km = km_final.labels_

# Order clusters by their mean overall score (descending) for consistency
overall_scores_map = dict(pd.read_sql(
    "SELECT district_id, score FROM district_scores WHERE score_type='overall'", con
).values)
cluster_overall = {c: np.mean([overall_scores_map[district_ids[i]]
                               for i in range(len(district_ids)) if labels_km[i] == c])
                   for c in range(K_FINAL)}
rank_map = {c: r for r, c in enumerate(
    sorted(cluster_overall, key=cluster_overall.get, reverse=True))}
labels_km_ordered = np.array([rank_map[l] for l in labels_km])

CLUSTER_NAMES = {
    0: "High Development",
    1: "Moderate Development",
    2: "Development Gaps"
}
CLUSTER_COLORS = {0: "#2ecc71", 1: "#f39c12", 2: "#e74c3c"}

print(f"  Silhouette score (k={K_FINAL}): {silhouette_score(X, labels_km_ordered):.4f}")

for c in range(K_FINAL):
    members = [district_labels[i] for i in range(len(district_ids))
               if labels_km_ordered[i] == c]
    print(f"  Cluster {c} – {CLUSTER_NAMES[c]} ({len(members)} districts):")
    print(f"    {', '.join(members)}")

# Silhouette per sample plot
sil_vals   = silhouette_samples(X, labels_km_ordered)
fig, ax    = plt.subplots(figsize=(9, 8))
y_lower    = 10
for c in range(K_FINAL):
    vals_c = np.sort(sil_vals[labels_km_ordered == c])
    size_c = len(vals_c)
    y_upper = y_lower + size_c
    ax.barh(np.arange(y_lower, y_upper), vals_c,
            color=CLUSTER_COLORS[c], alpha=0.85, edgecolor="white", height=0.9)
    ax.text(-0.05, y_lower + size_c / 2, CLUSTER_NAMES[c], ha="right",
            va="center", fontsize=8, color=CLUSTER_COLORS[c], fontweight="bold")
    y_lower = y_upper + 5
avg_sil = silhouette_score(X, labels_km_ordered)
ax.axvline(avg_sil, color="black", ls="--", lw=1.5,
           label=f"Mean silhouette = {avg_sil:.3f}")
ax.set_xlabel("Silhouette coefficient", fontsize=11)
ax.set_title(f"K-Means Silhouette Plot  (k={K_FINAL})", fontsize=12)
ax.legend(fontsize=10)
ax.set_yticks([])
ax.grid(axis="x", alpha=0.3)
plt.tight_layout()
plt.savefig(fig_path("IS_03_kmeans_silhouette_plot.png"), dpi=150, bbox_inches="tight")
plt.close()
print("  → Saved IS_03_kmeans_silhouette_plot.png")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 4 : HIERARCHICAL CLUSTERING + DENDROGRAM
# ─────────────────────────────────────────────────────────────────────────────
print("\n[4] Hierarchical clustering …")

Z = linkage(X, method="ward", metric="euclidean")

# Dendrogram
fig, ax = plt.subplots(figsize=(14, 7))
dend = dendrogram(
    Z,
    labels=district_labels,
    leaf_rotation=90,
    leaf_font_size=8.5,
    color_threshold=0.6 * max(Z[:, 2]),
    ax=ax
)
ax.set_title("InfraSense – Hierarchical Clustering Dendrogram\n"
             "(Ward linkage · Euclidean distance on standardised indicators)",
             fontsize=12)
ax.set_ylabel("Distance", fontsize=11)
ax.set_xlabel("District", fontsize=11)
ax.axhline(y=0.6 * max(Z[:, 2]), color="red", ls="--", lw=1.2,
           label="Suggested cut (3 clusters)")
ax.legend(fontsize=9)
ax.grid(axis="y", alpha=0.25)
plt.tight_layout()
plt.savefig(fig_path("IS_04_hierarchical_dendrogram.png"), dpi=150, bbox_inches="tight")
plt.close()
print("  → Saved IS_04_hierarchical_dendrogram.png")

# Hierarchical cluster labels (cut at 3)
labels_hc = fcluster(Z, K_FINAL, criterion="maxclust") - 1  # 0-indexed

# Map hierarchical to same cluster-name ordering (by mean overall score)
hc_overall = {c: np.mean([overall_scores_map[district_ids[i]]
                           for i in range(len(district_ids)) if labels_hc[i] == c])
              for c in range(K_FINAL)}
hc_rank_map = {c: r for r, c in enumerate(
    sorted(hc_overall, key=hc_overall.get, reverse=True))}
labels_hc_ordered = np.array([hc_rank_map[l] for l in labels_hc])

print(f"  Silhouette (hierarchical k={K_FINAL}): {silhouette_score(X, labels_hc_ordered):.4f}")
for c in range(K_FINAL):
    members = [district_labels[i] for i in range(len(district_ids))
               if labels_hc_ordered[i] == c]
    print(f"  HC Cluster {c} – {CLUSTER_NAMES[c]}: {', '.join(members)}")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 5 : PCA
# ─────────────────────────────────────────────────────────────────────────────
print("\n[5] PCA …")

pca      = PCA(n_components=min(14, len(district_ids) - 1), random_state=42)
X_pca    = pca.fit_transform(X)
evr      = pca.explained_variance_ratio_
cumevr   = np.cumsum(evr)

print(f"  PC1 explains {evr[0]*100:.1f}%  |  PC2 explains {evr[1]*100:.1f}%")
print(f"  PC1+PC2 combined: {cumevr[1]*100:.1f}%")
print(f"  PCs needed for 80% variance: {np.searchsorted(cumevr, 0.80) + 1}")

# 5a. Scree plot
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
ax1.bar(range(1, len(evr)+1), evr*100, color="#5b9bd5", alpha=0.85, edgecolor="white")
ax1.plot(range(1, len(evr)+1), cumevr*100, "o-", color="#c0392b", lw=2, label="Cumulative")
ax1.axhline(80, color="green", ls="--", lw=1.3, label="80% threshold")
ax1.set_xlabel("Principal Component", fontsize=11)
ax1.set_ylabel("Explained variance (%)", fontsize=11)
ax1.set_title("Scree Plot", fontsize=12)
ax1.set_xticks(range(1, len(evr)+1))
ax1.legend(fontsize=9)
ax1.grid(axis="y", alpha=0.3)

# 5b. Biplot (PC1 vs PC2)
ax2.set_title("PCA Biplot  (PC1 vs PC2)", fontsize=12)
for i, (x, y) in enumerate(X_pca[:, :2]):
    c = labels_km_ordered[i]
    ax2.scatter(x, y, color=CLUSTER_COLORS[c], s=90, zorder=4,
                edgecolors="white", linewidth=0.5)
    ax2.annotate(district_labels[i], (x, y), fontsize=6.5, ha="center",
                 xytext=(0, 6), textcoords="offset points", color="#333333")

# Loading arrows
loadings = pca.components_.T[:, :2]
scale    = 3.5
feat_short = {
    "road_density":          "Road\ndensity",
    "rural_connectivity":    "Rural\nconn.",
    "pt_coverage":           "PT\ncoverage",
    "internet_penetration":  "Internet",
    "broadband_per1k":       "Broadband",
    "msme_density":          "MSME\ndensity",
    "industrial_emp_rate":   "Ind.\nemp.",
    "startup_rate":          "Startups",
    "patent_rate":           "Patents",
    "renewable_capacity":    "Renew.\nCap.",
    "pm25":                  "PM2.5",
    "forest_cover_pct":      "Forest\ncover",
    "waste_processing_pct":  "Waste\nproc.",
    "literacy_rate":         "Literacy"
}
feat_names = df_wide.columns.tolist()
for fi, (lx, ly) in enumerate(loadings):
    ax2.annotate("",
        xy=(lx * scale, ly * scale), xytext=(0, 0),
        arrowprops=dict(arrowstyle="->", color="#555555", lw=1.0))
    ax2.text(lx * scale * 1.12, ly * scale * 1.12,
             feat_short.get(feat_names[fi], feat_names[fi]),
             ha="center", va="center", fontsize=6, color="#555555")

legend_patches = [mpatches.Patch(color=CLUSTER_COLORS[c], label=CLUSTER_NAMES[c])
                  for c in range(K_FINAL)]
ax2.legend(handles=legend_patches, fontsize=8, loc="lower left")
ax2.set_xlabel(f"PC1  ({evr[0]*100:.1f}%)", fontsize=10)
ax2.set_ylabel(f"PC2  ({evr[1]*100:.1f}%)", fontsize=10)
ax2.axhline(0, color="grey", lw=0.5, ls="--")
ax2.axvline(0, color="grey", lw=0.5, ls="--")
ax2.grid(alpha=0.2)

plt.suptitle("InfraSense – PCA: Dimensionality Reduction", fontsize=13, y=1.01)
plt.tight_layout()
plt.savefig(fig_path("IS_05_pca_scree_biplot.png"), dpi=150, bbox_inches="tight")
plt.close()
print("  → Saved IS_05_pca_scree_biplot.png")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 6 : CLUSTER PROFILES & INTERPRETATION
# ─────────────────────────────────────────────────────────────────────────────
print("\n[6] Cluster profiles …")

df_analysis                 = df_wide.copy()
df_analysis["km_cluster"]   = labels_km_ordered
df_analysis["hc_cluster"]   = labels_hc_ordered
df_analysis["district_name"]= district_labels
df_analysis["overall_score"]= [overall_scores_map[d] for d in district_ids]

# Mean normalised score per indicator per cluster
profile = df_analysis.groupby("km_cluster")[df_wide.columns.tolist()].mean().round(2)
overall_by_cluster = df_analysis.groupby("km_cluster")["overall_score"].mean().round(2)

print("\n  Cluster mean scores (normalised 0–100):")
header = f"  {'Indicator':<35s}" + "".join(f"  C{c}({CLUSTER_NAMES[c][:6]})" for c in range(K_FINAL))
print(header)
for col in df_wide.columns:
    row = f"  {col:<35s}"
    for c in range(K_FINAL):
        row += f"  {profile.loc[c, col]:8.1f}  "
    print(row)
print("  Mean overall score:", overall_by_cluster.to_dict())

# 6a. Radar / spider chart per cluster
from math import pi
categories = df_wide.columns.tolist()
N          = len(categories)
angles     = [n / float(N) * 2 * pi for n in range(N)]
angles    += angles[:1]

fig, axes = plt.subplots(1, K_FINAL, figsize=(6 * K_FINAL, 6),
                         subplot_kw=dict(polar=True))
for c, ax in enumerate(axes):
    vals = profile.loc[c, categories].tolist()
    vals += vals[:1]
    ax.plot(angles, vals, "o-", linewidth=2, color=CLUSTER_COLORS[c])
    ax.fill(angles, vals, alpha=0.25, color=CLUSTER_COLORS[c])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([feat_short.get(f, f) for f in categories],
                       fontsize=7, color="#333")
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(["20", "40", "60", "80", "100"], fontsize=6)
    ax.set_title(f"Cluster {c}\n{CLUSTER_NAMES[c]}\n"
                 f"(n={int((labels_km_ordered==c).sum())},  "
                 f"avg overall={overall_by_cluster[c]:.1f})",
                 fontsize=10, pad=20, color=CLUSTER_COLORS[c], fontweight="bold")
    ax.grid(alpha=0.4)

plt.suptitle("InfraSense – Cluster Radar Profiles  (mean normalised scores)",
             fontsize=13, y=1.01)
plt.tight_layout()
plt.savefig(fig_path("IS_06_cluster_radar.png"), dpi=150, bbox_inches="tight")
plt.close()
print("  → Saved IS_06_cluster_radar.png")

# 6b. Heatmap: district × indicator, sorted by cluster
df_heat = df_analysis.sort_values(["km_cluster", "overall_score"],
                                   ascending=[True, False])
feat_mat = df_heat[df_wide.columns.tolist()].values
dist_ord = df_heat["district_name"].tolist()
clust_ord= df_heat["km_cluster"].tolist()

fig, ax = plt.subplots(figsize=(16, 10))
im = ax.imshow(feat_mat, cmap="RdYlGn", vmin=0, vmax=100, aspect="auto")
ax.set_xticks(range(N))
ax.set_xticklabels([feat_short.get(f, f) for f in df_wide.columns],
                   fontsize=8, rotation=40, ha="right")
ax.set_yticks(range(len(dist_ord)))
ax.set_yticklabels(dist_ord, fontsize=8)
for i in range(len(dist_ord)):
    for j in range(N):
        ax.text(j, i, f"{feat_mat[i,j]:.0f}", ha="center", va="center",
                fontsize=5.5,
                color="black" if 20 < feat_mat[i,j] < 80 else "white")
# Cluster separators
prev = -1
for i, c in enumerate(clust_ord):
    if c != prev:
        if i > 0:
            ax.axhline(i - 0.5, color="navy", lw=2)
        ax.text(-0.7, i, CLUSTER_NAMES[c], va="top", ha="right",
                fontsize=8, color=CLUSTER_COLORS[c], fontweight="bold",
                transform=ax.transData)
        prev = c
plt.colorbar(im, ax=ax, fraction=0.015, label="Normalised score (0–100)")
ax.set_title("InfraSense – District × Indicator Heatmap  (sorted by cluster)",
             fontsize=12, pad=10)
plt.tight_layout()
plt.savefig(fig_path("IS_07_cluster_heatmap.png"), dpi=150, bbox_inches="tight")
plt.close()
print("  → Saved IS_07_cluster_heatmap.png")

# 6c. Bar chart: indicator means by cluster
fig, ax = plt.subplots(figsize=(15, 6))
x       = np.arange(N)
bar_w   = 0.28
for c in range(K_FINAL):
    vals = profile.loc[c, categories].values
    bars = ax.bar(x + (c - 1) * bar_w, vals, bar_w,
                  color=CLUSTER_COLORS[c], alpha=0.85,
                  label=CLUSTER_NAMES[c], edgecolor="white")
ax.set_xticks(x)
ax.set_xticklabels([feat_short.get(f, f) for f in categories],
                   fontsize=8, rotation=35, ha="right")
ax.set_ylabel("Mean normalised score (0–100)", fontsize=11)
ax.set_title("InfraSense – Mean Indicator Score per Cluster", fontsize=12)
ax.legend(fontsize=9)
ax.set_ylim(0, 115)
ax.grid(axis="y", alpha=0.3)
ax.axhline(50, color="grey", ls="--", lw=0.8, alpha=0.6)
plt.tight_layout()
plt.savefig(fig_path("IS_08_cluster_indicator_bars.png"), dpi=150, bbox_inches="tight")
plt.close()
print("  → Saved IS_08_cluster_indicator_bars.png")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 7 : INDICATOR DISTINGUISHABILITY (ANOVA-like variance decomposition)
# ─────────────────────────────────────────────────────────────────────────────
print("\n[7] Indicators that best distinguish clusters …")

from scipy.stats import f_oneway

anova_results = {}
for col in df_wide.columns:
    groups = [df_analysis.loc[df_analysis["km_cluster"] == c, col].values
              for c in range(K_FINAL)]
    f_val, p_val = f_oneway(*groups)
    anova_results[col] = {"F": round(f_val, 3), "p": round(p_val, 4)}

anova_df = pd.DataFrame(anova_results).T.sort_values("F", ascending=False)
print("  One-way ANOVA  (F-statistic ranking):")
for col, row in anova_df.iterrows():
    sig = "***" if row["p"] < 0.001 else ("**" if row["p"] < 0.01
          else ("*" if row["p"] < 0.05 else "  ns"))
    print(f"  {col:<35s}  F={row['F']:7.2f}  p={row['p']:.4f}  {sig}")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 8 : EXPLAINABILITY – CLUSTER PROFILES NARRATIVE
# ─────────────────────────────────────────────────────────────────────────────
print("\n[8] Cluster interpretation …")

for c in range(K_FINAL):
    members = df_analysis[df_analysis["km_cluster"] == c]["district_name"].tolist()
    scores  = profile.loc[c]
    top3    = scores.nlargest(3).index.tolist()
    bot3    = scores.nsmallest(3).index.tolist()
    print(f"\n  ── Cluster {c}: {CLUSTER_NAMES[c]} ──────────────────────────────────")
    print(f"  Districts ({len(members)}): {', '.join(members)}")
    print(f"  Mean overall score: {overall_by_cluster[c]:.2f}")
    print(f"  Strongest indicators: {', '.join(top3)} ({', '.join([str(scores[f].__round__(1)) for f in top3])})")
    print(f"  Weakest  indicators: {', '.join(bot3)} ({', '.join([str(scores[f].__round__(1)) for f in bot3])})")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 9 : SAVE ALL RESULTS BACK TO SQLITE
# ─────────────────────────────────────────────────────────────────────────────
print("\n[9] Writing results to InfraSense_Production.db …")

cur = con.cursor()

# 9a. Clear any previous ML results
cur.execute("DELETE FROM model_explanations")
cur.execute("DELETE FROM district_clusters")
cur.execute("DELETE FROM analysis_runs")
con.commit()

# 9b. Register analysis runs
km_params = json.dumps({
    "n_clusters": K_FINAL, "init": "k-means++", "n_init": 100,
    "random_state": 42, "max_iter": 1000,
    "silhouette": round(float(silhouette_score(X, labels_km_ordered)), 4),
    "inertia": round(float(km_final.inertia_), 2)
})
hc_params = json.dumps({
    "method": "ward", "metric": "euclidean", "n_clusters": K_FINAL,
    "criterion": "maxclust",
    "silhouette": round(float(silhouette_score(X, labels_hc_ordered)), 4)
})
pca_params = json.dumps({
    "n_components": 14,
    "pc1_variance_pct": round(float(evr[0]) * 100, 2),
    "pc2_variance_pct": round(float(evr[1]) * 100, 2),
    "pc1_pc2_cumulative_pct": round(float(cumevr[1]) * 100, 2),
    "pcs_for_80pct": int(np.searchsorted(cumevr, 0.80) + 1)
})

cur.execute(
    "INSERT INTO analysis_runs (run_name, algorithm, parameters, notes) VALUES (?,?,?,?)",
    ("kmeans_k3_v1", "K-Means",
     km_params,
     f"k={K_FINAL} final run; all 14 normalised indicators; silhouette={silhouette_score(X, labels_km_ordered):.4f}")
)
run_id_km = cur.lastrowid

cur.execute(
    "INSERT INTO analysis_runs (run_name, algorithm, parameters, notes) VALUES (?,?,?,?)",
    ("hclust_ward_k3_v1", "Hierarchical (Ward)",
     hc_params,
     f"Ward linkage, Euclidean, cut at k={K_FINAL}; silhouette={silhouette_score(X, labels_hc_ordered):.4f}")
)
run_id_hc = cur.lastrowid

cur.execute(
    "INSERT INTO analysis_runs (run_name, algorithm, parameters, notes) VALUES (?,?,?,?)",
    ("pca_14comp_v1", "PCA",
     pca_params,
     "14 components; PC1+PC2 explain cumulative variance noted in parameters")
)
run_id_pca = cur.lastrowid
con.commit()

# 9c. District cluster assignments
dists_to_centroids = km_final.transform(X)
for i, district_id in enumerate(district_ids):
    c     = int(labels_km_ordered[i])
    dist  = round(float(dists_to_centroids[i, rank_map[labels_km[i]]]), 4)
    sil_v = round(float(sil_vals[i]), 4)
    cur.execute(
        "INSERT INTO district_clusters "
        "(run_id, district_id, cluster_label, cluster_name, distance_to_centroid) "
        "VALUES (?,?,?,?,?)",
        (run_id_km, district_id, c, CLUSTER_NAMES[c], dist)
    )
    # Also store HC assignments (reuse table, different run_id)
    c_hc = int(labels_hc_ordered[i])
    cur.execute(
        "INSERT INTO district_clusters "
        "(run_id, district_id, cluster_label, cluster_name, distance_to_centroid) "
        "VALUES (?,?,?,?,?)",
        (run_id_hc, district_id, c_hc, CLUSTER_NAMES[c_hc], 0.0)
    )

con.commit()

# 9d. Feature importance (ANOVA F-score as proxy for each indicator's ability to separate clusters)
for col, row in anova_df.iterrows():
    cur.execute(
        "INSERT INTO model_explanations "
        "(run_id, district_id, indicator_code, shap_value, feature_importance) "
        "VALUES (?,?,?,?,?)",
        (run_id_km, None, col, None, round(float(row["F"]), 4))
    )

# 9e. PCA loadings stored in model_explanations (indicator_code, shap_value=PC1 loading, feature_importance=PC2 loading)
for fi, feat in enumerate(feat_names):
    cur.execute(
        "INSERT INTO model_explanations "
        "(run_id, district_id, indicator_code, shap_value, feature_importance) "
        "VALUES (?,?,?,?,?)",
        (run_id_pca, None, feat,
         round(float(pca.components_[0, fi]), 5),   # PC1 loading
         round(float(pca.components_[1, fi]), 5))   # PC2 loading
    )

con.commit()

# Verify
cur.execute("SELECT COUNT(*) FROM district_clusters"); print(f"  district_clusters rows: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM model_explanations"); print(f"  model_explanations rows: {cur.fetchone()[0]}")
cur.execute("SELECT run_id, run_name, algorithm FROM analysis_runs")
for r in cur.fetchall():
    print(f"  Run {r[0]}: {r[2]} – {r[1]}")

con.close()

# ─────────────────────────────────────────────────────────────────────────────
# STEP 10 : AGREEMENT BETWEEN K-MEANS AND HIERARCHICAL
# ─────────────────────────────────────────────────────────────────────────────
print("\n[10] K-Means vs Hierarchical agreement …")
agreement = int(np.sum(labels_km_ordered == labels_hc_ordered))
print(f"  Districts with same cluster label: {agreement}/{len(district_ids)}")
disagreements = [(district_labels[i], labels_km_ordered[i], labels_hc_ordered[i])
                 for i in range(len(district_ids))
                 if labels_km_ordered[i] != labels_hc_ordered[i]]
if disagreements:
    print("  Disagreements:")
    for d, km_c, hc_c in disagreements:
        print(f"    {d}: K-Means={CLUSTER_NAMES[km_c]}  |  HC={CLUSTER_NAMES[hc_c]}")
else:
    print("  Perfect agreement between methods.")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 11 : COMPREHENSIVE SUMMARY PLOT
# ─────────────────────────────────────────────────────────────────────────────
print("\n[11] Generating combined summary figure …")

fig = plt.figure(figsize=(18, 14))
gs  = GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.35)

# Panel A : PCA scatter
ax_pca = fig.add_subplot(gs[0, 0])
for i in range(len(district_ids)):
    c = labels_km_ordered[i]
    ax_pca.scatter(X_pca[i, 0], X_pca[i, 1],
                   color=CLUSTER_COLORS[c], s=70, edgecolors="white", lw=0.5, zorder=3)
    ax_pca.annotate(district_labels[i], (X_pca[i, 0], X_pca[i, 1]),
                    fontsize=5.5, ha="center", xytext=(0, 5), textcoords="offset points")
ax_pca.legend(handles=[mpatches.Patch(color=CLUSTER_COLORS[c], label=CLUSTER_NAMES[c])
                        for c in range(K_FINAL)], fontsize=7, loc="lower left")
ax_pca.set_xlabel(f"PC1 ({evr[0]*100:.1f}%)", fontsize=9)
ax_pca.set_ylabel(f"PC2 ({evr[1]*100:.1f}%)", fontsize=9)
ax_pca.set_title("A. PCA District Map", fontsize=10, fontweight="bold")
ax_pca.axhline(0, color="grey", lw=0.4, ls="--"); ax_pca.axvline(0, color="grey", lw=0.4, ls="--")
ax_pca.grid(alpha=0.2)

# Panel B : Elbow
ax_elb = fig.add_subplot(gs[0, 1])
ax_elb.plot(list(K_RANGE), inertias, "o-", color="#2b7cb7", lw=2)
ax_elb.set_xlabel("k", fontsize=9); ax_elb.set_ylabel("Inertia", fontsize=9)
ax_elb.set_title("B. Elbow Method", fontsize=10, fontweight="bold")
ax_elb.set_xticks(list(K_RANGE)); ax_elb.grid(alpha=0.3)

# Panel C : Silhouette by k
ax_sil = fig.add_subplot(gs[0, 2])
ax_sil.plot(list(K_RANGE), sil_scores, "s-", color="#e06c3c", lw=2)
ax_sil.axvline(best_k, color="green", ls="--", lw=1.5)
ax_sil.set_xlabel("k", fontsize=9); ax_sil.set_ylabel("Silhouette", fontsize=9)
ax_sil.set_title(f"C. Silhouette (best k={best_k})", fontsize=10, fontweight="bold")
ax_sil.set_xticks(list(K_RANGE)); ax_sil.grid(alpha=0.3)

# Panel D : Cluster overall score distribution
ax_box = fig.add_subplot(gs[1, 0])
data_box = [df_analysis[df_analysis["km_cluster"] == c]["overall_score"].values
            for c in range(K_FINAL)]
bp = ax_box.boxplot(data_box, patch_artist=True, widths=0.5)
for patch, c in zip(bp["boxes"], range(K_FINAL)):
    patch.set_facecolor(CLUSTER_COLORS[c])
    patch.set_alpha(0.75)
ax_box.set_xticklabels([f"C{c}\n{CLUSTER_NAMES[c][:8]}" for c in range(K_FINAL)], fontsize=8)
ax_box.set_ylabel("Overall development score", fontsize=9)
ax_box.set_title("D. Overall Score by Cluster", fontsize=10, fontweight="bold")
ax_box.grid(axis="y", alpha=0.3)

# Panel E : ANOVA F-scores (top-10)
ax_f = fig.add_subplot(gs[1, 1])
top_anova = anova_df.head(10)
colors_bar = ["#c0392b" if p < 0.05 else "#aaa" for p in top_anova["p"]]
ax_f.barh(range(len(top_anova)), top_anova["F"].values[::-1],
          color=colors_bar[::-1], alpha=0.85, edgecolor="white")
ax_f.set_yticks(range(len(top_anova)))
ax_f.set_yticklabels([feat_short.get(f, f) for f in top_anova.index[::-1]], fontsize=8)
ax_f.set_xlabel("F-statistic (ANOVA)", fontsize=9)
ax_f.set_title("E. Cluster-Distinguishing Indicators", fontsize=10, fontweight="bold")
ax_f.axvline(3, color="green", ls="--", lw=0.9, alpha=0.6)
ax_f.grid(axis="x", alpha=0.3)

# Panel F : PCA loadings bar (PC1 vs PC2)
ax_load = fig.add_subplot(gs[1, 2])
pc1_load = pca.components_[0]
pc2_load = pca.components_[1]
x_load   = np.arange(N)
ax_load.bar(x_load - 0.2, pc1_load, 0.38, label="PC1", color="#5b9bd5", alpha=0.85, edgecolor="white")
ax_load.bar(x_load + 0.2, pc2_load, 0.38, label="PC2", color="#f39c12", alpha=0.85, edgecolor="white")
ax_load.set_xticks(x_load)
ax_load.set_xticklabels([feat_short.get(f, f) for f in feat_names],
                         fontsize=6, rotation=45, ha="right")
ax_load.set_ylabel("Loading", fontsize=9)
ax_load.set_title("F. PCA Loadings (PC1 & PC2)", fontsize=10, fontweight="bold")
ax_load.legend(fontsize=8)
ax_load.axhline(0, color="grey", lw=0.6)
ax_load.grid(axis="y", alpha=0.3)

fig.suptitle("InfraSense – ML Analysis Summary  (Synthetic Data)", fontsize=14, y=1.01)
plt.savefig(fig_path("IS_09_ml_summary.png"), dpi=150, bbox_inches="tight")
plt.close()
print("  → Saved IS_09_ml_summary.png")

# ─────────────────────────────────────────────────────────────────────────────
# FINAL CONSOLE SUMMARY
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("STAGE 15 COMPLETE — SUMMARY")
print("=" * 70)

print(f"\nML Dataset: {X.shape[0]} districts × {X.shape[1]} indicators")
print(f"Missing values handled: {df_wide.isnull().sum().sum()} (all zero after any imputation)")
print(f"High correlations (|r|≥0.80): {len(high_corr_pairs)}")
print(f"\nK-Means (k={K_FINAL}):  silhouette = {silhouette_score(X, labels_km_ordered):.4f}")
print(f"Hierarchical (k={K_FINAL}): silhouette = {silhouette_score(X, labels_hc_ordered):.4f}")
print(f"Agreement between methods: {agreement}/{len(district_ids)} districts")
print(f"\nPCA: PC1={evr[0]*100:.1f}%  PC2={evr[1]*100:.1f}%  combined={cumevr[1]*100:.1f}%")
print(f"PCs needed for 80% variance: {np.searchsorted(cumevr, 0.80)+1}")

print("\nCluster assignments (K-Means):")
for c in range(K_FINAL):
    members = df_analysis[df_analysis["km_cluster"] == c]["district_name"].tolist()
    print(f"  [{CLUSTER_NAMES[c]}] ({len(members)} districts): {', '.join(members)}")

print("\nTop distinguishing indicators (ANOVA F-statistic):")
for col, row in anova_df.head(5).iterrows():
    sig = "***" if row["p"] < 0.001 else ("**" if row["p"] < 0.01 else ("*" if row["p"] < 0.05 else "ns"))
    print(f"  {col:<35s} F={row['F']:7.2f}  {sig}")

print("\nPlots saved:")
plots = [
    "IS_01_correlation_heatmap.png",
    "IS_02_kmeans_elbow_silhouette.png",
    "IS_03_kmeans_silhouette_plot.png",
    "IS_04_hierarchical_dendrogram.png",
    "IS_05_pca_scree_biplot.png",
    "IS_06_cluster_radar.png",
    "IS_07_cluster_heatmap.png",
    "IS_08_cluster_indicator_bars.png",
    "IS_09_ml_summary.png",
]
for p in plots:
    exists = os.path.exists(fig_path(p))
    print(f"  {'✓' if exists else '✗'} {p}")

print("\nSQLite tables updated: analysis_runs, district_clusters, model_explanations")
print("=" * 70)
