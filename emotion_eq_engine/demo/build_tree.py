from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List

from emotion_eq_engine.preset.preset_manager import PresetManager
from emotion_eq_engine.tree_builder.tree_builder import TreeBuilder
from emotion_eq_engine.tree_builder.tree_snapshot import save_tree_markdown, save_tree_snapshot


def default_snapshot_path() -> Path:
    project_root = Path(__file__).resolve().parents[2]
    return project_root / "data" / "tree_snapshot.json"


def default_markdown_path() -> Path:
    project_root = Path(__file__).resolve().parents[2]
    return project_root / "data" / "tree_snapshot.md"


def parse_coarse_bands(spec: str) -> Dict[str, List[int]]:
    # Format: "0-3,4-6,7-9" -> low,mid,high
    parts = [p.strip() for p in spec.split(",") if p.strip()]
    if len(parts) != 3:
        raise ValueError("coarse band spec must have 3 ranges: low,mid,high")
    names = ["low", "mid", "high"]
    out: Dict[str, List[int]] = {}
    for name, part in zip(names, parts):
        if "-" not in part:
            raise ValueError(f"invalid range '{part}', expected start-end")
        a_str, b_str = [x.strip() for x in part.split("-", 1)]
        a, b = int(a_str), int(b_str)
        if a < 0 or b > 9 or a > b:
            raise ValueError(f"invalid range '{part}', must be within 0..9 and start<=end")
        out[name] = list(range(a, b + 1))
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Build fixed EQ decision tree snapshot")
    parser.add_argument("--output", type=Path, default=default_snapshot_path())
    parser.add_argument("--md-output", type=Path, default=default_markdown_path())
    parser.add_argument("--coarse-buckets", type=int, choices=[3, 4], default=3)
    parser.add_argument(
        "--coarse-bands",
        type=str,
        default="0-3,4-6,7-9",
        help="Band ranges for low,mid,high (0-based), e.g. 0-3,4-6,7-9",
    )
    args = parser.parse_args()

    presets = PresetManager().load()
    coarse_features = parse_coarse_bands(args.coarse_bands)
    root = TreeBuilder(
        coarse_bucket_count=args.coarse_buckets,
        coarse_features=coarse_features,
    ).build(presets)
    save_tree_snapshot(root, args.output)
    save_tree_markdown(root, args.md_output)
    print(f"Tree snapshot saved: {args.output}")
    print(f"Tree markdown saved: {args.md_output}")
    print(f"coarse buckets: {args.coarse_buckets}")
    print(f"coarse bands: {coarse_features}")


if __name__ == "__main__":
    main()
