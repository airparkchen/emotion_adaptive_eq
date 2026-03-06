from __future__ import annotations

from .emotion_buffer import EmotionBuffer
from .emotion_vote import EmotionTrend, EmotionVote


class EmotionEvaluator:
    def __init__(self, window_size: int = 6, threshold: float = 0.05) -> None:
        self.buffer = EmotionBuffer(size=window_size)
        self.vote = EmotionVote(threshold=threshold)

    def update(self, emotion_score: float) -> str | None:
        self.buffer.push(emotion_score)
        if not self.buffer.ready():
            return None
        return self.vote.evaluate(self.buffer.values())

    @staticmethod
    def label_to_score(label: str) -> float:
        normalized = label.strip().lower()
        if normalized in {"positive", "pos", "1", "true"}:
            return 1.0
        if normalized in {"negative", "neg", "0", "false"}:
            return -1.0
        return 0.0
