# Emotion EQ Engine (MVP)

Emotion-driven adaptive progressive EQ recommendation.

## Requirements

- Python 3.10+
- Run commands at project root

## Core Workflow

1. Build fixed tree snapshot from `preset_library.json`
2. Inspect tree in JSON/Markdown
3. Run EQ engine using the fixed tree

## 1) Build Tree Snapshot

Default build:

```bash
python3 -m emotion_eq_engine.demo.build_tree
```

Outputs:

- `data/tree_snapshot.json`
- `data/tree_snapshot.md`

Advanced build options:

```bash
python3 -m emotion_eq_engine.demo.build_tree \
  --coarse-buckets 3 \
  --coarse-bands 0-3,4-6,7-9
```

Notes:

- `--coarse-buckets`: `3` or `4`
- `--coarse-bands`: low,mid,high index ranges (0-based)
- Example `0-3,4-6,7-9` means:
  - low: b1-b4
  - mid: b5-b7
  - high: b8-b10

## 2) Read Tree Output

- `tree_snapshot.json`: machine-readable tree
- `tree_snapshot.md`: human-readable tree
  - each node shows `stage`, `candidates`, and `delta` adjustments per band

## 3) Run EQ Engine

Use SEDU CSV:

```bash
python3 -m emotion_eq_engine.demo.run_demo \
  --sedu-csv data/sedu_sample.csv \
  --steps 30 \
  --interval 0.1
```

Without `--sedu-csv`, synthetic stream is used.

Force runtime rebuild from latest presets:

```bash
python3 -m emotion_eq_engine.demo.run_demo --rebuild-tree
```

Use specific snapshot path:

```bash
python3 -m emotion_eq_engine.demo.run_demo --tree-snapshot data/tree_snapshot.json
```

## Quick Validation

```bash
./tests/test_smoke.sh
```
