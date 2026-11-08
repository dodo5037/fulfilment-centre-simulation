# A3: Reducing order cycle time on the fulfilment line

*Simulation study with illustrative parameters. Owner: Abderrahmane Messaoudi.*

| 1. Background | 2. Current state |
|---|---|
| A fulfilment line (Pick → Pack → Sort/Ship, 11 staff) handles 120 orders/hour on a normal day and about 144 on peak days. Customers and outbound trucks depend on short, predictable order cycle times. | Average cycle time **8.5 min**, 95th percentile **14.7 min**. Only **48%** of an order's time is value-added work; the rest is waiting. On a peak day the line falls behind: **44.2 min** average, **315 of 360** units/h shipped. |

| 3. Goal | 4. Root cause analysis |
|---|---|
| Cut average cycle time by at least 30% on a normal day **without adding headcount**, and keep peak-day cycle time under 10 min. | Utilisation: pick 73%, **pack 94%**, sort 50%. Pack is the constraint. Near 100% load, random variation turns into long queues (queueing theory: waiting time grows sharply as ρ → 1). Each pack task starts with building a carton (0.8 min), much of which is setup that could be done ahead of time. |

| 5. Countermeasures tested (simulation, 30 shifts each) | 6. Results |
|---|---|
| A. Baseline · B. +1 packer · C. move 1 picker to pack · **D. Kaizen: pre-built cartons, pack setup 0.8 → 0.6 min (assumed)** · E. C + D · **F. D + 1 flex packer on peak days** | Normal day, **D**: cycle **5.1 min (-41%)**, p95 **8.4 min (-43%)**, value-added **78%**, same 11 staff. Rebalancing (C, E) only moved the bottleneck to pick (88%). Peak day, **F**: cycle **5.2 min (-88% vs baseline)**, ships 355 units/h. |

| 7. Follow-up | |
|---|---|
| 1. Time-study the pack station to confirm the 25% setup reduction before rollout. 2. Pilot pre-built cartons for 2 weeks; track cycle time p95 and pack queue length daily. 3. Cross-train one worker as a flex packer for peak days. 4. Re-run the model with measured times; next constraint to watch is pick. | |

Charts: `outputs/charts/`. Model and assumptions: `src/config.py`.
