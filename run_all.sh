#!/usr/bin/env bash
# Runs the experiments, draws the charts and runs the validation tests.
set -euo pipefail
cd "$(dirname "$0")"
python src/run_experiments.py
python src/charts.py
python -m pytest -q
