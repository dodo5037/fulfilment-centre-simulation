"""Charts for the README and the A3 report (reads the tables written by run_experiments.py)."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
T, C = ROOT / "outputs" / "tables", ROOT / "outputs" / "charts"
C.mkdir(parents=True, exist_ok=True)
NAVY, TEAL, PINK, GREY, AMBER = "#1f3864", "#10b981", "#f43f5e", "#9aa5b1", "#f59e0b"
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 150})

normal = pd.read_csv(T / "summary_normal.csv")
peak = pd.read_csv(T / "summary_peak.csv")
labels = [s.split(". ", 1)[0] + ". " + s.split(". ", 1)[1].split(" (")[0] for s in normal["scenario"]]

# 1. Cycle time, normal vs peak
x = np.arange(len(normal)); w = 0.38
fig, ax = plt.subplots(figsize=(10, 4.8))
ax.bar(x - w / 2, normal["cycle_mean_min"], w, yerr=normal["cycle_mean_min_ci"], color=TEAL, label="Normal day (120 orders/h)", capsize=3)
ax.bar(x + w / 2, peak["cycle_mean_min"], w, yerr=peak["cycle_mean_min_ci"], color=PINK, label="Peak day (144 orders/h)", capsize=3)
for i, (n, p) in enumerate(zip(normal["cycle_mean_min"], peak["cycle_mean_min"])):
    ax.text(i - w / 2, n + 1, f"{n:.1f}", ha="center", fontsize=8)
    ax.text(i + w / 2, p + 1, f"{p:.1f}", ha="center", fontsize=8)
ax.set_xticks(x, labels, rotation=12, ha="right")
ax.set_ylabel("Average order cycle time (min)")
ax.set_title("Order cycle time by scenario (30 simulated shifts each, 95% CI)")
ax.legend(frameon=False)
fig.tight_layout(); fig.savefig(C / "01_cycle_time.png"); plt.close(fig)

# 2. Utilisation heatmap: where the bottleneck sits
util = normal[["util_pick", "util_pack", "util_sort"]].values
fig, ax = plt.subplots(figsize=(6.5, 4.2))
im = ax.imshow(util, cmap="RdYlGn_r", vmin=0.4, vmax=1.0, aspect="auto")
ax.set_xticks(range(3), ["Pick", "Pack", "Sort/Ship"]); ax.set_yticks(range(len(labels)), labels)
for i in range(util.shape[0]):
    for j in range(3):
        ax.text(j, i, f"{util[i, j]:.0%}", ha="center", va="center", fontsize=9)
ax.set_title("Station utilisation, normal day (red = bottleneck)")
fig.colorbar(im, ax=ax, fraction=0.04)
fig.tight_layout(); fig.savefig(C / "02_utilisation_heatmap.png"); plt.close(fig)

# 3. Work vs waiting per order (lean view)
raw = pd.read_csv(T / "replications_normal.csv")
g = raw.groupby("scenario", sort=False).agg(cycle=("cycle_mean_min", "mean"), work=("work_mean_min", "mean"))
g["va"] = g["work"] / g["cycle"]
work = g["work"]; wait = g["cycle"] - work
fig, ax = plt.subplots(figsize=(9, 4.2))
ax.barh(labels, work.values, color=TEAL, label="Being worked on (value-added)")
ax.barh(labels, wait.values, left=work.values, color=GREY, label="Waiting in queues (waste)")
for i, (wk, wt, r) in enumerate(zip(work, wait, g["va"])):
    ax.text(wk + wt + 0.1, i, f"{r:.0%} value-added", va="center", fontsize=8)
ax.invert_yaxis(); ax.set_xlabel("Minutes per order (normal day)"); ax.set_xlim(0, (work + wait).max() * 1.35)
ax.set_title("Where an order's time goes")
ax.legend(frameon=False, loc="lower right", fontsize=8)
fig.tight_layout(); fig.savefig(C / "03_work_vs_wait.png"); plt.close(fig)

# 4. Productivity vs speed trade-off
fig, ax = plt.subplots(figsize=(7, 4.5))
for i, r in normal.iterrows():
    ax.scatter(r["uph_per_worker"], r["cycle_p95_min"], s=90, color=TEAL if r["headcount"] == 11 else AMBER, zorder=3)
    ax.annotate(labels[i].split(". ")[0], (r["uph_per_worker"], r["cycle_p95_min"]), xytext=(6, 4), textcoords="offset points")
ax.set_xlabel("Units per labour hour (higher = more productive)"); ax.set_ylabel("95th-percentile cycle time (min, lower = faster)")
ax.set_title("Speed vs productivity (teal = 11 staff, amber = 12 staff)")
fig.tight_layout(); fig.savefig(C / "04_tradeoff.png"); plt.close(fig)
print("charts:", sorted(p.name for p in C.glob("*.png")))
