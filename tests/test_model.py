"""Validation tests: the simulation must agree with queueing theory where theory has an answer."""
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from config import BASE, SCENARIOS  # noqa: E402
from model import run_replication, theoretical_utilisation, lognormal, STATIONS  # noqa: E402


def test_same_seed_gives_same_result():
    assert run_replication(BASE, 7) == run_replication(BASE, 7)


def test_lognormal_has_requested_mean_and_cv():
    rng = np.random.default_rng(0)
    x = np.array([lognormal(rng, 2.0, 0.3) for _ in range(200_000)])
    assert x.mean() == pytest.approx(2.0, rel=0.01)
    assert x.std() / x.mean() == pytest.approx(0.3, rel=0.02)


@pytest.mark.parametrize("p", SCENARIOS, ids=lambda p: p.name[:2])
def test_littles_law_holds(p):
    """L = lambda x W: average WIP must equal throughput x average time in system."""
    r = np.mean([[run_replication(p, s)["wip_avg"], run_replication(p, s)["littles_law_wip"]] for s in range(5)], axis=0)
    assert r[0] == pytest.approx(r[1], rel=0.05)


@pytest.mark.parametrize("p", SCENARIOS, ids=lambda p: p.name[:2])
def test_utilisation_matches_theory(p):
    """Busy fraction of each station must match rho = arrival rate x mean service time / servers."""
    theory = theoretical_utilisation(p)
    sims = [run_replication(p, s) for s in range(10)]
    for st in STATIONS:
        assert np.mean([r[f"util_{st}"] for r in sims]) == pytest.approx(theory[st], abs=0.03)


def test_throughput_matches_demand_when_stable():
    """A stable line (all rho < 1) ships what it receives: ~120 orders/h."""
    sims = [run_replication(BASE, s) for s in range(10)]
    assert np.mean([r["orders_per_h"] for r in sims]) == pytest.approx(BASE.orders_per_hour, rel=0.03)


def test_overloaded_station_builds_a_queue():
    """Above 100% load the queue must grow: give pack 2 workers (rho > 1)."""
    over = replace(BASE, packers=2)
    assert theoretical_utilisation(over)["pack"] > 1
    assert run_replication(over, 0)["queue_pack"] > run_replication(BASE, 0)["queue_pack"] * 3


def test_more_capacity_never_hurts_cycle_time():
    base = np.mean([run_replication(BASE, s)["cycle_mean_min"] for s in range(10)])
    more = np.mean([run_replication(replace(BASE, packers=4), s)["cycle_mean_min"] for s in range(10)])
    assert more < base
