from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class TreeNode:
    node_id: str
    name: str
    stage: str = "root"
    feature: Optional[str] = None
    delta_curve: Optional[List[float]] = None
    band_indices: List[int] = field(default_factory=list)
    candidate_presets: List[str] = field(default_factory=list)
    parent_id: Optional[str] = None
    children: List["TreeNode"] = field(default_factory=list)

    def add_child(self, node: "TreeNode") -> None:
        node.parent_id = self.node_id
        self.children.append(node)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "name": self.name,
            "stage": self.stage,
            "feature": self.feature,
            "delta_curve": self.delta_curve,
            "band_indices": self.band_indices,
            "candidate_presets": self.candidate_presets,
            "parent_id": self.parent_id,
            "children": [c.to_dict() for c in self.children],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TreeNode":
        node = cls(
            node_id=data["node_id"],
            name=data["name"],
            stage=data.get("stage", "root"),
            feature=data.get("feature"),
            delta_curve=data.get("delta_curve"),
            band_indices=list(data.get("band_indices", [])),
            candidate_presets=list(data.get("candidate_presets", [])),
            parent_id=data.get("parent_id"),
        )
        for child_data in data.get("children", []):
            child = cls.from_dict(child_data)
            node.add_child(child)
        return node
