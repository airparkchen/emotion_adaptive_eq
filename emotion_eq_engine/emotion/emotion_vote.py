from __future__ import annotations

from typing import List


class EmotionTrend:
    IMPROVE = "improve"
    STABLE = "stable"
    WORSEN = "worsen"


class EmotionVote:
    def __init__(self, threshold: float = 0.05) -> None:
        self.threshold = threshold

    def evaluate(self, values: List[float]) -> str:
        mid = len(values) // 2
        first = values[:mid]
        second = values[mid:]
        if not first or not second:
            return EmotionTrend.STABLE

        first_mean = sum(first) / len(first)
        second_mean = sum(second) / len(second)
        diff = second_mean - first_mean

        if diff > self.threshold:
            return EmotionTrend.IMPROVE
        if diff < -self.threshold:
            return EmotionTrend.WORSEN
        return EmotionTrend.STABLE
