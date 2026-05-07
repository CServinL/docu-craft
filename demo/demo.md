# 📄 Markdown Feature Showcase

This document exercises every standard Markdown feature to validate rendering consistency across all docu-craft output formats. 🚀

---

## 1. Headings

# 🏆 Heading Level 1
## 📌 Heading Level 2
### 🔍 Heading Level 3
#### ⚙️ Heading Level 4
##### 📎 Heading Level 5
###### 🔹 Heading Level 6

---

## 2. 📝 Paragraphs and Line Breaks

This is a regular paragraph. It wraps across multiple lines in the source but renders as a single block of text. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. ✍️

This is a second paragraph, separated by a blank line. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. 💬

---

## 3. ✨ Inline Formatting

- **Bold text** using double asterisks 💪
- *Italic text* using single asterisks 🎨
- ***Bold and italic*** combined 🔥
- `Inline code` using backticks 💻
- Plain text mixed with **bold**, *italic*, and `code` in a single sentence. 🧩

---

## 4. 💬 Blockquotes

> 💡 A single-line blockquote.

> 📖 A longer blockquote that spans more content. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident.

---

## 5. 📋 Unordered Lists

- 🟢 First item
- 🔵 Second item
- 🟡 Third item
- 🟠 Fourth item with **bold** and *italic* inside
- 🔴 Fifth item with `inline code` inside
- 🌍 Sixth item with a globe emoji in text

---

## 6. 🔢 Ordered Lists

1. 🥇 First step
2. 🥈 Second step
3. 🥉 Third step
4. 🏅 Fourth step with **emphasis**
5. 🎯 Fifth step

---

## 7. ➖ Horizontal Rules

Three dashes:

---

Three asterisks:

***

Three underscores:

___

---

## 8. 💾 Fenced Code Blocks

Python 🐍:

```python
def fibonacci(n: int) -> list[int]:
    seq = [0, 1]
    while len(seq) < n:
        seq.append(seq[-1] + seq[-2])
    return seq[:n]

print(fibonacci(10))
```

JavaScript 🌐:

```javascript
const greet = (name) => `Hello, ${name}!`;
console.log(greet("world"));
```

Bash 🖥️:

```bash
#!/usr/bin/env bash
set -euo pipefail

for file in *.md; do
    echo "Processing: $file"
done
```

Plain (no language tag):

```
This is a plain preformatted block.
    Indentation is preserved.
        Deeper indentation too.
```

---

## 9. 📊 Tables

### Simple Table

| Name       | Role        | Status   |
|------------|-------------|----------|
| 👩 Alice   | Engineer    | ✅ Active |
| 👨 Bob     | Designer    | ✅ Active |
| 👩 Carol   | Manager     | 🏖️ On leave |
| 👨 Dave    | QA          | ✅ Active |

### Wide Table

| ID  | First Name | Last Name | Department   | Location  | Start Date | Salary  |
|-----|-----------|-----------|--------------|-----------|------------|---------|
| 001 | Alice     | Smith     | Engineering  | 🏠 Remote | 2021-03-15 | 95,000  |
| 002 | Bob       | Jones     | Design       | 🗽 New York| 2020-07-01 | 88,000  |
| 003 | Carol     | Williams  | Management   | 🌆 Chicago | 2019-01-10 | 112,000 |
| 004 | Dave      | Brown     | QA           | 🏠 Remote | 2022-05-22 | 78,000  |

### Table with Inline Formatting

| Feature        | **Status**     | Notes                     |
|----------------|----------------|---------------------------|
| Bold in cells  | **Supported**  | Uses character style      |
| Italic in cells| *Supported*    | Uses character style      |
| Code in cells  | `Supported`    | Uses monospace font       |
| Plain text     | Supported      | Default body style        |

---

## 10. 🔗 Links

A [link to the docu-craft repository](https://github.com/CServinL/docu-craft) inline.

---

## 11. 🔬 Mixed Content

### 📈 Research Summary

This section demonstrates a realistic mix of formatting elements as they would appear in an academic or technical document.

The study involved **three experimental conditions** 🧪:

1. *Baseline* — standard configuration with no modifications
2. *Treatment A* — applied the `--fast` flag with `batch_size=64` ⚡
3. *Treatment B* — applied the `--fast` flag with `batch_size=128` 🚀

Results are summarized below:

| Condition   | Accuracy | Loss   | Duration |
|-------------|----------|--------|----------|
| Baseline    | 87.3%    | 0.412  | 42 min ⏱️ |
| Treatment A | 91.1%    | 0.301  | 28 min ⚡ |
| Treatment B | **93.4%**| **0.247** | 31 min 🏆 |

> 🏅 Treatment B achieved the best accuracy with only a marginal increase in training time compared to Treatment A.

Key findings from the `results.json` output file:

```json
{
  "best_condition": "treatment_b",
  "accuracy": 0.934,
  "loss": 0.247,
  "epochs": 50
}
```

Follow-up steps 📋:

- ✅ Validate results on the held-out test set
- 🔍 Run **ablation study** to isolate the effect of `batch_size`
- 📝 Document findings in the final *project report*

---

## 12. 🧪 Edge Cases

### Empty table cells

| A | B | C |
|---|---|---|
| 1 |   | 3 |
|   | 2 |   |

### Long unbroken words in a cell

| Column | Value |
|--------|-------|
| Hash 🔑 | a3f8b2c1d9e4f7a0b5c2d8e1f6a3b9c0d7e4f1a8b2c5d9e0f3a6b1c4d8e2f5 |

### Code block immediately after a heading ⚙️

```python
x = 42
```

### Consecutive list types 🔄

- 🔵 Bullet one
- 🟢 Bullet two

1. 1️⃣ Numbered one
2. 2️⃣ Numbered two

- 🔵 Back to bullets

### Nested Unordered Lists 🗂️

- 🌍 Continents
  - 🌎 Americas
    - 🇲🇽 Mexico
    - 🇺🇸 United States
    - 🇧🇷 Brazil
  - 🌍 Europe
    - 🇩🇪 Germany
    - 🇫🇷 France
    - 🇪🇸 Spain
  - 🌏 Asia
    - 🇯🇵 Japan
    - 🇨🇳 China
    - 🇮🇳 India
- 🌊 Oceans
  - Pacific
  - Atlantic
  - Indian

### Nested Ordered Lists 📑

1. 🧠 Machine Learning Pipeline
   1. Data Collection
      1. Raw data sources
      2. Scraping and APIs
   2. Preprocessing
      1. Cleaning
      2. Normalization
      3. Feature engineering
   3. Training
      1. Model selection
      2. Hyperparameter tuning
   4. Evaluation
2. 🚀 Deployment
   1. Containerization
   2. CI/CD pipeline
   3. Monitoring

### Mixed Nested Lists 🔀

- 📦 Project Structure
  1. Define requirements
  2. Set up repository
  3. Configure CI
- 🛠️ Development
  1. Implement core features
     - Unit tests
     - Integration tests
  2. Code review
  3. Merge to main
- 🎉 Release
  1. Tag version
  2. Publish to PyPI

### Emoji variety 🎭

Faces: 😀 😂 🤔 😎 🥳 😴 🤯 😇 🥺 😡
Nature: 🌲 🌊 🔥 ⛅ 🌙 ⭐ 🌈 🌸 🍀 🦋
Objects: 📱 💻 🖥️ ⌨️ 🖱️ 📡 🔬 🧲 💡 🔋
Symbols: ✅ ❌ ⚠️ ℹ️ 🔒 🔓 ♻️ 🏷️ 🔖 📌
Transport: 🚀 ✈️ 🚂 🚗 🛸 ⛵ 🚁 🏎️ 🛺 🚠
Food: 🍕 🍔 🌮 🍜 🍣 🥗 🍩 🍎 🥑 ☕
