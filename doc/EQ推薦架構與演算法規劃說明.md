# EQ 推薦架構與演算法規劃說明

Date: 2026-04-10

## 1. 文件目的

本文件整理目前專案對 EQ 調整演算法的整體構思，說明：

1. 為什麼本專案將問題定義成 `preset-based personalized recommendation`，而不是完整的 EQ 分類問題
2. EQ preset 的選擇理由與數量需求應如何描述
3. EQ 變化的方法、tree 切分邏輯、以及目前已實作的演算法細節

本文件的定位是規劃說明，不是數學上完整證明；目的在於建立一套對內對外都可一致描述的方法論。

## 2. 問題定義：我們做的是推薦問題，不是完整分類問題

### 2.1 為什麼不是 27 類分類問題

若將 EQ 偏好空間簡化成：

- `low`
- `mid`
- `high`

三個主區段，並假設每個區段只有三種狀態：

- `boost`
- `neutral`
- `cut`

那理論上可以形成 `3 x 3 x 3 = 27` 種組合。

這種定義方式在概念上是成立的，但不適合作為目前專案的產品化起點，原因有三個：

1. 我們沒有足夠依據去定義 27 組 EQ 都是有代表性、可辨識、且有實際價值的 preset。
2. EQ 不只取決於方向，還取決於幅度，因此若要完整覆蓋所有可能性，實際空間會遠大於 27。
3. 即使建立 27 組 preset，也不代表它們都能形成穩定、可感知、可區辨的使用者選擇。

因此，本專案目前不把問題定義成「窮舉所有可能 EQ 組合」，而是定義成：

> 在一組具有代表性與外部依據的 EQ preset 候選集合中，透過情緒回饋做漸進式個人化推薦。

### 2.2 我們目前的核心定位

本系統的角色是：

1. 先建立一組高價值的 EQ preset library
2. 將這些 preset 轉成可逐步探索的 decision tree
3. 根據使用者對不同頻段調整方向的情緒回饋，逐步推定偏好
4. 收斂到最適合的 preset，最後再做細部貼合

也就是說：

- preset library 是 `候選集合`
- tree 是 `搜尋結構`
- emotion feedback 是 `個人化依據`

## 3. EQ preset 的選擇理由

### 3.1 preset 的角色

目前 preset 並不被定義成「所有人最終都會喜歡其中一個固定答案」，而是：

> 一組具有代表性的聲音原型（sound archetypes），作為搜尋空間的候選骨架。

系統的目標不是要求使用者一定要完全落在某個原始 preset 上，而是先透過這些 preset 快速定位偏好方向，再做後續 refine。

### 3.2 preset 的來源依據

目前合理的 preset 來源可包含：

1. 文獻或既有調音曲線支持，例如 Harman
2. 音樂平台、耳機產品、常見音色類型
3. 工程與聽感評估後認為具代表性的調音

因此，preset library 的建立原則不是「排列組合完整覆蓋」，而是「代表性、可分性、可用性」。

### 3.3 preset 數量如何描述

對目前專案來說，較合理的說法不是「我們證明 12 個一定足夠」，而是：

> 我們先建立一組可涵蓋主要聲音偏好方向的候選集合，並驗證該集合是否足以支撐穩定的 tree 搜尋與個人化 refine。

也就是說，preset 數量是一個工程設計量，而不是先驗真值。

### 3.4 是否有最低需求數目

在目前的 tree-based recommendation 架構下，可以給出一個工程上的最低需求概念：

1. 若希望 coarse tree 至少能形成 3 個主要群組，且每群內仍保有進一步搜尋空間，實務上 learnable preset 不宜太少。
2. 若每個 coarse 群組只有 1 個 preset，tree 會很快退化成直接選單，失去 progressive search 的意義。
3. 因此，第一版至少應有足以形成多個 coarse 群與子群的數量。

以目前專案的經驗可描述為：

- `9` 組 learnable preset 可視為最低可行規模
- `12` 組 learnable preset 是較合理的第一版規模，因為可支撐例如 `4 / 4 / 4` 的 coarse 分群

這不是理論下限，而是基於 tree 搜尋穩定性與可分性的工程下限。

## 4. 個人化依據是什麼

本系統的個人化依據，不是先驗地假設某使用者屬於哪一類 EQ，而是：

> 根據使用者對不同頻段調整方向的情緒回饋差異，逐步推定其偏好方向。

例如系統會逐步判斷：

- 使用者是否對高頻增加有正向反應
- 使用者是否偏好中頻前移或後退
- 使用者是否喜歡更強的低頻量感

因此，本系統的個人化是「回饋驅動的偏好估計」，而不是「預先標籤式分類」。

## 5. EQ tree 如何切分

### 5.1 tree 的功能目的

tree 的目的不是直接表示完整 preset 本身，而是：

> 將 preset library 轉成一個可漸進式搜尋的路徑結構。

每一層的工作都是：

1. 找出當前候選 preset 之間差異最大的頻段特徵
2. 用該特徵做分群
3. 讓系統先判定使用者在這個特徵上的偏好方向
4. 再進一步縮小候選範圍

### 5.2 現在的切分邏輯

目前實作中：

1. coarse 層特徵是 `low / mid / high` 這類大區段
2. 系統會在 coarse feature 中，選出最能區分目前 preset 候選集合的區段作為第一層 split
3. 在 medium 層，系統改用 band pair，例如：
   - `b1_2`
   - `b3_4`
   - `b5_6`
   - `b7_8`
   - `b9_10`
4. 在 fine 層，系統可進一步下探到單一 band

也就是：

- 第一層先做大方向判斷
- 第二層再做局部特徵判斷
- 最後用 finer step 收斂到單一候選

### 5.3 coarse 分群目前如何實作

目前 coarse 層不是只看單一 band 平均值，而是：

1. 取候選 preset 在某 coarse 區段上的局部曲線向量
2. 用 L1 距離做 medoid-based clustering
3. 分成 `3` 或 `4` 個 coarse bucket
4. 再做平衡調整，使 coarse 層分群盡量平均

目前已支援：

- `--coarse-buckets 3`：`boost / neutral / cut`
- `--coarse-buckets 4`：`boost / neutral / cut / strong_cut`

並支援 coarse band 邊界設定，例如：

- `0-3,4-6,7-9`

這些邏輯實作在：

- [tree_builder.py](/home/parker6/Documents/project_02_ARMO/emotion_adaptive_eq/emotion_eq_engine/tree_builder/tree_builder.py)
- [build_tree.py](/home/parker6/Documents/project_02_ARMO/emotion_adaptive_eq/emotion_eq_engine/demo/build_tree.py)

## 6. 每個節點的調整值怎麼來

### 6.1 目前做法

在每個 tree 節點，我們不直接使用「完整 preset 值」，而是給節點一個局部的 `delta_curve`。

目前 `delta_curve` 的設定方式是：

> 取該子集中所有 preset 在該特徵區段上的代表值，使用中位數作為節點調整值。

### 6.2 為什麼不用 common core

討論過的另一種做法，是使用所謂「最大公因曲線 / common core」，也就是只取子集中共同擁有的調整部分。

最後沒有採用的原因是：

1. 若子集合內 band 差異太大，common core 會快速變小
2. coarse/medium 階段可能因此變得不夠有感
3. 本系統本來就有「單一候選後 full refine」機制，因此前段不必過度保守

因此目前維持中位數更合理：

- 可保留足夠調整量
- 可讓前段搜尋更穩、更有感
- 不影響最後精修到完整 preset 的能力

## 7. EQ 變化的方法：coarse-to-fine 調整

### 7.1 基本原則

EQ 變化採用 progressive adjustment：

1. 初期變化要夠明顯，讓使用者情緒回饋能有效區分方向
2. 後期逐步細修，避免過度震盪

### 7.2 目前實作的 step scheduler

目前 scheduler 設定為：

1. `coarse`
   - 前 8 步
   - `step_size = 4 dB`
   - `band_width = 4`
2. `medium`
   - 第 9~16 步
   - `step_size = 2 dB`
   - `band_width = 2`
3. `fine`
   - 第 17 步之後
   - `step_size = 1 dB`
   - `band_width = 1`

對應實作：

- [step_scheduler.py](/home/parker6/Documents/project_02_ARMO/emotion_adaptive_eq/emotion_eq_engine/optimizer/step_scheduler.py)
- [eq_optimizer.py](/home/parker6/Documents/project_02_ARMO/emotion_adaptive_eq/emotion_eq_engine/optimizer/eq_optimizer.py)

### 7.3 運作方式

每一步：

1. 決定目前的 target EQ
2. 只在當前 focus band 上更新
3. 挑出與 target 差距最大的 band 優先調整
4. 依照當前 stage 的 step size 漸進靠近

## 8. 目前是否需要數據

### 8.1 第一版演算法不需要大量資料

要建出第一版系統，不需要先有大量情緒資料集。

第一版需要的是：

1. 一組可用的 preset library
2. 一個能提供情緒回饋的輸入來源
3. 一套能驗證 traversal 是否合理的測試流程

目前專案使用：

- preset library
- `SEDU` 類型資料流 / sample CSV
- fixed tree snapshot

已能完成 prototype 驗證。

### 8.2 第二版優化需要資料

若要回答以下問題，則需要資料：

- preset 數量是否足夠
- coarse band 邊界怎麼切最好
- coarse bucket 應該是 3 還是 4
- `4/2/1 dB` 的 step 是否合理
- fallback 是否太敏感

因此資料在第一版不是 prerequisite，但在第二版一定是必要條件。

## 9. 總結

目前最合理的系統說法是：

1. 本專案不是完整 EQ 組合空間分類，而是候選集合上的個人化推薦問題
2. 我們先建立一組具有代表性與外部依據的 EQ preset library
3. 再從這些 preset 之間的差異建立 coarse-to-fine 的搜尋樹
4. 系統根據使用者對不同頻段調整方向的情緒回饋，逐步推定偏好
5. 最後收斂到最適合的 preset，並做 full preset refine

這樣的架構同時滿足：

- 可解釋性
- 可實作性
- prototype 階段資源可承受
- 後續可擴充性
