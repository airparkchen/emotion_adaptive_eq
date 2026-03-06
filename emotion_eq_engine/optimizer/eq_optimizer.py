from __future__ import annotations

from typing import List, Tuple

from .step_scheduler import StepScheduler


class EQOptimizer:
    def __init__(self, scheduler: StepScheduler | None = None) -> None:
        self.scheduler = scheduler or StepScheduler()

    def next_eq(
        self,
        current: List[float],
        target: List[float],
        step_index: int,
        band_indices: List[int] | None = None,
    ) -> Tuple[List[float], str]:
        cfg = self.scheduler.config_for_step(step_index)
        focus = set(band_indices if band_indices else range(len(current)))
        diffs = [(i, target[i] - current[i]) for i in range(len(current)) if i in focus]
        diffs.sort(key=lambda x: abs(x[1]), reverse=True)

        next_eq = current[:]
        updated = 0
        limit = min(cfg.band_width, len(focus))
        for i, delta in diffs:
            if updated >= limit:
                break
            if delta == 0:
                continue
            move = min(cfg.step_size, abs(delta))
            next_eq[i] += move if delta > 0 else -move
            next_eq[i] = max(-12.0, min(12.0, next_eq[i]))
            updated += 1

        return next_eq, cfg.stage
