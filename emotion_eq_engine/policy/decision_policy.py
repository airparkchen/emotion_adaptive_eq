from __future__ import annotations

from typing import Dict, List

from emotion_eq_engine.emotion.emotion_vote import EmotionTrend
from emotion_eq_engine.tree_builder.tree_node import TreeNode


class DecisionPolicy:
    def __init__(self, root: TreeNode) -> None:
        self.root = root
        self._parent: Dict[str, TreeNode] = {}
        self._siblings: Dict[str, List[TreeNode]] = {}
        self._index(root)

    def choose_next(self, current: TreeNode, trend: str) -> TreeNode:
        if trend == EmotionTrend.IMPROVE:
            return self._prefer_deeper(current)
        if trend == EmotionTrend.WORSEN:
            return self._fallback(current)
        return self._switch_side(current)

    def _prefer_deeper(self, node: TreeNode) -> TreeNode:
        if node.children:
            return node.children[0]
        return node

    def _switch_side(self, node: TreeNode) -> TreeNode:
        siblings = self._siblings.get(node.node_id, [])
        if not siblings:
            if node.children:
                return node.children[0]
            return node

        idx = siblings.index(node)
        return siblings[(idx + 1) % len(siblings)]

    def _fallback(self, node: TreeNode) -> TreeNode:
        return self._parent.get(node.node_id, self.root)

    def _index(self, root: TreeNode) -> None:
        stack = [root]
        while stack:
            node = stack.pop()
            if node.children:
                for child in node.children:
                    self._parent[child.node_id] = node
                for child in node.children:
                    self._siblings[child.node_id] = node.children
                stack.extend(node.children)
