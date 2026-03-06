#!/usr/bin/env bash
set -euo pipefail
python3 -m emotion_eq_engine.demo.run_demo --sedu-csv data/sedu_sample.csv --steps 8 --interval 0
