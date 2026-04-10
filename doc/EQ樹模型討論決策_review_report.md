# EQ 樹模型討論決策 Review Report

Date: 2026-03-09

## 1. 目的

本文件整理本輪討論的重點決策，作為後續實作與溝通基準。

## 2. 已確認的核心方向

1. 系統分為兩個任務：
   - 建樹分析任務（離線）：由 preset 建立固定 tree snapshot
   - EQ 模型任務（線上執行）：載入固定 tree，根據情緒回饋做 traversal 與 EQ 調整
2. runtime 不需要每次重建 tree，除非 preset 或建樹參數改變。
3. tree 的角色是「漸進式搜尋與候選收斂」，不是直接等於最終完整 preset。
4. 當候選收斂到單一 preset 時，engine 會切到完整 preset 目標做 full-band refine。

## 3. Tree 生成邏輯（目前採用）

1. coarse 層使用 clustering（曲線形狀分群，非單純平均值）。
2. coarse bucket 支援 `3` 或 `4` 群：
   - 3 群：`boost / neutral / cut`
   - 4 群：`boost / neutral / cut / strong_cut`
3. coarse band 區間可調（low/mid/high 可自訂 band index range）。
4. 目前已加入平衡分配機制，當資料條件允許時可達到例如 `4/4/4`。

## 4. 節點調整值：中位數 vs common core

### 4.1 兩種方法

1. 中位數 delta（目前採用）：
   - 節點調整值使用該子集在該特徵區段的中位數代表值
2. common core（討論但目前未採用）：
   - 以子集共同擁有的曲線部分作為調整值（類似最大公因曲線概念）

### 4.2 討論結論

在目前系統架構下，維持中位數更合理，理由：

1. 子集合 band 差異大時，common core 容易被壓得太小，初期調整不明顯。
2. 中位數可保留足夠調整量，前段更有「可感」變化。
3. 系統本來就有「單一候選後 full preset refine」，因此前段只需把 EQ 帶到目標附近，不必每步都採最保守共同值。

## 5. 關於「是否會偏離 preset」的結論

1. tree 節點本身是局部 delta，不是完整 preset。
2. 但 runtime 在單一候選時會切成完整 preset 目標。
3. 因此整體流程可同時滿足：
   - 前段：可解釋、可感知、漸進搜尋
   - 後段：可收斂到指定 preset

## 6. fallback 與回調理解

1. 到葉節點不代表永久鎖定。
2. 若後續情緒持續負面，policy 可 fallback 回上層再探索。
3. 可進一步加強（後續建議）：
   - 連續 N 次 worsen 才 fallback
   - branch cooldown，避免來回震盪

## 7. 目前產出與可讀性

已具備雙輸出：

1. `data/tree_snapshot.json`：機器可讀
2. `data/tree_snapshot.md`：人類可讀（每個節點列出 stage、候選數、band 調整 dB）

## 8. 最終結論

本輪決策為：

1. 保留 clustering coarse 分群與可調 coarse bands 設定。
2. 保留中位數作為節點調整代表值（不改 common core）。
3. 保留單一候選後 full preset refine，確保最終可貼合 preset。
4. 後續優化優先放在 fallback 穩定化，而非重寫節點數值定義。
