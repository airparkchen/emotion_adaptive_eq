from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from emotion_eq_engine.emotion.emotion_evaluator import EmotionEvaluator
from emotion_eq_engine.emotion.sedu_stream import SEDUStream
from emotion_eq_engine.optimizer.eq_optimizer import EQOptimizer
from emotion_eq_engine.policy.decision_policy import DecisionPolicy
from emotion_eq_engine.preset.preset_manager import PresetManager
from emotion_eq_engine.tree_builder.tree_builder import TreeBuilder
from emotion_eq_engine.tree_builder.tree_node import TreeNode
from emotion_eq_engine.tree_builder.tree_snapshot import load_tree_snapshot, save_tree_snapshot


@dataclass
class EngineState:
    step: int
    current_node: str
    trend: str | None
    stage: str
    candidate_count: int
    current_eq: List[float]


class EQEngine:
    def __init__(
        self,
        sedu_csv: Path | None = None,
        stream_loop: bool = True,
        tree_snapshot: Path | None = None,
        rebuild_tree: bool = False,
    ) -> None:
        self.preset_manager = PresetManager()
        self.presets = self.preset_manager.load()

        snapshot_path = tree_snapshot or self._default_tree_snapshot_path()
        if rebuild_tree or not snapshot_path.exists():
            self.root = TreeBuilder().build(self.presets)
            save_tree_snapshot(self.root, snapshot_path)
        else:
            self.root = load_tree_snapshot(snapshot_path)

        self.policy = DecisionPolicy(self.root)
        self.optimizer = EQOptimizer()
        self.evaluator = EmotionEvaluator(window_size=6, threshold=0.04)
        self.stream = SEDUStream(csv_path=sedu_csv, loop=stream_loop)
        self.parents = self._index_parents(self.root)

        self.current_node = self.root
        self.current_eq = [0.0] * 10
        self._stream_iter = self.stream.iter_scores()

    def step_once(self, step_index: int) -> EngineState:
        try:
            emotion_score = next(self._stream_iter)
        except StopIteration:
            # Defensive fallback for non-loop streams.
            self._stream_iter = self.stream.iter_scores()
            emotion_score = next(self._stream_iter)
        trend = self.evaluator.update(emotion_score)

        if trend is not None:
            self.current_node = self.policy.choose_next(self.current_node, trend)

        target = self._resolve_target_eq(self.current_node)
        focus_indices = self._resolve_focus_indices(self.current_node)
        self.current_eq, stage = self.optimizer.next_eq(
            self.current_eq,
            target,
            step_index,
            band_indices=focus_indices,
        )

        return EngineState(
            step=step_index,
            current_node=self.current_node.name,
            trend=trend,
            stage=stage,
            candidate_count=len(self.current_node.candidate_presets),
            current_eq=self.current_eq[:],
        )

    def run(self, steps: int = 30, interval_sec: float = 0.2) -> List[EngineState]:
        history: List[EngineState] = []
        for i in range(steps):
            state = self.step_once(i)
            history.append(state)
            time.sleep(interval_sec)
        return history

    def _resolve_target_eq(self, node: TreeNode) -> List[float]:
        # Once tree search converges to one preset, refine toward exact preset EQ.
        if len(node.candidate_presets) == 1:
            preset_name = node.candidate_presets[0]
            vec = self.presets.get(preset_name)
            if vec is not None:
                return [max(-12.0, min(12.0, float(v))) for v in vec]

        target = [0.0] * 10
        for n in self._path_to_root(node):
            if n.delta_curve:
                target = [target[i] + n.delta_curve[i] for i in range(10)]
        return [max(-12.0, min(12.0, v)) for v in target]

    def _resolve_focus_indices(self, node: TreeNode) -> List[int] | None:
        # For exact preset refinement, allow all bands to be updated.
        if len(node.candidate_presets) == 1:
            return None
        return node.band_indices

    def _path_to_root(self, node: TreeNode) -> List[TreeNode]:
        path: List[TreeNode] = []
        cur = node
        while cur.node_id != "root":
            path.append(cur)
            parent = self.parents.get(cur.node_id)
            if parent is None:
                break
            cur = parent
        path.reverse()
        return path

    def _index_parents(self, root: TreeNode) -> Dict[str, TreeNode]:
        parent: Dict[str, TreeNode] = {}
        stack = [root]
        while stack:
            node = stack.pop()
            for child in node.children:
                parent[child.node_id] = node
                stack.append(child)
        return parent

    def _default_tree_snapshot_path(self) -> Path:
        project_root = Path(__file__).resolve().parents[2]
        return project_root / "data" / "tree_snapshot.json"
