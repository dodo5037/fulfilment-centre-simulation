# Study guide: own this project before you show it

I (Claude) built the first version while you slept. Before you put it on your CV or LinkedIn, you need to be able to explain every part of it in your own words. Work through this in order. Budget about 3 to 4 hours.

## 1. Run it yourself (15 min)

```bash
cd ~/Desktop/"career ops"/fulfilment-centre-simulation
source .venv/bin/activate
./run_all.sh
```

You should see the two results tables, then "17 passed".

## 2. Read the code in this order (1.5 h)

1. `src/config.py`: every assumption lives here. For each number, ask: what does it mean physically?
2. `src/model.py`: follow ONE order through `order()`. Understand `yield req` (wait for a worker) and `yield env.timeout(...)` (do the work).
3. `src/run_experiments.py`: why 30 replications, and what the ± number means.
4. `tests/test_model.py`: why each test proves the model is trustworthy.

## 3. Concepts you must be able to explain

| Concept | One-line answer you should be able to give |
|---|---|
| Discrete-event simulation | The model jumps from event to event (arrival, start, finish) instead of ticking every second. |
| Poisson arrivals | Orders arrive randomly and independently at an average rate; gaps between them are exponential. |
| Lognormal task times | Always positive and right-skewed: most tasks are near average, a few take much longer, like real work. |
| Utilisation ρ = λ·E[S]/c | Arrival rate × average task time ÷ number of workers. Above about 85-90%, queues grow fast. |
| Bottleneck / constraint | The station with the highest utilisation; it limits the whole line (Theory of Constraints). |
| Little's Law L = λW | Average WIP = throughput × average time in system. True for any stable system; used here to validate the model. |
| Warm-up period | The line starts empty; the first hour is thrown away so results reflect normal running. |
| Replications + 95% CI | Each shift is random. 30 shifts give a mean and a range; if two ranges don't overlap, the difference is real. |
| Common random numbers | All scenarios use the same 30 seeds, so differences come from the design, not luck. |
| p95 cycle time | 95% of orders finish faster than this. Customers and truck cut-offs care about the slow orders, not just the average. |
| Value-added ratio | Time being worked on ÷ total time. Waiting is waste (lean). |
| Kaizen | A small, focused improvement that removes waste (here: pre-built cartons). |
| A3 | A one-page problem-solving report: background, current state, goal, root cause, countermeasures, results, follow-up. |

## 4. Interview questions to practise out loud

1. Walk me through your simulation in 60 seconds.
2. How do you know your model is correct? *(Little's Law and utilisation match theory; 17 tests.)*
3. Why did moving a picker to pack not help? *(It moved the bottleneck to pick, 88%, which breaks at peak.)*
4. Why 30 replications? Why not 1?
5. Where do your numbers come from? *(They are assumptions; say so. The next step is a time study.)*
6. What would you do with real data from our warehouse?
7. What are the limitations? *(No breaks, failures, waves; one product family; FCFS.)*
8. Why look at p95 and not just the average?

## 5. Make it yours (pick at least one, this is what you talk about in interviews)

- Add **hourly demand waves** (e.g. a morning peak) instead of a constant rate.
- Add **worker breaks** or **equipment downtime** at pack.
- Add a **cost model** (labour cost per hour vs late-order penalty) and find the cheapest staffing.
- Try **batch picking** (one picker handles 2-3 orders per trip) and see if pick stops being the next constraint.
- Draw a proper **value stream map** by hand from the results and add a photo to `docs/`.

## 6. Then

- Tell Claude when you're ready to push it to GitHub (it's committed locally only).
- Add it to `cv.md`, LinkedIn Projects, and pin it on GitHub.
