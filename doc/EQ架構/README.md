# EQ 架構總覽

Date: 2026-04-15

本資料夾用來整理目前 `emotion_adaptive_eq` 專案的核心規劃。  
這份 README 的目的不是放所有細節，而是讓第一次接觸這個專案的人，能先快速理解：

1. 我們想解決什麼問題
2. 目前採用什麼方法
3. 哪些部分已經有初步共識
4. 哪些部分還在持續研究與調參

若需要深入細節，可再進一步閱讀各子文件。

## 1. EQ 方案整體概述

本專案要做的是一個 **情緒驅動的個人化 EQ 推薦系統**。

核心目標不是直接在完整 10-band EQ 空間中暴力搜尋最佳解，而是：

1. 先建立一組具有代表性的 `preset EQ` 候選集合
2. 將這些 preset 轉成 `coarse-to-fine` 的 tree 搜尋結構
3. 在使用者實際聆聽過程中，透過情緒模型輸出取得 reward
4. 根據 reward 逐步決定 EQ 的前進、切換、回退方向
5. 最後收斂到最接近使用者偏好的 EQ

目前專案的整體定位是：

- `preset-based recommendation`
- `emotion-driven closed-loop optimization`
- `coarse-to-fine personalization`

這裡的問題定義不是：

- 完整分類所有可能 EQ 組合

而是：

- 從高價值候選集合中做個人化推薦

詳細說明：
- [完整提案說明.md](/home/parker6/Documents/project_02_ARMO/emotion_adaptive_eq/doc/EQ架構/完整提案說明.md)

## 2. EQ Preset

目前系統先以一組人工整理的 `preset EQ` 作為推薦候選。

這些 preset 的角色是：

1. 作為代表性的聲音原型（sound archetypes）
2. 作為 tree 搜尋的候選終點
3. 作為 coarse-to-fine 調整的骨架

目前我們不主張：

- 這些 preset 已完整覆蓋所有人的最終偏好

而是主張：

- 它們足以作為第一版候選集合，支撐 tree-based progressive search

詳細說明：
- [完整提案說明.md](/home/parker6/Documents/project_02_ARMO/emotion_adaptive_eq/doc/EQ架構/完整提案說明.md)

## 3. EQ Tree 的建構依據和算法

EQ tree 的角色是把 preset library 轉成「可逐步探索的搜尋路徑」。

目前的建構概念是：

1. 先以 `flat` 作為 baseline
2. 比較各 preset 的差異
3. coarse 階段先用較大的頻段特徵做分群
4. 再往 medium / fine 階段做更細的切分
5. 每個節點保留：
   - 它代表的 EQ 特徵
   - 對應的候選 preset 子集
   - 該節點的局部調整值

目前節點的 `delta` 採用子集的中位數代表值，理由是：

1. 比 common core 更穩
2. 比較不會因子集合差異太大而縮得太小
3. 適合前段 coarse / medium 的有感調整

詳細說明：
- [完整提案說明.md](/home/parker6/Documents/project_02_ARMO/emotion_adaptive_eq/doc/EQ架構/完整提案說明.md)
- [Emotion回饋與搜尋策略提案草案.md](/home/parker6/Documents/project_02_ARMO/emotion_adaptive_eq/doc/EQ架構/Emotion回饋與搜尋策略提案草案.md)

## 4. Evaluation

Evaluation 要回答的問題是：

> 某一個 EQ 節點，在一段時間內的情緒表現要怎麼算？

目前的初步共識：

1. 先使用 `emotion_score` 連續值，不用 binary 當主要訊號
2. reward 需要考慮同一 EQ 下的自然波動（noise）
3. EQ 切換後第一筆資料較不穩，因此不建議只用單筆決定
4. 目前先採用 2 個 windows 聚合，例如：

```text
node_reward = 0.3 * window_1 + 0.7 * window_2
```

這個定義不是定稿，而是目前根據小規模資料得出的工程化初值。

詳細說明：
- [Emotion回饋與搜尋策略提案草案.md](/home/parker6/Documents/project_02_ARMO/emotion_adaptive_eq/doc/EQ架構/Emotion回饋與搜尋策略提案草案.md)

## 5. Decision

Decision 要回答的問題是：

> 這個節點比上一個節點好嗎？

目前的方向是：

1. 先看 reward 的相對變化：

```text
delta_reward = reward_t - reward_(t-1)
```

2. 再用 threshold 轉成：
   - `improve`
   - `stable`
   - `worsen`

目前 threshold 初值先從 `8` 開始，但已明確知道後續很可能需要：

```text
T_coarse > T_medium > T_fine
```

也就是 coarse / medium / fine 使用不同 threshold。

另外我們也注意到：

- `stable` 不只有一種意思

至少可能分成：

1. 一般 stable：代表沒有明顯資訊量，可試 sibling
2. 高分 stable：代表已接近高偏好區域，不一定應直接放棄

詳細說明：
- [Emotion回饋與搜尋策略提案草案.md](/home/parker6/Documents/project_02_ARMO/emotion_adaptive_eq/doc/EQ架構/Emotion回饋與搜尋策略提案草案.md)

## 6. Tree 探索方式

目前 tree 搜尋策略的基本概念是：

1. coarse 層先做較寬的探索
2. 找到較有希望的大方向後
3. 再在 medium / fine 階段逐步深入

目前可先理解成：

- coarse 偏 `breadth-first`
- medium / fine 偏 `depth-first`

大致規則是：

1. `improve` -> deeper
2. `stable` -> sibling
3. `worsen` -> fallback

但我們也已經知道，後續很可能需要加入：

1. stage-specific threshold
2. 高 reward 區域的特殊 stable 解讀
3. reward 高成本下的 budget-aware search

因此這一段目前仍屬於「可運作草案」，尚未完全定稿。

詳細說明：
- [Emotion回饋與搜尋策略提案草案.md](/home/parker6/Documents/project_02_ARMO/emotion_adaptive_eq/doc/EQ架構/Emotion回饋與搜尋策略提案草案.md)

## 7. 調參實驗規劃

目前我們已將實驗分成兩類：

1. `參數校準 / 資料蒐集實驗`
2. `正式驗證實驗`

調參實驗的目的是：

1. 估計 `window` 長度
2. 調整 `reward weighting`
3. 找出合適的 `threshold`
4. 檢查 coarse / medium / fine 是否需要不同 threshold
5. 觀察 stable / sibling / fallback 的合理規則

目前較合理的資料蒐集方向是：

1. 先讓受測者做 preset 主觀排序，記錄 `Top1 / Top2`
2. 測全部 coarse 節點
3. 再測 `Top1` 所屬分支下的全部節點與 preset
4. 每段固定收幾個 windows
5. 之後用離線 replay 來比較不同參數組合

詳細說明：
- [驗證與探索實驗規劃.md](/home/parker6/Documents/project_02_ARMO/emotion_adaptive_eq/doc/EQ架構/驗證與探索實驗規劃.md)

## 8. 驗證實驗規劃

正式驗證實驗的定位是：

> 等 reward、threshold、policy 較穩定後，再驗證完整演算法是否有效。

這時的流程應更接近真實使用情境：

1. 受測者先做 preset 排序
2. 系統實際跑一輪 adaptive search，直到 `stable`
3. 再驗證最終結果是否接近使用者主觀偏好

目前比較合適的驗證指標包括：

1. `Top-N hit rate`
2. `tree node distance`
3. `convergence steps`
4. `convergence time`

也就是說，正式驗證不是拿來調參，而是拿來回答：

- 這個演算法最後到底有沒有幫使用者找到接近喜歡的 EQ

詳細說明：
- [驗證與探索實驗規劃.md](/home/parker6/Documents/project_02_ARMO/emotion_adaptive_eq/doc/EQ架構/驗證與探索實驗規劃.md)

## 9. 個人化發展規劃

除了當次 closed-loop search 之外，我們也開始討論：

> 是否能替使用者建立可累積的偏好記憶，以降低冷啟動成本並加速收斂？

目前比較合理的第一版方向不是直接做 SVD，而是：

1. 先用 tree node 的 feature tag
2. 為每位使用者建立 feature-based preference vector
3. 根據正負回饋調整節點探索優先級

這樣做的角色分工是：

- tree 用 feature 定義搜尋空間
- user vector 用 feature 記錄偏好權重

後續可能的演進方向包括：

1. `V1`: 純 tree-based search
2. `V2`: feature-based preference memory
3. `V3`: contextual bandit / shared prior / latent factor

詳細說明：
- [個人化先驗與偏好記憶研究草案.md](/home/parker6/Documents/project_02_ARMO/emotion_adaptive_eq/doc/EQ架構/個人化先驗與偏好記憶研究草案.md)

## 文件索引

目前主要文件如下：

1. [完整提案說明.md](/home/parker6/Documents/project_02_ARMO/emotion_adaptive_eq/doc/EQ架構/完整提案說明.md)
   - 上位提案文件，整理整體問題定義與系統定位
2. [Emotion回饋與搜尋策略提案草案.md](/home/parker6/Documents/project_02_ARMO/emotion_adaptive_eq/doc/EQ架構/Emotion回饋與搜尋策略提案草案.md)
   - reward、decision、search policy 的工作草案
3. [驗證與探索實驗規劃.md](/home/parker6/Documents/project_02_ARMO/emotion_adaptive_eq/doc/EQ架構/驗證與探索實驗規劃.md)
   - 參數校準 / 資料蒐集實驗與正式驗證實驗規劃
4. [個人化先驗與偏好記憶研究草案.md](/home/parker6/Documents/project_02_ARMO/emotion_adaptive_eq/doc/EQ架構/個人化先驗與偏好記憶研究草案.md)
   - 個人化先驗與使用者偏好記憶的研究方向
5. [議題整理.md](/home/parker6/Documents/project_02_ARMO/emotion_adaptive_eq/doc/EQ架構/議題整理.md)
   - 議題脈絡與待決問題整理
