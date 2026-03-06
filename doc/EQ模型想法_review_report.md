# EQ 模型想法 Review Report

Date: 2026-03-05  
Author: Codex (based on user discussion)

## 1. Executive Summary

本提案的核心是建立一個「情緒驅動 + 漸進式 + 決策樹」的 EQ 推薦機制。  
與一般直接逼近某個完整 preset 向量不同，你的設計是先將 preset 分解成可重用的小曲線（delta primitives），再透過情緒回饋逐步選擇路徑，達成候選 preset 的持續收斂（例如 5 -> 3 -> 2 -> 1）。

結論：此設計具備可行性，且在產品化上具備可解釋性與可擴展性，方向正確。

## 2. User Intent (Confirmed Understanding)

你要的模型不是「直接往某 preset 向量靠近」，而是：

1. 每個 preset 是一條完整 EQ 曲線。
2. 每條曲線可由多段小曲線組合而成（有共用片段，也有特有片段）。
3. tree 節點 = 小曲線（例如 `low +4dB`、`high +4dB`、`mid -2dB`）。
4. 每走一個節點就疊加一段小曲線，並同時縮小候選 preset 集合。
5. 情緒趨勢決定 traversal：keep / switch / fallback。
6. coarse-to-fine 應同時包含：
   - 調整幅度（dB step size）
   - 頻帶寬度（區域 -> 子區域 -> 單 band）

## 3. Technical Value

此架構有三個明顯優勢：

1. 可解釋性高：每次調整都能用「哪段小曲線被選中」來解釋。
2. 搜尋效率高：先做大分裂，可快速縮小候選空間。
3. 可持續學習：長期可統計哪些小曲線在何種使用者/音樂特徵下有效。

## 4. Algorithm Feasibility

小曲線節點可由 preset library 自動計算，不需全手工定義。建議流程：

1. 選 baseline（flat 或平均曲線）。
2. 計算各 preset 的 delta 向量。
3. 依 coarse/medium/fine 的 band group 切分。
4. 將區段 delta 量化成 token（例：`low:+4`, `high:-2`）。
5. 統計 token 支持度與區分能力（support + information gain）。
6. 以高區分度 token 建立 decision tree。
7. 每個節點保存：
   - `delta_curve`
   - `candidate_presets`
   - `depth/stage`

## 5. Key Design Requirements

為符合你的原始意圖，系統需具備以下必要能力：

1. `Delta-curve tree`：節點必須是可套用的小曲線，不是僅分類標籤。
2. `Candidate pruning`：每一步都要更新候選 preset 集合。
3. `Width-aware optimization`：stage 要控制 band width（不是只有 step size）。
4. `Path memory`：保留已套用小曲線序列，避免無效震盪。
5. `Emotion robustness`：滑動視窗 + 投票/平滑，降低短期雜訊影響。

## 6. Risks and Mitigation

1. 情緒訊號不穩定造成錯誤分支
   - Mitigation: window smoothing、minimum confidence、cooldown steps。
2. 小曲線字典過大導致分支爆炸
   - Mitigation: 支持度閾值、最大樹深、每層 top-k token。
3. preset 間可分性不足
   - Mitigation: 增加中層特徵（pair-band tokens）或引入音樂內容條件。
4. 路徑震盪（來回切換）
   - Mitigation: hysteresis 機制 + fallback penalty。

## 7. Suggested Implementation Plan (MVP -> V2)

1. V1: 手工定義少量小曲線節點（先驗證路徑式收斂）
2. V1.5: 自動 token 萃取 + candidate pruning
3. V2: 引入 width-aware scheduler（region -> pair -> single）
4. V2.5: 加入 path scoring（emotion gain 累積分數）
5. V3: 長期資料學習 User Sound Profile

## 8. Review Verdict

你的模型思路在技術上成立，且相較「直接向量逼近 preset」更符合情緒閉環場景。  
下一步的關鍵不是再增加更多 preset，而是先把「小曲線節點 + 候選收斂 + width-aware coarse-to-fine」三件事做完整。
