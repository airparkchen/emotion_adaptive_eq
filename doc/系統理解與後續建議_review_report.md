# 系統理解與後續建議 Review Report

Date: 2026-03-05

## 1. 我目前理解的核心需求

你的核心需求是：

1. 先固定建出一棵可重現的 EQ 決策樹。
2. runtime 不重建樹，只做情緒回饋驅動 traversal。
3. EQ 調整必須有「初期有感、後期細修」的體感。
4. 最終可以收斂到某一 preset，並在必要時回退重新探索。

## 2. 目前系統已達成的事情

1. 已分成兩個任務：
   - 分析建樹任務（build tree snapshot）
   - EQ 模型任務（load tree + emotion loop）
2. 支援 tree snapshot 輸出與載入：
   - `data/tree_snapshot.json`
   - `data/tree_snapshot.md`
3. 支援 SEDU 類型資料流輸入，loop 不會因 EOF 中斷。
4. 已實作 coarse/medium/fine 漸進式 optimizer。
5. 已實作收斂到單一候選後的 full preset refine。
6. coarse 層已改為曲線形狀分群（非單純平均值），並可平衡分配。
7. coarse bucket 數與 low/mid/high band 邊界可由 build 指令調整。

## 3. 目前你可能會感到「不直覺」的點

1. tree 節點不是完整 preset，而是局部調整。
2. 葉節點不等於最終 EQ，最終 EQ 要看 runtime 的 refine。
3. 當情緒持續變差時，policy 會 fallback，可能看起來像「已到目標又離開」。

這三點都是目前架構預期行為。

## 4. 對產品化最重要的三件事

1. 回退策略穩定化
   - 加 `連續負面 N 次才 fallback`
   - 加 branch cooldown
2. 觀測性強化
   - 每步記錄：節點、候選數、目標 preset、回退原因
3. A/B 驗證
   - 比較「無回退鎖定」vs「有回退保守策略」的情緒趨勢

補充：

- coarse 分群建議固定版本參數（例如 `--coarse-buckets 3 --coarse-bands 0-3,4-6,7-9`）並寫入發版紀錄，避免不同批次建樹不一致。

## 5. 建議短期里程碑

### Milestone A（穩定）

- 加入 negative streak + cooldown
- 增加執行 log 欄位
- 完成 3~5 組固定測試情境

### Milestone B（可評估）

- 跑離線 replay（同一批情緒序列）
- 評估指標：
  - 收斂速度
  - 回退次數
  - 最終情緒分數

### Milestone C（可展示）

- Demo 顯示：
  - 當前節點
  - 候選 preset 收斂
  - EQ 曲線變化

## 6. 整體判斷

目前系統已經不是概念稿，而是可運作的 MVP。

若以你的目標「情緒驅動適應性漸進 EQ 推薦」來看，主要剩餘工作不是再改大架構，而是把策略穩定性和可觀測性補齊。
