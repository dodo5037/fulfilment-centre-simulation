"""Discrete-event simulation of an order fulfilment line: Pick -> Pack -> Sort/Ship.

Each order:
  1. arrives (Poisson process),
  2. waits for a free picker, gets picked,
  3. waits for a free packer, gets packed,
  4. waits for a free sorter, gets sorted to an outbound lane, and leaves.

Every station is a SimPy Resource with N identical workers and a first-come-first-served queue.
Service times are lognormal (always positive, right-skewed like real task times) with the
mean from config and a common coefficient of variation.

One call to run_replication() simulates warm-up + one measured shift and returns KPIs:
  throughput (orders/h, units/h), units per labour hour (UPH), cycle time (mean, p95),
  average queue length and utilisation per station, average work-in-process (WIP), and the
  value-added ratio (time being worked on / total time in the system, a lean metric).
"""
from __future__ import annotations
import math
import numpy as np
import simpy
from config import Params

STATIONS = ("pick", "pack", "sort")


def lognormal(rng: np.random.Generator, mean: float, cv: float) -> float:
    """Draw a lognormal value with the given mean and coefficient of variation."""
    sigma2 = math.log(1 + cv ** 2)
    mu = math.log(mean) - sigma2 / 2
    return float(rng.lognormal(mu, math.sqrt(sigma2)))


def mean_service_time(p: Params, station: str) -> float:
    """Expected service time per order at a station (used for the analytic check)."""
    units = 1 + p.extra_units_mean
    return {"pick": p.pick_fixed + p.pick_per_unit * units,
            "pack": p.pack_fixed + p.pack_per_unit * units,
            "sort": p.sort_fixed}[station]


def theoretical_utilisation(p: Params) -> dict[str, float]:
    """Offered load rho = arrival rate x mean service time / workers (queueing theory)."""
    lam = p.orders_per_hour / 60
    servers = {"pick": p.pickers, "pack": p.packers, "sort": p.sorters}
    return {s: lam * mean_service_time(p, s) / servers[s] for s in STATIONS}


def run_replication(p: Params, seed: int) -> dict:
    rng = np.random.default_rng(seed)
    env = simpy.Environment()
    res = {"pick": simpy.Resource(env, p.pickers),
           "pack": simpy.Resource(env, p.packers),
           "sort": simpy.Resource(env, p.sorters)}
    t0, t1 = p.warmup_min, p.warmup_min + p.measure_min
    done = []                       # (arrival_time, finish_time, units, work_time)
    wip = {"n": 0}
    samples = {f"q_{s}": [] for s in STATIONS} | {f"busy_{s}": [] for s in STATIONS} | {"wip": []}

    def service(station: str, units: int) -> float:
        if station == "pick":
            m = p.pick_fixed + p.pick_per_unit * units
        elif station == "pack":
            m = p.pack_fixed + p.pack_per_unit * units
        else:
            m = p.sort_fixed
        return lognormal(rng, m, p.service_cv)

    def order(units: int):
        arrive = env.now
        work = 0.0
        wip["n"] += 1
        for s in STATIONS:
            with res[s].request() as req:
                yield req
                d = service(s, units)
                work += d
                yield env.timeout(d)
        wip["n"] -= 1
        done.append((arrive, env.now, units, work))

    def arrivals():
        rate = p.orders_per_hour / 60
        while True:
            yield env.timeout(rng.exponential(1 / rate))
            env.process(order(1 + int(rng.poisson(p.extra_units_mean))))

    def sampler():
        yield env.timeout(t0)
        while env.now < t1:
            for s in STATIONS:
                samples[f"q_{s}"].append(len(res[s].queue))
                samples[f"busy_{s}"].append(res[s].count / res[s].capacity)
            samples["wip"].append(wip["n"])
            yield env.timeout(p.sample_every_min)

    env.process(arrivals())
    env.process(sampler())
    env.run(until=t1)

    hours = p.measure_min / 60
    finished = [r for r in done if t0 <= r[1] < t1]
    cycle = np.array([f - a for a, f, _, _ in finished]) if finished else np.array([np.nan])
    work = np.array([w for *_, w in finished]) if finished else np.array([np.nan])
    units = sum(u for _, _, u, _ in finished)
    out = {
        "orders_per_h": len(finished) / hours,
        "units_per_h": units / hours,
        "uph_per_worker": units / hours / p.headcount,
        "cycle_mean_min": float(np.nanmean(cycle)),
        "cycle_p95_min": float(np.nanpercentile(cycle, 95)),
        "work_mean_min": float(np.nanmean(work)),
        "value_added_ratio": float(np.nanmean(work) / np.nanmean(cycle)),
        "wip_avg": float(np.mean(samples["wip"])),
        "orders_open_at_end": wip["n"],
    }
    for s in STATIONS:
        out[f"queue_{s}"] = float(np.mean(samples[f"q_{s}"]))
        out[f"util_{s}"] = float(np.mean(samples[f"busy_{s}"]))
    # Little's Law check: WIP = throughput (per minute) x time in system
    out["littles_law_wip"] = out["orders_per_h"] / 60 * out["cycle_mean_min"]
    return out
