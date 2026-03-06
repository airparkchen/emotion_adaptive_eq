from __future__ import annotations

import csv
import itertools
import math
from pathlib import Path
from typing import Iterator, List


class SEDUStream:
    def __init__(self, csv_path: Path | None = None, loop: bool = True) -> None:
        self.csv_path = csv_path
        self.loop = loop

    def iter_scores(self) -> Iterator[float]:
        if self.csv_path is None:
            yield from self._synthetic_stream()
            return

        rows = self._load_csv_scores()
        if not rows:
            raise ValueError(f"No emotion data found in CSV: {self.csv_path}")

        if self.loop:
            while True:
                for score in rows:
                    yield score
        else:
            for score in rows:
                yield score

    def _load_csv_scores(self) -> List[float]:
        scores: List[float] = []
        with self.csv_path.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if "emotion_score" in row and row["emotion_score"]:
                    scores.append(float(row["emotion_score"]))
                elif "emotion_label" in row and row["emotion_label"]:
                    label = row["emotion_label"].strip().lower()
                    scores.append(1.0 if label in {"positive", "pos", "1"} else -1.0)
                else:
                    scores.append(0.0)
        return scores

    def _synthetic_stream(self) -> Iterator[float]:
        for i in itertools.count():
            base = math.sin(i / 7.0)
            yield max(-1.0, min(1.0, base))
