---
title: EQ新方案專案架構

---

先給結論：
你這個專案的程式其實可以拆成 **5–6 個核心模組**，對應提案中的兩個核心技術點：

1️⃣ **EQ 漸進調整（coarse → fine）**
2️⃣ **emotion feedback 決策（tree traversal）**


---

# 一、核心程式模組規劃

整個 EQ model 系統可以拆成 6 個模組。

```text
emotion-adative-eq
│
├── preset
├── tree_builder
├── eq_optimizer
├── emotion_evaluator
├── decision_policy
└── controller
```

下面逐一說明。

---

# 1. preset module

**功能：管理 default EQ presets**

負責：

* 定義 preset
* 轉換為 10-band vector
* 供演算法使用

例如：

```python
EQ = [b1,b2,b3,...b10]
```

可能會包含：

```python
harman
bass_boost
vocal
bright
warm
```

資料形式可能是：

```json
{
  "harman":[...],
  "bass_boost":[...]
}
```

建議檔案：

```
preset/
    preset_manager.py
    preset_library.json
```

---

# 2. tree_builder module

**功能：將 preset 分析成 decision tree**

負責：

* 分析 preset vectors
* 生成 decision tree
* 支援 coarse-to-fine

例如：

```text
root
 ├─ high boost
 │    ├─ bright
 │    └─ vocal
 └─ bass boost
```

主要輸出：

```python
TreeNode
```

檔案：

```
tree_builder/
    tree_builder.py
    tree_node.py
```

---

# 3. eq_optimizer module

**功能：EQ 漸進調整**

這個模組負責：

```text
coarse → medium → fine
```

例如：

Stage1

```
band group adjustment
```

Stage2

```
band pair
```

Stage3

```
single band
```

輸出：

```python
next_eq_setting
```

檔案：

```
optimizer/
    eq_optimizer.py
    step_scheduler.py
```

---

# 4. emotion_evaluator module

**功能：情緒評估**

處理：

```
emotion window
emotion smoothing
vote mechanism
```

例如：

```python
window_size = 3
vote = majority
```

輸出：

```python
emotion_trend
```

例如：

```text
positive
negative
neutral
```

檔案：

```
emotion/
    emotion_buffer.py
    emotion_vote.py
```

---

# 5. decision_policy module

**功能：決定 tree traversal**

核心邏輯：

```text
keep going
switch side
fallback
```

輸入：

```python
emotion_trend
current_node
```

輸出：

```python
next_node
```

檔案：

```
policy/
    decision_policy.py
```

---

# 6. controller module

**功能：整體 orchestration**

負責：

```text
EQ step
→ apply EQ
→ wait emotion
→ evaluate
→ next decision
```

這是整個系統的主流程。

檔案：

```
engine/
    eq_engine.py
```

---

# 二、整體資料流

整體流程會是：

```text
Preset Manager
      ↓
Tree Builder
      ↓
EQ Optimizer
      ↓
Apply EQ
      ↓
Emotion Evaluator
      ↓
Decision Policy
      ↓
Next Node
```

形成：

```text
closed loop
```

---

# 三、Repo 命名建議

repo 名稱我會建議**偏工程模組名稱**，不要太學術。

推薦幾個。

### 1️⃣ 最推薦

```
emotion-eq-engine
```

優點：

* 清楚
* 模組導向
* 未來可 productize

---

### 2️⃣ 偏研究型

```
emotion-driven-eq
```

---

### 3️⃣ 偏系統型

```
adaptive-eq-engine
```

---

### 4️⃣ 偏 audio 技術

```
emotion-audio-tuning
```

---

# 我最推薦

```
emotion-eq-engine
```

因為你的專案其實是：

```text
EQ optimization engine
```

---

# 四、repo 結構建議

```text
emotion-eq-engine
│
├── preset
│
├── tree_builder
│
├── optimizer
│
├── emotion
│
├── policy
│
├── engine
│
├── tests
│
└── demo
```
