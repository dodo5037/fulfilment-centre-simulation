"""Run every scenario 30 times (different random seeds) and report mean +/- 95% confidence interval.

Why replications: one simulated shift is one random sample. Running 30 independent shifts
and reporting a confidence interval shows whether a difference between scenarios is real
or just luck. Scenarios share the same seeds (common random numbers), which makes the
comparison fairer.
"""
from pathlib import Path
import numpy as np
import pandas as pd
from config import SCENARIOS, PEAK, REPLICATIONS
from model import run_replication, theoretical_utilisation, STATIONS

ROOT = Path(__file__).resolve().parents[1]
T = ROOT / "outputs" / "tables"
T.mkdir(parents=True, exist_ok=True)
T_CRIT_29 = 2.045  # two-sided 95% t value for 29 degrees of freedom

KPIS = ["orders_per_h", "units_per_h", "uph_per_worker", "cycle_mean_min", "cycle_p95_min",
        "work_mean_min", "value_added_ratio", "wip_avg", "littles_law_wip", "orders_open_at_end"] + \
       [f"queue_{s}" for s in STATIONS] + [f"util_{s}" for s in STATIONS]


def run(scenarios, tag):
    raw = []
    for p in scenarios:
        for seed in range(REPLICATIONS):
            r = run_replication(p, seed)
            r.update(scenario=p.name, seed=seed, headcount=p.headcount)
            raw.append(r)
    raw = pd.DataFrame(raw)
    raw.to_csv(T / f"replications_{tag}.csv", index=False)

    rows = []
    for name, g in raw.groupby("scenario", sort=False):
        row = {"scenario": name, "headcount": int(g["headcount"].iat[0])}
        for k in KPIS:
            m, sd = g[k].mean(), g[k].std(ddof=1)
            row[k] = m
            row[k + "_ci"] = T_CRIT_29 * sd / np.sqrt(len(g))
        # Value-added ratio = average work time / average cycle time (ratio of means, not mean of ratios)
        row["value_added_ratio"] = row["work_mean_min"] / row["cycle_mean_min"]
        p = next(s for s in scenarios if s.name == name)
        for s, rho in theoretical_utilisation(p).items():
            row[f"theory_util_{s}"] = rho
        util = {s: row[f"util_{s}"] for s in STATIONS}
        row["bottleneck"] = max(util, key=util.get)
        rows.append(row)
    summary = pd.DataFrame(rows)
    summary.to_csv(T / f"summary_{tag}.csv", index=False)
    return summary


def fmt(summary):
    cols = {"headcount": "Staff", "units_per_h": "Units/h", "uph_per_worker": "UPH/worker",
            "cycle_mean_min": "Cycle mean (min)", "cycle_p95_min": "Cycle p95 (min)",
            "value_added_ratio": "Value-added %", "bottleneck": "Bottleneck"}
    out = summary[["scenario"] + list(cols)].rename(columns=cols).set_index("scenario")
    for c, k in [("Units/h", "units_per_h"), ("Cycle mean (min)", "cycle_mean_min"), ("Cycle p95 (min)", "cycle_p95_min")]:
        out[c] = [f"{m:.1f} ± {ci:.1f}" for m, ci in zip(summary[k], summary[k + "_ci"])]
    out["UPH/worker"] = summary["uph_per_worker"].round(1).values
    out["Value-added %"] = (summary["value_added_ratio"] * 100).round(0).astype(int).astype(str).values
    return out


if __name__ == "__main__":
    normal = run(SCENARIOS, "normal")
    peak = run(PEAK, "peak")
    pd.set_option("display.width", 200)
    print("NORMAL DEMAND (120 orders/h), 30 shifts each, mean ± 95% CI\n")
    print(fmt(normal).to_string())
    print("\nPEAK DEMAND (144 orders/h)\n")
    print(fmt(peak).to_string())
    print("\nUtilisation, simulated vs theory (normal demand):")
    for _, r in normal.iterrows():
        print(f"  {r['scenario']:<42} " + "  ".join(f"{s}: {r[f'util_{s}']:.2f}/{r[f'theory_util_{s}']:.2f}" for s in STATIONS))
    print("\nLittle's Law (normal): measured WIP vs throughput x cycle time")
    for _, r in normal.iterrows():
        print(f"  {r['scenario']:<42} {r['wip_avg']:.2f} vs {r['littles_law_wip']:.2f}")
