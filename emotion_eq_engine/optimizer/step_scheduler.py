from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StepConfig:
    stage: str
    step_size: float
    band_width: int


class StepScheduler:
    def config_for_step(self, step_index: int) -> StepConfig:
        if step_index < 8:
            return StepConfig(stage="coarse", step_size=4.0, band_width=4)
        if step_index < 16:
            return StepConfig(stage="medium", step_size=2.0, band_width=2)
        return StepConfig(stage="fine", step_size=1.0, band_width=1)
