"""Model parameters and scenarios.

IMPORTANT: these are ILLUSTRATIVE ASSUMPTIONS for a small e-commerce fulfilment line,
not data from any real company. They are chosen so the baseline has a realistic
imbalance (one overloaded station) that the analysis then fixes. Change them here
and every script picks them up.

Time unit: minutes.
"""
from dataclasses import dataclass, field, replace

@dataclass(frozen=True)
class Params:
    name: str = "A. Baseline"
    # Demand
    orders_per_hour: float = 120.0          # Poisson arrivals
    extra_units_mean: float = 1.5           # units per order = 1 + Poisson(1.5) -> mean 2.5
    # Staffing (servers per station)
    pickers: int = 6
    packers: int = 3
    sorters: int = 2
    # Service times: fixed part per order + part per unit (means, minutes)
    pick_fixed: float = 1.2                 # walk to the zone, scan tote
    pick_per_unit: float = 0.4              # locate + pick one unit
    pack_fixed: float = 0.8                 # build carton, print label
    pack_per_unit: float = 0.25             # place + protect one unit
    sort_fixed: float = 0.5                 # scan, route to the right outbound lane
    service_cv: float = 0.3                 # variability of every task (lognormal, coefficient of variation)
    # Run control
    warmup_min: float = 60.0                # discarded so the line starts "already running"
    measure_min: float = 480.0              # one 8-hour shift measured
    sample_every_min: float = 0.5           # queue / WIP sampling interval

    @property
    def headcount(self) -> int:
        return self.pickers + self.packers + self.sorters

BASE = Params()

SCENARIOS = [
    BASE,
    replace(BASE, name="B. Add a packer (+1 headcount)", packers=4),
    replace(BASE, name="C. Rebalance (move 1 picker to pack)", pickers=5, packers=4),
    replace(BASE, name="D. Kaizen at pack (pre-built cartons)", pack_fixed=0.6),
    replace(BASE, name="E. Rebalance + Kaizen", pickers=5, packers=4, pack_fixed=0.6),
    replace(BASE, name="F. Kaizen + flex packer", packers=4, pack_fixed=0.6),
]

# Stress test: the chosen design under a 20% demand peak
PEAK = [replace(s, name=s.name + " @ +20% demand", orders_per_hour=144.0) for s in SCENARIOS]

REPLICATIONS = 30
