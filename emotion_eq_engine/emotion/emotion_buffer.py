from __future__ import annotations

from collections import deque
from typing import Deque, List


class EmotionBuffer:
    def __init__(self, size: int = 6) -> None:
        self.size = size
        self._values: Deque[float] = deque(maxlen=size)

    def push(self, score: float) -> None:
        self._values.append(score)

    def values(self) -> List[float]:
        return list(self._values)

    def ready(self) -> bool:
        return len(self._values) == self.size
