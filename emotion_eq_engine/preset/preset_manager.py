from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


class PresetManager:
    def __init__(self, library_path: Path | None = None) -> None:
        if library_path is None:
            library_path = Path(__file__).with_name("preset_library.json")
        self.library_path = library_path
        self._presets: Dict[str, List[float]] = {}

    def load(self) -> Dict[str, List[float]]:
        data = json.loads(self.library_path.read_text(encoding="utf-8"))
        self._validate(data)
        self._presets = {k: [float(v) for v in vec] for k, vec in data.items()}
        return self._presets

    @property
    def presets(self) -> Dict[str, List[float]]:
        if not self._presets:
            return self.load()
        return self._presets

    @staticmethod
    def _validate(data: Dict[str, List[float]]) -> None:
        for name, vec in data.items():
            if len(vec) != 10:
                raise ValueError(f"Preset '{name}' must have 10 bands, got {len(vec)}")
            for v in vec:
                if v < -12 or v > 12:
                    raise ValueError(f"Preset '{name}' has out-of-range band value: {v}")
