# 第一階段 Pilot Data 實驗規劃書

Date: 2026-04-17

## 1. 文件目的

本文件用來整理第一階段 `pilot data` 實驗的規劃，目的是：

1. 作為提案時可直接說明的實驗設計文件
2. 作為後續實際執行資料蒐集時的工作草案
3. 明確界定這次實驗的目的、範圍、方法與產出

本實驗不是正式驗證演算法有效性的最終實驗，而是：

> 一個以資料蒐集與參數校準為核心的前導實驗（pilot calibration study）。

## 2. 實驗定位

本階段實驗的主要目標，不是直接證明完整 EQ 推薦系統已經能找到使用者的最終最佳 EQ，而是先取得足夠的基礎資料，用來：

1. 定義單一 EQ / 節點下的情緒波動 `noise`
2. 觀察 reward 的量級分布
3. 觀察正向 / 中性 / 負向回饋的大致區間
4. 比較不同 `window / weighting / threshold` 的候選設定
5. 支撐 V1 版本 `Evaluation / Decision / Search Policy` 的建立
6. 作為後續個人化與 `Contextual Bandit` 的初始 global prior 資料基礎

因此這個實驗的定位是：

- `pilot data collection`
- `parameter calibration`
- `tree feature validity check`

而不是：

- `final validation`

## 3. 實驗核心問題

本階段希望優先回答以下問題：

1. 在單一 EQ 條件下，emotion score 的自然波動有多大？
2. 在明顯喜歡、明顯不喜歡、以及中性條件下，reward 的量級差異是否足夠分開？
3. `4 x 15s` 的 windows 中，前幾個 window 的資訊量與穩定性如何？
4. 目前採用的 reward 定義是否合理？

```text
node_reward = 0.3 * window_1 + 0.7 * window_2
```

5. `threshold = 8` 是否是合理的初始值？
6. coarse / medium / fine 是否呈現不同量級的 reward 變化，足以支持 stage-specific threshold？
7. tree 的 coarse 特徵是否真的能把使用者帶到接近偏好的區域？

## 4. 實驗假設

本階段實驗基於以下初步假設：

1. `emotion_score` 比 binary 更適合作為 reward 基礎
2. EQ 切換後第一個 window 較不穩，需要降權或至少單獨觀察
3. `Top1`、`Bottom1`、`flat` 三類條件能提供正向 / 負向 / 中性錨點
4. coarse / deeper 節點的 reward 量級可能不同
5. 即使 coarse 沒有直接命中 Top1 branch，也仍可能具有足夠的方向辨識力

## 5. 實驗對象與前置條件

### 5.1 對象

1. 小規模內部受測者
2. 先以能穩定完成完整流程的受測者為主

### 5.2 前置條件

1. 使用固定歌曲片段
2. 使用固定 preset library
3. 使用固定 tree snapshot
4. 每個條件下維持相同音量與播放環境

## 6. 實驗流程

### 6.1 Phase 0：主觀標定

目的：

建立每位受測者的主觀偏好基準。

流程：

1. 受測者主觀聆聽所有 preset EQ
2. 記錄至少以下資訊：
   - `Top1`
   - `Bottom1`
   - `flat` 的主觀位置或分數
3. 若可行，保留全部 preset 的簡單評分或排序

這一階段的作用是建立：

- 正向條件
- 負向條件
- 中性條件

## 6.2 Phase 1：coarse 全量測

目的：

1. 觀察 coarse 三個方向的 reward 量級
2. 觀察 coarse 是否能提供足夠辨識力

流程：

1. 量測 coarse 三個主要方向
   - `boost`
   - `neutral`
   - `cut`
2. 每個條件固定播放 `4` 個 windows
3. 每個 window 約 `15 秒`
4. 每個條件總聆聽時間約 `1 分鐘`

## 6.3 Phase 2：Top1 branch 深測

目的：

1. 收集高偏好區域中的 reward 變化
2. 觀察 medium / fine 節點是否仍有可辨識的提升
3. 檢查在高 reward 區域中，stable 是否呈現特殊行為

流程：

1. 找出 `Top1 preset` 所屬的 coarse branch
2. 量測該 branch 下的全部節點與 preset
3. 每個條件固定播放 `4` 個 windows

## 6.4 Phase 3：Bottom1 branch 深測

目的：

1. 收集低偏好區域中的 reward 變化
2. 建立負向條件下的 reward / delta 分布
3. 協助後續定義 worsen 區間

流程：

1. 找出 `Bottom1 preset` 所屬的 coarse branch
2. 量測該 branch 下的全部節點與 preset
3. 每個條件固定播放 `4` 個 windows

## 6.5 Flat 穿插量測

目的：

1. 提供中性 / baseline 對照
2. 降低強烈 EQ 對下一條件的 carry-over effect
3. 觀察 session 中是否存在整體漂移

因此建議：

1. 在 coarse 條件之間插入 `flat`
2. 在 Top1 / Bottom1 branch 深測過程中，定期插入 `flat`

## 7. 需要收集的資料

每個條件至少需記錄：

1. 受測者 ID
2. 歌曲片段 ID
3. tree node / preset ID
4. stage
   - coarse / medium / fine / preset / flat
5. branch 資訊
6. 每個 window 的：
   - `emotion_score`
   - 開始時間
   - 結束時間
7. 該條件下的主觀備註（若有）

建議額外保留：

1. raw prediction
2. binary
3. stress score
4. 其他模型輸出欄位

原因是未來可能仍會想回頭檢查：

1. 是否有其他比 `emotion_score` 更穩定的訊號
2. 是否可作為 contextual bandit 或個人化的額外 context

## 8. 預期分析內容

本階段資料收集完成後，優先分析：

1. 單一 EQ / 單一節點下的 noise
2. `Top1`、`Bottom1`、`flat` 的 reward 分布差異
3. `window_1 / window_2 / window_3 / window_4` 的穩定性
4. 不同 reward 聚合方式的差異，例如：
   - `0.5 / 0.5`
   - `0.3 / 0.7`
   - 2-window、3-window、4-window 聚合
5. 不同 threshold 候選的離線表現，例如：
   - `5 / 8 / 10 / 12`
6. coarse / medium / fine 是否呈現不同 reward 量級
7. coarse 最佳分支是否落在：
   - `Top1` 所屬分支
   - `Top1 / Top2` 接近區域

## 9. 這個實驗能回答什麼

這個實驗主要能回答：

1. reward 應如何定義
2. threshold 初值應落在哪個區間
3. coarse / medium / fine 是否需要不同 threshold
4. 哪種 window / weighting 較穩
5. tree 的 coarse 特徵是否具有方向辨識力
6. 後續個人化與 contextual bandit 是否已有足夠的 global prior 基礎

## 10. 這個實驗不能直接回答什麼

這個實驗目前還不能直接回答：

1. 完整 adaptive EQ search 是否已經有效
2. 演算法是否一定能找到使用者的最終 Top1
3. 最終 Search Policy 是否已完全定稿

因此本實驗結束後，仍需要：

1. 將資料轉成正式 reward / threshold 定義
2. 固定一版 V1 Search Policy
3. 再做正式 closed-loop validation

## 11. 與後續系統發展的關係

本實驗資料將同時支撐兩條後續路線：

### 11.1 V1 rule-based 演算法

用來校準：

1. `Evaluation`
2. `Decision`
3. `Search Policy`

### 11.2 後續個人化 / Contextual Bandit

用來建立：

1. 初始 global prior
2. 各 feature / stage 的 reward 分布理解
3. 未來 contextual bandit 的 context / reward 設計參考

## 12. 暫時結論

第一階段 pilot data 實驗的定位應該清楚定義為：

> 一個為 V1 EQ 推薦演算法與後續個人化方法提供基礎資料的校準型前導實驗。

它的價值在於先建立：

1. noise 基線
2. reward 量級
3. 正中負區間
4. window / weighting / threshold 候選
5. 後續 global prior 的基礎

而不是直接作為最終產品有效性的證明。

## 13. 總結版

   ### 13.1 實驗目的

   本實驗的主要目的，是先收集足夠的前導資料，用來支撐 V1 EQ 推薦演算法的初始規格建立。重點包括：

   1. 觀察單一 EQ / 節點下的情緒波動 `noise`
   2. 觀察 reward 的量級分布
   3. 觀察正向 / 中性 / 負向條件下的回饋區間
   4. 比較 `window / weighting / threshold` 的候選設定
   5. 作為 V1 `Evaluation / Decision / Search Policy` 的校準基礎
   6. 作為後續個人化與 `Contextual Bandit` 的初始 global prior 資料來源

   ### 13.2 實驗方法

   本實驗採用固定音樂片段、固定 preset library 與固定 tree snapshot 的方式進行。  
   受測者會先完成主觀偏好標定，再進入節點級的 EQ 聆聽與 emotion 資料收集。

   量測方法的核心設計為：

   1. 使用者主觀標定 `Top1`、`Bottom1` 與 `flat` 的相對位置
   2. 量測 coarse 三個主要方向
   3. 深測 `Top1` 所在分支
   4. 深測 `Bottom1` 所在分支
   5. 在條件之間穿插 `flat`，作為 baseline 與 reset
   6. 每個條件固定量測 `4` 個 windows，每個 window 約 `15 秒`

   ### 13.3 實驗流程

   1. 受測者先聆聽全部 preset EQ，記錄主觀偏好，至少包含：
      - `Top1`
      - `Bottom1`
      - `flat` 的主觀位置或分數
   2. 依序量測 coarse 三個主要方向：
      - `boost`
      - `neutral`
      - `cut`
   3. 找出 `Top1 preset` 所屬分支，量測該分支下的全部節點與 preset
   4. 找出 `Bottom1 preset` 所屬分支，量測該分支下的全部節點與 preset
   5. 在 coarse 與 branch 測試之間穿插 `flat`
   6. 每個條件下皆記錄：
      - 每個 window 的 `emotion_score`
      - 條件對應的 tree node / preset / stage / branch 資訊
      - 必要時保留其他模型輸出欄位作後續分析

   一句話總結：

   > 本實驗是一個以資料蒐集與參數校準為核心的 pilot study，目的在於先建立 reward、threshold 與 tree decision 所需的基礎資料，而不是直接驗證最終演算法是否已經有效。
