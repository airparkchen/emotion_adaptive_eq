# Tree 設計與生成邏輯 Review Report

Date: 2026-03-05

## 1. 目的

本文件說明目前 EQ decision tree 的設計原則、生成流程、執行時如何被使用，以及目前已知限制。

## 2. 設計目標

目前 tree 的目標是：

1. 讓 EQ 搜尋具備 `coarse -> medium -> fine` 的漸進性。
2. 每個節點可解釋（節點有明確 delta 調整）。
3. 每個節點可追蹤候選 preset (`candidate_presets`)。
4. 在候選收斂到單一 preset 後，交由 engine 做完整 preset 精修。

## 3. Tree 結構（Node Schema）

每個節點包含：

- `name`: 節點名稱（例如 `mid:cut`、`b1_2:+4.0`）
- `stage`: `root/coarse/medium/fine`
- `feature`: 當前分裂依據特徵
- `delta_curve`: 此節點定義的 10-band 局部調整
- `band_indices`: 本節點主要作用 band
- `candidate_presets`: 走到此節點時仍可能的 preset
- `children`: 子節點

## 4. 生成流程

### 4.1 輸入與前處理

1. 讀取 `preset_library.json`。
2. 以 `flat` 為 baseline，計算各 preset 的 delta 向量。

### 4.2 分層特徵定義（可調）

- `coarse`: `low(1-4), mid(5-7), high(8-10)`
- `medium`: `b1_2, b3_4, b5_6, b7_8, b9_10`
- `fine`: `b1 ... b10`

說明：

- `coarse` 的 band 分段可由 build 指令調整（`--coarse-bands`）。
- `coarse` bucket 數可設定為 `3` 或 `4`（`--coarse-buckets`）。

### 4.3 Coarse 分群策略（目前版本）

coarse 層採用「區段曲線形狀分群」：

1. 對候選 preset 取 coarse 區段向量。
2. 使用 medoid-based clustering（L1 距離）分成 `k` 群（`k=3/4`）。
3. 進行平衡分配（rebalance），使群組大小盡量平均（例如 12 筆可達 4/4/4）。
4. 依群組中心均值由高到低映射語意標籤：
   - 3 群：`boost / neutral / cut`
   - 4 群：`boost / neutral / cut / strong_cut`

此方式避免僅靠單一平均值造成的錯分，並兼顧分群穩定性與可讀性。

### 4.4 Medium/Fine 分裂策略

在 medium/fine 層，對特徵值做量化 token（例如 `+4`, `-2`），選擇可有效分離候選 preset 的特徵建立子節點。

### 4.5 節點 delta 設定

節點 `delta_curve` 採候選 preset 在該特徵區段的代表值（中位數）寫入，以降低 outlier 影響。

## 5. Runtime 如何使用 Tree

1. Emotion evaluator 輸出 `improve/stable/worsen`。
2. Decision policy 決定 `keep/switch/fallback`。
3. Engine 取得目前路徑節點 delta，形成路徑目標。
4. 若 `candidate_presets == 1`，目標切換為該 preset 的完整 10-band（精修模式）。
5. Optimizer 按 stage 逐步更新 EQ（幅度 + band width 控制）。

## 6. 為何 Tree 葉節點不一定等於完整 Preset

Tree 主要負責「路徑式搜尋與候選收斂」，不是直接保證葉節點即完整 preset。

完整 preset 對齊由 engine 在單一候選時接手完成（full-band refine）。

## 7. 當前優點

1. 可解釋：每步可看到節點調整 band 與 dB。
2. 可觀測：有 JSON 與 Markdown 兩種 snapshot 輸出。
3. 可維護：改 preset 後可固定重建 snapshot，runtime 只載入固定樹。

## 8. 當前限制

1. balanced clustering 是啟發式方法，非全域最優解。
2. 若 preset 非常相似，medium/fine 仍可能較淺。
3. policy 目前尚未加入「連續負面 N 次才 fallback」遲滯機制。

## 9. 建議下一步

1. 加入 `negative_streak` 與 fallback 門檻（N 次 worsen 才回退）。
2. 加入 branch cooldown 防止分支震盪。
3. 對 snapshot.md 增加「累積路徑目標」欄位，讓閱讀更直覺。
