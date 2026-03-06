from __future__ import annotations

from dataclasses import dataclass
import math
from statistics import median
from typing import Dict, List, Tuple

from .tree_node import TreeNode


@dataclass(frozen=True)
class StageDefinition:
    stage: str
    step_size: float
    features: Dict[str, List[int]]


class TreeBuilder:
    def __init__(
        self,
        coarse_bucket_count: int = 3,
        coarse_features: Dict[str, List[int]] | None = None,
    ) -> None:
        if coarse_bucket_count not in {3, 4}:
            raise ValueError("coarse_bucket_count must be 3 or 4")
        self.coarse_bucket_count = coarse_bucket_count
        if coarse_features is None:
            coarse_features = {
                "low": [0, 1, 2, 3],
                "mid": [4, 5, 6],
                "high": [7, 8, 9],
            }
        self.stage_defs = [
            StageDefinition(
                stage="coarse",
                step_size=4.0,
                features=coarse_features,
            ),
            StageDefinition(
                stage="medium",
                step_size=2.0,
                features={
                    "b1_2": [0, 1],
                    "b3_4": [2, 3],
                    "b5_6": [4, 5],
                    "b7_8": [6, 7],
                    "b9_10": [8, 9],
                },
            ),
            StageDefinition(
                stage="fine",
                step_size=1.0,
                features={
                    "b1": [0],
                    "b2": [1],
                    "b3": [2],
                    "b4": [3],
                    "b5": [4],
                    "b6": [5],
                    "b7": [6],
                    "b8": [7],
                    "b9": [8],
                    "b10": [9],
                },
            ),
        ]
        self._node_seq = 0

    def build(self, presets: Dict[str, List[float]]) -> TreeNode:
        baseline = presets.get("flat", [0.0] * 10)
        learnable = {k: v for k, v in presets.items() if k != "flat"}
        deltas = {k: [v[i] - baseline[i] for i in range(10)] for k, v in learnable.items()}

        root = TreeNode(
            node_id="root",
            name="root",
            stage="root",
            candidate_presets=sorted(learnable.keys()),
            delta_curve=[0.0] * 10,
        )
        self._expand(parent=root, deltas=deltas, candidates=root.candidate_presets, stage_idx=0)
        return root

    def _expand(
        self,
        parent: TreeNode,
        deltas: Dict[str, List[float]],
        candidates: List[str],
        stage_idx: int,
    ) -> None:
        if stage_idx >= len(self.stage_defs):
            return
        if len(candidates) <= 1:
            return

        stage_def = self.stage_defs[stage_idx]
        if stage_idx == 0:
            feature_name, buckets = self._pick_best_coarse_feature(candidates, deltas, stage_def)
        else:
            feature_name, buckets = self._pick_best_feature(candidates, deltas, stage_def)
        if feature_name is None:
            return

        indices = stage_def.features[feature_name]
        for token_key, token_candidates in self._sorted_buckets(buckets):
            token_value = self._token_delta_value(token_candidates, indices, deltas)
            delta_curve = [0.0] * 10
            for idx in indices:
                delta_curve[idx] = token_value

            if isinstance(token_key, str):
                node_name = f"{feature_name}:{token_key}"
            else:
                node_name = f"{feature_name}:{token_key:+.1f}"

            child = TreeNode(
                node_id=self._next_node_id(stage_def.stage),
                name=node_name,
                stage=stage_def.stage,
                feature=feature_name,
                delta_curve=delta_curve,
                band_indices=indices[:],
                candidate_presets=sorted(token_candidates),
            )
            parent.add_child(child)
            self._expand(
                parent=child,
                deltas=deltas,
                candidates=child.candidate_presets,
                stage_idx=stage_idx + 1,
            )

    def _pick_best_coarse_feature(
        self,
        candidates: List[str],
        deltas: Dict[str, List[float]],
        stage_def: StageDefinition,
    ) -> Tuple[str | None, Dict[str, List[str]]]:
        best_feature = None
        best_buckets: Dict[str, List[str]] = {}
        best_score = -1e18

        for feature_name, indices in stage_def.features.items():
            buckets, score = self._cluster_coarse_buckets(candidates, deltas, indices)
            if len(buckets) <= 1:
                continue

            if score > best_score:
                best_score = score
                best_feature = feature_name
                best_buckets = buckets

        return best_feature, best_buckets

    def _pick_best_feature(
        self,
        candidates: List[str],
        deltas: Dict[str, List[float]],
        stage_def: StageDefinition,
    ) -> Tuple[str | None, Dict[float, List[str]]]:
        best_feature = None
        best_buckets: Dict[float, List[str]] = {}
        best_score = -1

        for feature_name, indices in stage_def.features.items():
            buckets: Dict[float, List[str]] = {}
            for preset_name in candidates:
                value = sum(deltas[preset_name][i] for i in indices) / len(indices)
                token = self._quantize(value, stage_def.step_size)
                buckets.setdefault(token, []).append(preset_name)

            if len(buckets) <= 1:
                continue

            score = len(buckets)
            if score > best_score:
                best_score = score
                best_feature = feature_name
                best_buckets = buckets

        return best_feature, best_buckets

    def _cluster_coarse_buckets(
        self,
        candidates: List[str],
        deltas: Dict[str, List[float]],
        indices: List[int],
    ) -> Tuple[Dict[str, List[str]], float]:
        k = min(self.coarse_bucket_count, len(candidates))
        vectors = {name: [deltas[name][i] for i in indices] for name in candidates}
        names = sorted(candidates)

        # Deterministic farthest-first init for medoids.
        medoids = [names[0]]
        while len(medoids) < k:
            remaining = [n for n in names if n not in medoids]
            farthest = max(
                remaining,
                key=lambda n: min(self._l1(vectors[n], vectors[m]) for m in medoids),
            )
            medoids.append(farthest)

        assignments = self._assign_to_medoids(names, medoids, vectors)
        for _ in range(3):
            medoids = self._recompute_medoids(assignments, vectors)
            assignments = self._assign_to_medoids(names, medoids, vectors)

        desired = self._desired_sizes(len(names), len(medoids))
        assignments = self._rebalance_assignments(assignments, medoids, vectors, desired)

        medoid_vecs = [vectors[m] for m in medoids]
        if len(medoid_vecs) > 1:
            sep = sum(
                self._l1(medoid_vecs[i], medoid_vecs[j])
                for i in range(len(medoid_vecs))
                for j in range(i + 1, len(medoid_vecs))
            ) / (len(medoid_vecs) * (len(medoid_vecs) - 1) / 2.0)
        else:
            sep = 0.0
        compact = 0.0
        denom = 0
        for m, members in assignments.items():
            for n in members:
                compact += self._l1(vectors[n], vectors[m])
                denom += 1
        compact = compact / max(denom, 1)

        ordered = sorted(
            assignments.items(),
            key=lambda x: self._cluster_mean(x[1], vectors),
            reverse=True,
        )
        labels = self._coarse_labels(len(ordered))
        buckets: Dict[str, List[str]] = {}
        for label, (_, members) in zip(labels, ordered):
            buckets[label] = sorted(members)

        score = sep - compact
        return buckets, score

    @staticmethod
    def _coarse_labels(k: int) -> List[str]:
        if k >= 4:
            return ["boost", "neutral", "cut", "strong_cut"][:k]
        if k == 3:
            return ["boost", "neutral", "cut"]
        if k == 2:
            return ["boost", "cut"]
        return ["neutral"]

    @staticmethod
    def _cluster_mean(members: List[str], vectors: Dict[str, List[float]]) -> float:
        vals = [sum(vectors[m]) / len(vectors[m]) for m in members]
        return sum(vals) / len(vals)

    @staticmethod
    def _l1(a: List[float], b: List[float]) -> float:
        return sum(abs(a[i] - b[i]) for i in range(len(a)))

    def _assign_to_medoids(
        self,
        names: List[str],
        medoids: List[str],
        vectors: Dict[str, List[float]],
    ) -> Dict[str, List[str]]:
        out = {m: [] for m in medoids}
        for n in names:
            best = min(medoids, key=lambda m: (self._l1(vectors[n], vectors[m]), m))
            out[best].append(n)
        return out

    def _recompute_medoids(
        self,
        assignments: Dict[str, List[str]],
        vectors: Dict[str, List[float]],
    ) -> List[str]:
        medoids: List[str] = []
        for old_m, members in assignments.items():
            if not members:
                medoids.append(old_m)
                continue
            new_m = min(
                members,
                key=lambda x: sum(self._l1(vectors[x], vectors[y]) for y in members),
            )
            medoids.append(new_m)
        return sorted(medoids)

    @staticmethod
    def _desired_sizes(n: int, k: int) -> List[int]:
        base = n // k
        rem = n % k
        return [base + (1 if i < rem else 0) for i in range(k)]

    def _rebalance_assignments(
        self,
        assignments: Dict[str, List[str]],
        medoids: List[str],
        vectors: Dict[str, List[float]],
        desired_sizes: List[int],
    ) -> Dict[str, List[str]]:
        desired = {m: desired_sizes[i] for i, m in enumerate(medoids)}
        out = {m: members[:] for m, members in assignments.items()}
        for m in out:
            out[m].sort()

        while True:
            over = [m for m in medoids if len(out[m]) > desired[m]]
            under = [m for m in medoids if len(out[m]) < desired[m]]
            if not over or not under:
                break

            best_move = None
            best_cost = math.inf
            for src in over:
                for name in out[src]:
                    src_cost = self._l1(vectors[name], vectors[src])
                    for dst in under:
                        dst_cost = self._l1(vectors[name], vectors[dst])
                        move_cost = dst_cost - src_cost
                        if move_cost < best_cost:
                            best_cost = move_cost
                            best_move = (src, dst, name)

            if best_move is None:
                break
            src, dst, name = best_move
            out[src].remove(name)
            out[dst].append(name)
            out[dst].sort()

        return out

    @staticmethod
    def _token_delta_value(
        token_candidates: List[str],
        indices: List[int],
        deltas: Dict[str, List[float]],
    ) -> float:
        means = []
        for preset_name in token_candidates:
            vals = [deltas[preset_name][i] for i in indices]
            means.append(sum(vals) / len(vals))
        return round(float(median(means)), 1)

    @staticmethod
    def _sorted_buckets(buckets: Dict[float, List[str]] | Dict[str, List[str]]) -> List[Tuple[float | str, List[str]]]:
        if not buckets:
            return []
        sample_key = next(iter(buckets.keys()))
        if isinstance(sample_key, str):
            order = {"boost": 0, "neutral": 1, "cut": 2, "strong_cut": 3}
            return sorted(buckets.items(), key=lambda x: order.get(str(x[0]), 99))
        return sorted(buckets.items(), key=lambda x: float(x[0]), reverse=True)

    @staticmethod
    def _quantize(value: float, step: float) -> float:
        token = round(value / step) * step
        if abs(token) < (step / 2.0):
            return 0.0
        return max(-12.0, min(12.0, float(token)))

    def _next_node_id(self, stage: str) -> str:
        self._node_seq += 1
        return f"{stage}_{self._node_seq:04d}"
