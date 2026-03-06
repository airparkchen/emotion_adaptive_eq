---
title: EQ新方案review

---

# Emotion-Driven EQ Adjustment System

## Technical Review Report

## 1. Proposal Overview

本提案的目標是在耳機 / 音樂 APP 中建立一個 **Emotion-Driven EQ Recommendation System**。

系統透過使用者的生理訊號（PPG）與情緒推論模型，動態調整音樂的 EQ，使使用者在聆聽過程中逐步找到能產生 **較正面情緒回饋** 的聲音設定。

核心概念為建立一個 **closed-loop EQ optimization system**：

```
Music playback
↓
Apply EQ
↓
User listening
↓
PPG signal
↓
Emotion inference
↓
EQ adjustment decision
```

系統會根據情緒回饋逐步調整 EQ，直到找到最適合該使用者的 EQ setting。

---

# 2. System Constraints and Assumptions

本提案在 prototype 階段採用以下設計假設：

1. 使用 **PPG sensor** 收集生理訊號
2. 使用 **第三方 emotion model**
3. emotion model 輸出為 **binary label**

```
Positive
Negative
```

4. 系統 **完全信任 emotion model 的輸出** 作為 reward signal
5. emotion evaluation window 約 **15 秒**

為降低變數，demo 階段會：

* 使用 **固定音樂（fixed demo music）**
* 專注驗證 EQ 調整模型

---

# 3. EQ Representation

EQ 使用 **10-band parametric EQ**。

每組 EQ 設定表示為一個向量：

```
EQ = [b1, b2, b3 ... b10]
```

每個 band 的範圍：

```
−12 dB  ~  +12 dB
```

直接在完整 EQ 空間中搜尋最佳設定是不可行的，因此系統會先定義一組 **default EQ presets**。

例：

* Harman curve
* Bass boost
* Vocal enhancement
* Bright boost
* Warm tuning
* Other designed EQ

所有 preset 會轉換為 **Airoha SDK compatible EQ vector**。

---

# 4. Core Algorithm Concept

EQ 調整模型的核心概念是：

**Emotion-guided EQ search in preset space**

系統並不是在完整 EQ 空間中搜尋，而是在 **preset space** 中逐步逼近最適合使用者的 EQ。

---

# 5. Core Technical Design

EQ 模型的主要技術點包含兩個部分：

## 5.1 Progressive EQ Adjustment (Coarse-to-Fine)

EQ 調整採用 **progressive search strategy**。

系統會先對 default EQ presets 進行分析，建立一個 **decision tree structure**。

搜尋流程採用 **coarse-to-fine 調整策略**：

### Stage 1 – Coarse Adjustment

先進行較大尺度調整，例如：

* 大頻段調整（band region）
* 大幅度調整（例如 ±4 dB）

例如：

```
Low band (1-4)
Mid band (5-7)
High band (8-10)
```

目的是快速判斷聲音偏好方向。

---

### Stage 2 – Medium Adjustment

在選定區域內進一步細分：

例如：

```
band3-4
band5-6
band8-9
```

調整幅度變小，例如：

```
±2 dB
```

---

### Stage 3 – Fine Adjustment

最後進行單一 band 微調：

```
band4
band6
band9
```

調整幅度：

```
±1 dB
```

此策略可有效減少搜尋步數。

---

# 5.2 Emotion-Driven Decision Strategy

EQ 搜尋方向由 **emotion feedback** 決定。

系統在每次 EQ 調整後會等待 emotion evaluation window。

為降低 emotion signal 的隨機波動，會採用：

```
Sliding window
Voting mechanism
```

來判斷情緒趨勢。

Decision strategy 包含三種結果：

### 1. Keep Going

情緒持續改善：

```
continue current branch
```

### 2. Switch Side

情緒沒有改善：

```
switch to alternative branch
```

### 3. Fallback

情緒變差：

```
return to previous node
```

透過此機制，系統可以在 decision tree 中逐步逼近最佳 preset。

---

# 6. Demo Scenario

Prototype demo 流程：

```
Play fixed demo music
↓
Baseline EQ
↓
Emotion evaluation
↓
AI begins EQ search
↓
Progressive EQ adjustment
↓
Emotion feedback decision
↓
Final recommended EQ
```

使用者體驗：

```
Original sound
↓
AI adjusting sound
↓
Emotion improves
↓
Recommended EQ
```

---

# 7. Data Strategy

Prototype 階段：

* 不需要事先收集大量資料
* 主要透過 **online feedback search** 驗證演算法

但系統仍會 **被動記錄運行資料**：

```
Music
EQ step
Emotion result
Final EQ
```

這些資料未來可用於：

* preset space optimization
* decision tree optimization
* user preference learning

---

# 8. Future Extension

未來產品化方向：

建立 **User Sound Profile**。

利用長期資料建立模型：

```
User
+
Music feature
→
Recommended EQ
```

讓系統不需要每次重新搜尋。

---

# 9. Key Innovation

本提案的創新點在於：

**Emotion-aware audio personalization**

系統透過生理訊號回饋，讓聲音能夠自動適應使用者。

從：

```
Manual EQ tuning
```

進一步演進為：

```
Emotion-driven adaptive audio
```

---
