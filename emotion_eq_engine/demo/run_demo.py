from __future__ import annotations

import argparse
from pathlib import Path

from emotion_eq_engine.engine.eq_engine import EQEngine


def main() -> None:
    parser = argparse.ArgumentParser(description="Run emotion-driven EQ engine demo")
    parser.add_argument("--sedu-csv", type=Path, default=None, help="Path to SEDU CSV with emotion_score/emotion_label")
    parser.add_argument("--steps", type=int, default=30)
    parser.add_argument("--interval", type=float, default=0.1)
    parser.add_argument("--no-loop", action="store_true", help="Disable CSV replay when end-of-file is reached")
    parser.add_argument("--tree-snapshot", type=Path, default=None, help="Path to prebuilt tree snapshot JSON")
    parser.add_argument("--rebuild-tree", action="store_true", help="Rebuild tree from presets and overwrite snapshot")
    args = parser.parse_args()

    engine = EQEngine(
        sedu_csv=args.sedu_csv,
        stream_loop=not args.no_loop,
        tree_snapshot=args.tree_snapshot,
        rebuild_tree=args.rebuild_tree,
    )
    history = engine.run(steps=args.steps, interval_sec=args.interval)

    for s in history:
        print(
            f"step={s.step:02d} node={s.current_node:<14} trend={str(s.trend):<7} "
            f"stage={s.stage:<6} candidates={s.candidate_count:<2} "
            f"eq={','.join(f'{v:>4.1f}' for v in s.current_eq)}"
        )


if __name__ == "__main__":
    main()
