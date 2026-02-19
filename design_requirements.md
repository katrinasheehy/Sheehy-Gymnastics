# 📋 Sheehy All-Around - Design Requirements (v2.3)

## **1. Core Objective**
A unified, family-centric dashboard to track and visualize gymnastics progress for Annabelle, Azalea, and Ansel. Normalizes data across Men's/Women's disciplines and provides context for scores.

---

## **2. User Profiles**
| Gymnast | Level | Theme Color | Events |
| :--- | :--- | :--- | :--- |
| **Annabelle** | Level 3 (W) | Pink (`#FF69B4`) | VT, UB, BB, FX |
| **Azalea** | Level 4 (W) | Purple (`#9370DB`) | VT, UB, BB, FX |
| **Ansel** | Level 4 (M) | Teal (`#008080`) | FX, PH, SR, VT, PB, HB |

---

## **3. Data Pipeline & Storage**
### **A. "Save & Scoop" Workflow**
* **Input:** Manual HTML saves from MSO to `ansel_history/`.
* **Processor:** `process_all_history.py` parses metadata and scores.

### **B. Data Schema (`cleaned_gymnastics.csv`)**
* **Core:** `Date`, `Gymnast`, `Meet`, `Session`, `Level`, `Division`.
* **Overall Performance:** `Meet_Rank`, `Meet_Rank_Total`.
* **Event Scores & Ranks:** * Scores: `VT`, `UB`, `BB`, `FX`, `PH`, `SR`, `PB`, `HB`, `AA`.
    * **Ranks:** Each event must have a corresponding rank column (e.g., `VT_Rank`, `UB_Rank`, `AA_Rank`).
* **Context (PLANNED):** `Session_Average`, `Session_Median`.

 ### **C. Session Context Pipeline (NEW)**
* **Objective:** Collect EVERY athlete's score for sessions attended by the Sheehy kids in 2026.
* **Input:** Automatically derived from `cleaned_gymnastics.csv` (2026 rows).
* **Storage:** `session_raw_data.csv` (Full session table).
* **Validation:** Script must confirm "Athletes Found" matches "Meet_Rank_Total" from the primary CSV.
---

## **4. Feature Requirements**
### **A. Dashboard UI**
1. **Summary Header:** Rank Badge ("🏆 Rank: X / Y") and Session Info.
2. **Score Cards:** 3-decimal display for specific gymnast events.
3. **Trend Visualization:** Line chart of All-Around (AA) scores.

### **B. Advanced Analytics**
1. **Event Drill-Down:** View history/trend for a single event (e.g., "Just Beam").
2. **Consistency Tracking:** Standard Deviation per event (Stable vs. Volatile).
3. **Judge Consistency:** Compare score vs. Session Average (+/- Diff).

---

## **5. Live Tracking Mode (Real-Time)**
* **Objective:** Dynamic updates during a meet via a **Local Agent** script.
* **Live Features:** Auto-refresh, Dynamic Rank, Projected Finish (e.g., "Needs 9.2 on Floor for PB").

---

## **6. Technical Constraints**
* **Cloud Blocking:** MSO blocks Cloudflare. Requires local HTML saves or local agent.
* **Deduplication:** Must keep "last" entry to allow data enrichment of existing meets.

---
Session Context Analytics Framework (v1.0)I. Core Analytical MetricsFor every event at every meet, the following metrics will be calculated to provide a 360-degree view of the performance:Metric 1: Session Median (The Anchor)Description: The middle value of all scores in the session/level.Purpose: Establishes the judge's baseline for the day. It accounts for "tight" vs. "loose" scoring.Metric 2: Session Max (The Ceiling)Description: The highest score awarded in that session/level.Purpose: Defines the upper limit of what the judge considered "perfection" for that specific group.Metric 3: Percentile Rank (The Magnitude)Description: The percentage of the field the child outscored (e.g., Top 10%).Purpose: Normalizes ranking across different session sizes (e.g., being 7th out of 152 is different than 7th out of 10).Metric 4: Judge Strictness Index (JSI) (The "Weather")Description: The numerical difference between the current session's median and the child’s season-long average median for that level.Purpose: Proves mathematically if the meet was "harder than usual."II. Data Hygiene & Exclusion RulesTo prevent "garbage in, garbage out" math, the following scores are excluded from group baselines:The "Scratch" Rule: All 0.0 or "DNS" scores are removed.The "Fall" Filter: Scores more than 2.5 Standard Deviations below the median are excluded. This removes "catastrophe" outliers (multiple falls/equipment failure) that don't reflect the judge's standard curve.The Self-Exclusion Rule: When calculating a baseline for your child, their own score is removed from the group to prevent "circular logic" in the comparison.III. The Meet Context Card (Visual Design)The card will use a Layered Horizontal Bullet Chart to visualize the child's place in the competitive world.Layer 1 (Background): A gray bar representing the score range (Min to Max) of the entire Level session.Layer 2 (Foreground): A colored, nested bar representing the range of the specific Age Division.Marker 1 (The Star): The child's score for that event.Marker 2 (The Line): The Division Median.Marker 3 (The Ghost Star): The child’s Personal Season Best for that event.Insight Text Generation"Ansel scored a 9.3. While this is lower than his last meet, he was in the Top 5% of this session of 152 athletes in Level 4D1, and the judge's median was 0.4 lower than average today."The Context Footer (Judge Strictness Index)Located at the bottom of the card to provide the final "verdict" on the scoring environment:Numeric: JSI: $-0.45$Descriptive: "Judge Mood: Significantly Stricter than Average"IV. Scope of AnalysisTotal Data Points: 655 rows across 9 PDF-harvested sessions (2026 Season).Discipline Handling: Parallel logic for Men’s (6 events) and Women’s (4 events).Groupings: Comparisons calculated at both the Session Level (150+ kids) and Division Level (Age-group specific).


## Phase 2: Session Context Analytics

### 1. Data Processing Logic
- **Exclusion Rules:** - Filter all 0.0 (Scratches/DNS) from session and division baselines.
    - Exclude "Catastrophe Outliers" (scores > 2.5 Standard Deviations below the median).
- **Metric Definitions:**
    - **Session Median/Max:** Calculated per Level across the entire session.
    - **Division Median/Max:** Calculated per specific Age Group.
    - **JSI (Judge Strictness Index):** `Current Session Median - Season Level Average Median`.
    - **Percentile Rank:** `(Number of athletes outscored / Total active athletes in session) * 100`.

### 2. UI/UX: Meet Context Cards
- **Visuals:** Layered Bullet Charts (Plotly or Altair) displaying Session vs. Division ranges.
- **Interactivity:**
    - Dashboard event scores are clickable to trigger the Context Card modal.
    - "Judge Weather" toggle on the Meet Overview page to show/hide JSI metrics.
- **Dynamic Text:** Automated generation of the performance insight sentence.
- 
## **7. Active Bug & Data Debt Tracker**
* [ ] **Data Cleanup - Ansel:** Recent imports missing Division/Session metadata.
* [ ] **Data Cleanup - Mardi Gras Meet:** Girls' data missing ranks and session info.
* [ ] **Missing Ranks:** Populate `[Event]_Rank` columns for all historical data.
* [ ] **Blank Cells:** Ensure `fillna("")` is handled in the processor to prevent app crashes.
