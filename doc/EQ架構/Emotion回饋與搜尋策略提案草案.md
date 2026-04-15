# Emotion 回饋與搜尋策略提案草案

Date: 2026-04-14

## 1. 文件定位

本文件是一份可持續更新的提案草案，用來定義目前 EQ 自適應演算法中的：

1. emotion 回饋如何被使用
2. 如何從 emotion 回饋得到 trend
3. tree 應如何被搜尋
4. 如何把 reward 高成本這件事納入設計

## 2. V1 基本假設

### 2.1 Evaluation

定義：

> 對某一個 EQ 節點，在固定 observation window 內取得 emotion reward。

V1 假設：

1. 一個 EQ 節點對應一個固定 observation window
2. 該 window 內取得 emotion model 輸出
3. 用該 window 內的平均 emotion score 當作節點 reward

公式：

```text
node_reward = average(emotion_scores_within_window)
```

### 2.2 Decision

定義：

> 比較目前節點與上一個節點的 reward，將差值轉成 trend。

V1 假設：

1. 使用 reward 差值
2. 定義 threshold `T`
3. 規則：
   - `delta > +T` -> `improve`
   - `delta < -T` -> `worsen`
   - 其餘 -> `stable`

公式：

```text
delta_reward = reward_t - reward_(t-1)
```

### 2.3 Search Policy

定義：

> 根據當前 trend，決定 tree 下一步 traversal action。

V1 假設：

1. coarse 層偏 breadth-first
2. medium / fine 層偏 depth-first
3. mapping：
   - `improve` -> deeper
   - `stable` -> sibling
   - `worsen` -> fallback

## 3. V1 emotion input spec 假設

### 3.1 輸出格式

V1 建議優先支援 continuous score，例如：

- `-1.0 ~ +1.0`

原因：

1. 比 binary 更容易比較節點差異
2. 容易做平均與 threshold 設定
3. binary 可作為 fallback，但資訊量較少

目前觀察補充：

1. 既有 E1(flat) / E2(主觀 Top1) 小規模資料顯示，binary 幾乎都偏正，不足以穩定區分不同 EQ。
2. `emotion_score` 連續值在不同受測者上仍能觀察到 E2 高於 E1 的趨勢，因此目前較適合作為 reward 基礎。

### 3.2 Observation Window

V1 不先寫死秒數，但先定一條原則：

> `evaluation_window >= emotion_model_minimum_valid_window`

例如若模型需要 15 秒 PPG 才能穩定估計情緒，則 decision cadence 不應快於 15 秒。

目前觀察補充：

1. 現有實驗資料中，每筆輸出約對應 13~15 秒窗口。
2. EQ 剛切換後的第一筆輸出可能受到過渡效應影響，穩定性較差。
3. 因此實務上不建議用單一第一筆作為最終 reward。

### 3.3 V1 reward 的暫定修正方向

基於目前資料觀察，V1 可從單純平均進一步修正為：

1. 每個節點至少收集 2 個連續 windows
2. 使用連續值 `emotion_score`
3. 對第一個 window 給較低權重，第二個 window 給較高權重

例如可先用：

```text
node_reward = 0.3 * window_1 + 0.7 * window_2
```

此做法的目的不是定稿，而是先反映：

1. binary 不足
2. 第一筆可能較不穩
3. reward 應採用多 window 聚合

### 3.4 根據目前資料的 reward 初步定義

目前可用的先驗資料來自 `doc/EQ_exp_data/` 中的 E1(flat) 與 E2(主觀 Top1) 比較。

初步觀察：

1. 三位受測者都能觀察到 `E2 > E1` 的方向性差異。
2. 差異量級存在個體差異，但仍落在可區分的範圍。
3. 同一 EQ 下的 `emotion_score` 仍有自然波動，因此 reward 不適合用單筆決定。

目前資料的粗略量級可先作為 V1 定義依據：

1. `E2 - E1` 的平均差距約落在 `+6.9` 到 `+28.6`
2. 同一 EQ 內的標準差約落在 `7` 到 `11`

因此 V1 先採以下定義：

```text
window_1_score = first valid window emotion_score
window_2_score = second valid window emotion_score
node_reward = 0.3 * window_1_score + 0.7 * window_2_score
```

這個定義的理由是：

1. 保留第一筆資訊，但不讓它主導結果
2. 第二筆通常較接近 EQ 切換後的穩定狀態
3. reward 仍維持為單一連續值，方便後續比較與記錄

這裡的 `0.3 / 0.7` 不是理論最優，而是根據目前觀察到「第一筆較不穩」的工程化初值。若後續資料顯示第一筆與第二筆差異沒有那麼明顯，可再調整為 `0.5 / 0.5` 或其他比例。

### 3.5 根據目前資料的 threshold 初步定義

目前不建議直接用絕對 emotion score 區間來判斷 EQ 好壞，較合理的是看 reward 的相對變化：

```text
delta_reward = reward_t - reward_(t-1)
```

threshold 的目的，是把：

1. 真正的偏好提升
2. 同一 EQ 下的自然波動
3. 模型推論噪音

區分開來。

根據目前 E1 / E2 小規模資料，可先得到兩個啟發：

1. 使用者在「普通(flat)」與「明顯偏好(Top1)」之間，reward 差距通常大於單一 EQ 內的波動。
2. 但個體差異明顯，因此 threshold 不適合直接設成非常小的數字。

因此 V1 建議先把 threshold 定義成一個可調校的 noise-aware 區間，而不是單一固定理論值。

可先使用：

```text
if delta_reward >= +8:
    improve
elif delta_reward <= -8:
    worsen
else:
    stable
```

`8` 的理由不是它已被證明最優，而是：

1. 它大致高於目前單一 EQ 內常見的局部波動量級
2. 它又沒有高到會吞掉目前資料裡較小但仍可能有意義的改善訊號
3. 它可作為後續探索實驗的起始值

因此目前應把：

- `+8 / -8`

理解成：

> 一個根據現有 E1 / E2 資料先估出的初始 decision threshold，而不是定稿。

後續若有更多資料，建議以以下方式更新：

1. 收集更多受測者在同一 EQ 下的 window-to-window 波動
2. 重新估計 noise floor
3. 檢查「主觀喜歡 vs 普通」的典型 reward 差距
4. 讓 threshold 介於 noise floor 與可感知偏好差距之間

換句話說，threshold 的更新原則不是「越小越靈敏」，而是：

> 必須大到不把 noise 誤判成 improvement，又小到不錯過真正偏好提升。

### 3.6 threshold 可能需要是 stage-specific

目前的 `+8 / -8` 只是 V1 的單一初值，但從演算法行為來看，後續較合理的方向很可能是：

```text
T_coarse > T_medium > T_fine
```

原因：

1. coarse 節點的 EQ 變化最大，理論上 reward 差異也應較大
2. medium 節點的變化較小，因此可接受較小的改善幅度
3. fine 節點通常已經接近偏好區域，邊際提升自然變小，若仍使用 coarse 等級 threshold，容易全部被判成 `stable`

因此後續探索實驗除了估計一個整體 threshold，也應檢查：

1. coarse / medium / fine 是否應使用不同門檻
2. 不同 stage 的 `improve / stable / worsen` 比例是否合理
3. 不同 stage 下，使用者是否確實呈現不同量級的 reward 變化

目前可先把 `+8 / -8` 視為：

- 一個全域初值

而不是最終版本。若後續資料支持，應改成 stage-specific threshold。

### 3.7 stable 的兩種語意

目前 V1 把 `stable` 簡化成單一類別，但實際上 stable 可能代表兩種不同情況：

1. `neutral stable`
   - child 相對 parent 沒有明顯改善
   - 也沒有明顯變差
   - 這通常代表此方向資訊量不足，可改試 sibling

2. `good stable`
   - current node 本身 reward 已經很高
   - child 只有小幅變化，沒有顯著更好
   - 這不一定表示此方向沒價值，反而可能表示系統已接近使用者的高偏好區域

這個 distinction 很重要，因為如果目標只是找到 `good enough` 的解，`stable` 可以偏向停止或換支線；但如果目標是更接近 `Top 1`，則高分區域內的小差異仍可能值得做 sibling comparison。

因此後續 decision rule 很可能需要同時考慮：

1. `delta_reward`
2. `current_reward`
3. `stage`

而不是只用單一 threshold 直接把所有 stable 視為同義。

## 4. V1 traversal 策略

### 4.1 coarse 階段

目標：

- 快速判斷大方向
- 避免第一層就走錯

V1 做法：

1. 每個 coarse 主要分支至少試一次
2. 比較各 coarse 節點 reward
3. 選 reward 最好的 coarse 分支往下

### 4.2 medium / fine 階段

目標：

- 在較小候選空間中快速收斂

V1 做法：

1. 若節點帶來改善，往下走
2. 若沒有明顯改善，試同層 sibling
3. 若明顯變差，退回 parent

補充：

- `improve / stable / worsen` 的判定目前較適合用 reward 變化區間，而不是直接用絕對 emotion score 區間。
- 原因是不同人、不同音樂、不同 session 之間可能存在基線差異，因此後續 threshold 應以變化量與 noise 為核心來定義。
- 在更接近使用者偏好區域時，reward 的邊際提升可能自然變小，因此後續 policy 不宜只用單一固定 threshold 做所有階段的判定。

### 4.3 後續可延伸的 decision 修正方向

如果後續要從 `good enough search` 往更接近 `Top 1 search` 的方向發展，較合理的修正包括：

1. coarse / medium / fine 採不同 threshold
2. 在高 reward 區域中，即使 `delta` 不大，也保留 limited sibling check
3. 將 `stable` 區分為一般穩定與高分穩定
4. 將 `current_reward` 納入 decision，而不只看 `delta_reward`

這些都代表：

> 當系統越接近使用者偏好區域時，decision rule 應該越保守地解讀小變化，避免過早停止在「還不錯」而不是「最喜歡」的節點。

## 5. V1 stopping criteria

V1 假設：

1. 若候選收斂到單一 preset，進入 full preset refine
2. refine 階段若連續 2~3 次 trend 為 `stable`
3. 或達到最大步數
4. 則視為得到暫時 stable EQ

## 6. V1 的限制

這個版本主要是先讓 closed-loop 可討論、可驗證，因此刻意保留簡化：

1. 尚未加入 confidence-based gating
2. 尚未加入 negative streak / hysteresis
3. 尚未加入 branch cooldown
4. 尚未納入 reward 高成本的 budget constraint
5. 預設會偏向追到單一 preset 再 refine

## 7. 新增的產品限制：Reward 是高成本訊號

這一點是目前必須補進設計的核心。

### 7.1 問題定義

每一次 reward 的取得都需要：

1. 套用一個 EQ 節點
2. 讓使用者實際聽一段時間
3. 等待 emotion model 完成推論

所以 reward 是高成本訊號，代表：

- tree search 不能被視為可完整展開的搜尋問題
- 必須加入時間與節點預算概念

### 7.2 因此需要補充的條件

建議後續補進以下設計條件：

1. `max_total_windows`
2. `max_total_search_time`
3. `max_tested_nodes`
4. `minimum_effective_gain`
5. `good_enough_reward`

## 8. V1.5 建議方向：Budget-aware Search

如果把 reward 高成本正式納入考量，則 V1 可往 V1.5 擴充。

### 8.1 可能的新增規則

1. coarse 層不一定每個分支都要測滿
2. 若某分支明顯較差，可提早淘汰
3. 若目前節點已夠好，可 early stop
4. 若進一步 improvement 太小，可停止深入

### 8.2 相關方法方向

可參考的思路包括：

1. multi-armed bandit / best-arm identification
2. beam search
3. successive halving
4. anytime / satisficing search

### 8.3 對目前專案較實際的版本

比較適合先做的版本是：

1. coarse 層保留 top 1~2 個分支
2. medium / fine 層沿 best branch 深入
3. improvement 小於 `T_small` 時 early stop
4. 若達到 `good_enough_reward`，不再追求最佳解

## 9. 後續討論重點

接下來最需要定下來的是：

1. emotion model 最短有效 window
2. reward 與 threshold 的初始定義
3. budget constraint
4. 是否允許停在中間節點
5. stable EQ 的正式定義

目前根據既有資料，reward / threshold 討論可先聚焦：

1. 是否固定採用兩個 windows 聚合
2. 第一筆與第二筆的加權比例
3. threshold 是否應以同一 EQ 下的自然波動作為 noise floor
