# Contextual Bandit 導入草案

Date: 2026-04-17

## 1. 文件目的

本文件用來整理目前關於 `Contextual Bandit` 的初步延伸思考，目的是：

1. 說明為什麼它值得作為後續方向
2. 說明它和目前 tree-based search 的關係
3. 釐清 bandit 可以接手哪些決策
4. 記錄目前較合理的導入路線

本文件不是要直接取代目前的手寫 policy，而是作為：

> 未來若要讓系統從 rule-based search 演進到 learning-based search 時的參考草案。

## 2. 為什麼會開始考慮 Contextual Bandit

目前的 tree-based closed-loop search 雖然已有初步可行架構，但仍有幾個自然限制：

1. reward 很昂貴
   - 每個節點都需要使用者實際聽一段時間
2. 若目標是更接近 `Top 1 EQ`
   - 可能需要試較多節點
3. cold start 情境下
   - 系統一開始對使用者沒有先驗
4. 手寫 policy 需要持續調參
   - improve / stable / worsen 的規則不一定能涵蓋所有情況

因此很自然會想到：

> 是否能讓系統從資料中學習「下一步最值得測哪個節點」，而不是完全依賴手寫 traversal 規則？

這就是 Contextual Bandit 值得被討論的原因。

## 3. 它和目前 tree search 的關係

目前最重要的共識是：

> Contextual Bandit 不一定要取代 tree，本專案更適合讓 tree 保留為搜尋空間，而讓 bandit 接手節點選擇。

換句話說：

```text
tree = search space / structure
bandit = action selection / traversal priority
```

因此比較合理的導入方式不是：

- 拿掉 tree，讓 bandit 直接控制完整 EQ 空間

而是：

- 保留 coarse-to-fine tree
- 在目前可選節點中，讓 bandit 決定下一步優先測誰

## 4. 在這個專案裡，Bandit 可能接手什麼

若導入 Contextual Bandit，它最自然可以接手的部分包括：

1. coarse 層先試哪個主分支
2. sibling 間的優先排序
3. child 與 sibling 的選擇
4. 是否值得繼續 deeper
5. 在 exploration 與 exploitation 之間如何平衡

也就是說，它會開始影響：

1. EQ 調整方向
2. tree search 的 traversal priority
3. 某種程度上的 search policy

但它不一定要一開始就負責：

1. tree 的建立
2. reward 的定義
3. preset library 的設計

## 5. 在這個問題中，Bandit 的基本元素

若將目前系統映射成 contextual bandit，可先這樣理解：

### 5.1 Action

`action` = 當前可選的下一個節點

例如：

1. 某個 coarse child
2. 某個 medium child
3. 某個 sibling
4. 某個 fallback 候選路徑

### 5.2 Reward

`reward` = 套用該節點後得到的 emotion-based reward

也就是目前我們已在討論的：

```text
node_reward = 0.3 * window_1 + 0.7 * window_2
```

因此在 bandit 架構中，emotion score 最自然的角色仍然是：

- reward signal

### 5.3 Context

`context` = 系統在選擇 action 前已知的資訊

可能包括：

1. 當前 stage
   - coarse / medium / fine
2. 當前節點的 feature
3. 目前可選節點的 feature
4. 使用者的 preference memory
5. 最近一段的情緒狀態或 trend
6. 目前已走過的 path

因此 bandit 看到的，不是「單一節點好不好」，而是：

> 在目前這個使用者狀態與路徑上下文下，哪個 action 最值得試？

## 6. Emotion score 能不能當 context

可以，但要區分清楚兩種角色：

### 6.1 當 reward

這是最自然、也最乾淨的做法。

例如：

1. 套用節點
2. 收集 2 個 windows
3. 算出 `node_reward`
4. 當成這次 action 的結果

### 6.2 當 context

也可以，但比較適合放的是：

- 當前已知的情緒狀態
- 最近一段情緒趨勢
- 與 baseline 的相對差值

而不是直接把「這次 action 的最終 reward」同時當作 action 前的 context。

因此較合理的做法是：

1. 本次測得的 `emotion_score / node_reward`
   - 當 reward
2. 前一段或最近幾段的情緒狀態
   - 當 context

## 7. 它和目前手寫 Search Policy 的關係

目前我們的 V1 Search Policy 草案是：

1. coarse 先廣度試
2. `improve` -> deeper
3. `stable` -> sibling
4. `worsen` -> fallback

若導入 bandit，這些規則不一定完全消失，但會逐步轉變成：

1. tree 先定義目前有哪些可選 action
2. bandit 根據 context 為每個 action 預估價值
3. 再決定下一步優先試誰

這代表 bandit 會開始接手：

1. child / sibling 的排序
2. 某些情況下的 fallback 決策
3. exploration / exploitation 平衡

因此可以把它理解成：

> bandit 是 Search Policy 的學習化版本，而不是 tree 的替代品。

## 8. 為什麼仍然需要先做小規模資料收集

不論最後是：

1. 手動調整超參數
2. 還是導入 Contextual Bandit

都需要先有一批小規模資料，作為：

1. reward / threshold 的校準依據
2. global prior 的初始來源
3. bandit 的 feature / context 設計參考
4. offline replay / sandbox 測試資料

因此目前較合理的順序是：

1. 先做小規模資料蒐集與參數校準
2. 先建立初版 reward / threshold / tree search baseline
3. 再評估 bandit 是否值得導入，以及適合接手哪些決策

## 9. 現階段最合理的導入路線

### V1

1. 保留手寫 Search Policy
2. 先完成 reward / threshold / window 校準
3. 收集可重播的小規模實驗資料

### V2

1. 保留 tree
2. 導入 bandit 來做 coarse child / sibling 排序
3. 先讓 bandit 接手局部 action selection，而不是整個系統

### V3

1. 將更多 traversal 決策交給 bandit
2. 與個人化 preference memory 結合
3. 視資料量與穩定度，再評估是否需要更進一步的模型化方法

## 10. 目前暫時結論

目前較合理的結論是：

1. Contextual Bandit 是值得保留的後續方向
2. 它最適合做的是：
   - 在 tree 定義好的搜尋空間中，學習下一步最值得測的節點
3. 它不應在現階段直接取代 tree
4. 目前比起先把 Search Policy 完全定死，更重要的是：
   - 先做小規模資料蒐集
   - 建立 reward / threshold baseline
   - 讓未來 bandit 導入有可依據的 global prior

一句話總結：

> Contextual Bandit 更像是 tree-based EQ search 的學習化決策層，而不是 tree 的替代品；而要走到這一步，仍然需要先有一批可用於校準與離線測試的小規模資料。
