# Emotion 回饋與搜尋策略規格草案

> Note
> 本文件已由 `doc/EQ架構/Emotion回饋與搜尋策略提案草案.md` 接手持續維護。
> 此檔案保留作為歷史版本參考，後續請以 `doc/EQ架構/` 內文件為主。

Date: 2026-04-14

## 1. 文件定位

本文件是一份 V1 草案，用來定義目前 EQ 自適應演算法中的：

1. emotion 回饋如何被使用
2. 如何從 emotion 回饋得到 decision trend
3. tree 應如何被搜尋

這不是最終產品規格，而是一份可供後續討論與實驗設計延伸的初始版本。

## 2. 設計原則

本草案採用以下原則：

1. emotion model 不直接輸出 EQ 調整方向
2. emotion model 只提供某一節點的 `reward signal`
3. tree 的 traversal direction 由 `reward + policy` 決定
4. coarse 階段優先避免大方向判錯
5. fine 階段優先加速收斂

## 3. V1 系統拆分

### 3.1 Evaluation

定義：

> 對某一個 EQ 節點，在固定時間窗內取得 emotion reward。

V1 假設：

1. 一個 EQ 節點對應一個固定 observation window
2. 在該 window 內取得 emotion model 輸出
3. 用該 window 內的平均 emotion score 作為該節點 reward

也就是：

```text
node_reward = average(emotion_scores_within_window)
```

### 3.2 Decision

定義：

> 比較目前節點與上一個節點的 reward，將差值轉成 trend。

V1 假設：

1. 以 reward 差值作為 decision 依據
2. 定義一個 threshold `T`
3. 轉換規則：
   - `delta > +T` -> `improve`
   - `delta < -T` -> `worsen`
   - 其餘 -> `stable`

也就是：

```text
delta_reward = reward_t - reward_(t-1)
```

### 3.3 Search Policy

定義：

> 根據當前 trend，決定 tree 下一步 traversal action。

V1 假設：

1. coarse 層使用偏 breadth-first 策略
2. medium / fine 層使用偏 depth-first 策略
3. policy mapping：
   - `improve` -> deeper
   - `stable` -> sibling
   - `worsen` -> fallback

## 4. V1 emotion input spec 假設

本草案先不綁定特定 emotion model，但提出一組 V1 使用假設。

### 4.1 輸出格式

V1 建議優先支援 continuous score，例如：

- `-1.0 ~ +1.0`

原因：

1. 比 binary label 更容易比較節點差異
2. 比較容易做平均與 threshold 設定
3. binary 可作為 fallback，但資訊量較少

### 4.2 Observation Window

V1 規劃：

1. 每個 EQ 節點至少觀察一個固定時間窗
2. 實際秒數需受 emotion model 的最短有效窗口限制
3. 若模型需要 15 秒才能做一次可靠預測，則 decision cadence 不應快於 15 秒

因此 V1 不先寫死秒數，而是定義：

> `evaluation_window >= emotion_model_minimum_valid_window`

### 4.3 Reward 定義

V1 reward 使用：

```text
node_reward = mean(window_scores)
```

這是最簡單、最容易落地的版本，後續若有需要，可再擴充成：

- weighted mean
- confidence-weighted mean
- trend-weighted score

## 5. V1 traversal 策略

### 5.1 coarse 階段

coarse 階段的主要風險是：

> 若第一層方向判錯，後續搜尋會整段偏掉。

因此 V1 建議 coarse 層採用偏 breadth-first 策略：

1. 每個 coarse 主要分支至少試一次
2. 比較各 coarse 節點 reward
3. 選擇表現最好的 coarse 分支往下

這樣可降低一開始就走錯大方向的機率。

### 5.2 medium / fine 階段

進入 medium / fine 後，候選範圍已縮小，V1 建議改用偏 depth-first 策略：

1. 若節點帶來改善，優先往下走
2. 若節點沒有明顯改善，改試同層 sibling
3. 若節點明顯變差，退回 parent

## 6. V1 policy mapping

V1 定義：

### 6.1 improve

條件：

```text
reward_t - reward_(t-1) > +T
```

行為：

- 保留目前方向
- 往當前節點更深層 child 前進

### 6.2 stable

條件：

```text
abs(reward_t - reward_(t-1)) <= T
```

行為：

- 不直接判定當前方向錯誤
- 先試同層 sibling，取得更多區辨資訊

### 6.3 worsen

條件：

```text
reward_t - reward_(t-1) < -T
```

行為：

- 視為目前方向不佳
- fallback 到 parent

## 7. V1 stopping criteria

V1 先定義一個可討論的停止條件：

1. 若候選收斂到單一 preset，進入 full preset refine
2. refine 階段若連續 2~3 次 trend 為 `stable`
3. 或達到最大步數
4. 則視為得到暫時 stable EQ

此處的 stable EQ 不代表永久不再改變，而代表：

> 在當前音樂與當前回饋條件下，系統已收斂到一個可接受的穩定解。

## 8. V1 的限制

這個版本的目的是先讓系統具備可討論、可實驗、可量測的閉環行為，因此有幾個刻意保留的簡化：

1. 尚未加入 confidence-based gating
2. 尚未加入 negative streak / hysteresis
3. 尚未加入 best-known-node memory
4. 尚未加入 branch cooldown
5. 尚未根據不同 tree 深度調整不同 threshold

## 9. 後續可以延伸的方向

若 V1 可以順利跑通，後續可逐步擴充：

1. `Evaluation`
   - 改成 weighted average
   - 引入 confidence
2. `Decision`
   - 加入連續 worsen 才 fallback
   - 加入 adaptive threshold
3. `Policy`
   - coarse 層多臂 bandit / beam search
   - fine 層局部 hill-climbing
4. `Stopping`
   - 加入穩定性與時間上限雙重條件

## 10. 總結

V1 草案的核心不是求最佳，而是先定義出一套最小可運作的 closed-loop 規格：

1. 用固定 window 計算節點 reward
2. 用 reward 差值判斷 improve / stable / worsen
3. coarse 用 breadth-first、medium/fine 用 depth-first
4. 用單一候選後 full refine 完成收斂

這一版最適合作為後續實驗設計與規格討論的起點。
