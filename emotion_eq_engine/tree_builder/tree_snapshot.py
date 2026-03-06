from __future__ import annotations

import json
from pathlib import Path
from typing import List

from .tree_node import TreeNode


BAND_FREQS = [200.0, 280.0, 400.0, 550.0, 770.0, 1000.0, 2000.0, 4000.0, 8000.0, 16000.0]


def save_tree_snapshot(root: TreeNode, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(root.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_tree_snapshot(path: Path) -> TreeNode:
    data = json.loads(path.read_text(encoding="utf-8"))
    return TreeNode.from_dict(data)


def save_tree_markdown(root: TreeNode, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: List[str] = []
    lines.append("# EQ Tree Snapshot")
    lines.append("")
    lines.append("## Band Mapping")
    lines.append(", ".join(f"b{i+1}:{freq:.1f}Hz" for i, freq in enumerate(BAND_FREQS)))
    lines.append("")
    lines.append("## Tree")
    _render_node(root, depth=0, lines=lines)
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _render_node(node: TreeNode, depth: int, lines: List[str]) -> None:
    indent = "  " * depth
    lines.append(f"{indent}- `{node.name}` (stage={node.stage}, candidates={len(node.candidate_presets)})")
    if node.candidate_presets:
        lines.append(f"{indent}  - presets: {', '.join(node.candidate_presets)}")
    if node.delta_curve:
        adj = _format_adjustments(node.delta_curve)
        if adj:
            lines.append(f"{indent}  - delta: {adj}")
    for child in node.children:
        _render_node(child, depth + 1, lines)


def _format_adjustments(delta_curve: List[float]) -> str:
    parts: List[str] = []
    for i, v in enumerate(delta_curve):
        if abs(v) < 1e-9:
            continue
        sign = "+" if v > 0 else ""
        parts.append(f"b{i+1}({BAND_FREQS[i]:.1f}Hz) {sign}{v:.1f}dB")
    return ", ".join(parts)
