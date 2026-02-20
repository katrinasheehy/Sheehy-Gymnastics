# 📋 Sheehy All-Around - Design Requirements (version 2)

## **1. Core Objective**
A unified, family-centric dashboard to track and visualize gymnastics progress for Annabelle, Azalea, and Ansel. Normalizes data across Men's/Women's disciplines and provides context for scores.

---

## **2. User Profiles**
| Gymnast | Level | Theme Color | Events |
| :--- | :--- | :--- | :--- |
| **Annabelle** | Level 3 (W) | Pink (`#FF69B4`) | VT, UB, BB, FX |
| **Azalea** | Level 4 (W) | Purple (`#9370DB`) | VT, UB, BB, FX |
| **Ansel** | Level 4 (M) | Teal (`#008080`) | FX, PH, SR, VT, PB, HB |

# 🤸 Project Specification: Sheehy All-Around (Version 2.0)

This document outlines the architectural and design requirements for **Version 2.0** of the Sheehy Gymnastics Analytics App. V2 marks the transition from a standard result tracker to a high-fidelity performance analytics engine.

---

## 🏗️ 1. Data Architecture
To support advanced analytics without sacrificing speed, V2 utilizes a **Normalized Data Structure** across two distinct files.

### **File: `v2_session_context.csv`**
* **Scope:** Level-wide (analyzing every athlete in that USAG Level within the meet PDF).
* **New Primary Columns:**
    * `Level_Rank`: Standing against the entire Level population.
    * `Div_Median` / `Div_Max`: Score benchmarks for the specific Age Group.
    * `Level_Median` / `Level_Max`: Score benchmarks for the entire Level (the "Big Pond").
    * `Count`: Total number of athletes in the Level (e.g., "Out of 152").

### **File: `v2_judge_analytics.csv`**
* **Scope:** Behavioral metadata per Meet/Session/Event.
* **Metrics:**
    * `JSI_Standard`: Strictness measured against USAG National Success Markers.
    * `IQR (Interquartile Range)`: A measure of judging consistency (Lower = More Consistent).
# JUDGE ANALYTICS VERSION 2.0
# -----------------------------------------------------------------------------------------
# CALCULATION METHODS:
# 1. JSI_Standard: (Level_Median - USAG_Benchmark). Reflects absolute strictness.
# 2. JSI_Relative: (Level_Median - Meet_Average_Median). Reflects strictness relative to peers.
# 3. IQR: (Q3 Score - Q1 Score). Reflects judge consistency (Lower = More Consistent).
# -----------------------------------------------------------------------------------------
# DATA SOURCE & BENCHMARKS:
# Benchmarks derived from USAG Compulsory Scoring Guidelines (Start Value - standard execution deductions)
# and historical regional scoring medians (2023-2025).
# 
# GIRLS LEVEL 3: VT(9.2), UB(8.8), BB(8.7), FX(9.0)
# GIRLS LEVEL 4: VT(9.1), UB(8.7), BB(8.6), FX(8.9)
# BOYS LEVEL 4D1: FX(8.8), PH(8.5), SR(8.4), VT(9.2), PB(8.5), HB(8.5)
# -----------------------------------------------------------------------------------------
---

## 📈 2. Statistical Requirements

### **Percentile Logic (Excel Standard)**
V2 utilizes the **Inclusive Percentile** (`PERCENTRANK.INC`) to ensure rankings are intuitive for competitive sports.
* **Formula:** `((Count - Level_Rank) / (Count - 1)) * 100`
* **Success Metric:** A Rank **1** finish must always result in a **100.0%** standing.

### **Judge Profile Matrix**
The app must automatically synthesize `JSI` and `IQR` into human-readable behavioral labels for coaching context:

| JSI (Mood) | IQR (Consistency) | Behavioral Label |
| :--- | :--- | :--- |
| **Strict** | **Consistent** | ⚖️ Fair but Tough |
| **Strict** | **Erratic** | 🌪️ Strict & Unpredictable |
| **Average** | **Consistent** | 📖 Textbook Judging |
| **Loose** | **Consistent** | ☀️ Generous but Precise |
| **Loose** | **Erratic** | 🎢 Generous but Erratic |

---

## 🎨 3. UI/UX & Visualization

### **Nested Context Charts**
Context cards for individual events must now feature **Dual-Layer Range Bars**:
1.  **Level Bar (Light Gray):** Represents the full score range for the Level.
2.  **Division Bar (Dark Gray):** Nested inside the Level bar, representing the score range for the specific Age Group.
3.  **Gold Star:** Represents the subject's score relative to both populations.
4.  **Median Marker:** A white vertical line indicating the Level Median.

### **Scoreboard Highlights**
* **Personal Bests (PB):** Cells in the "Score" row must glow with the athlete's theme color if that score is the Season PB.
* **Sticky Navigation:** Mobile users must have access to athlete tabs (Annabelle, Azalea, Ansel) at the top of the viewport at all times.

---

## 📑 4. USAG Benchmarks (2026 Reference)
The following benchmarks are used as the "Zero Point" for calculating Judge Strictness:

| Level | Vault | Bars | Beam/Rings | Floor |
| :--- | :--- | :--- | :--- | :--- |
| **Girls L3** | 9.20 | 8.80 | 8.70 | 9.00 |
| **Girls L4** | 9.10 | 8.70 | 8.60 | 8.90 |
| **Boys 4D1** | 9.20 | 8.50 | 8.40* | 8.80 |
*\*Note: For Boys, the 8.4 benchmark applies to Rings, P-Bars, and High Bar.*

---

## 🚀 5. Deployment Strategy
* **V1 (Stable):** Hosted on the `main` branch.
* **V2 (Beta):** Hosted on the `version-2` branch for testing and live Saturday updates.
* **Merge Policy:** V2 will be merged into Main only after a full multi-user testing cycle.
