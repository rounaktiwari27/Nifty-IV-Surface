# NIFTY IV Surface Reconstruction

Reconstructing missing implied volatility values across the NIFTY 50 options chain using cross-sectional smile interpolation.

---


## Problem Statement

Given partial implied volatility (IV) data across the NIFTY 50 options chain, reconstruct the complete IV surface by predicting missing values. The dataset spans multiple strikes and timestamps, with ~20% of values missing.

Submissions are evaluated on **Mean Squared Error (MSE)** between predicted and true IV values.

---

## Dataset

| Property | Value |
|---|---|
| Timestamps | 975 rows (5-min intervals, 07-Jan-2026 to 27-Jan-2026) |
| CE strikes | 14 strikes, 25200–26500 |
| PE strikes | 14 strikes, 23800–25100 |
| Total IV columns | 28 |
| Missing values | 5,460 (~20%) |
| Spot price (approx.) | 26,112 |

Each row is one 5-minute timestamp. Each column (e.g. `NIFTY27JAN2625200CE`) holds the implied volatility for that contract at that moment.

---

## Approach

### Core Insight: The Volatility Smile is Cross-Sectional

At any single timestamp, IV is a smooth, structured function of strike price — this is the well-known **volatility smile**. For example:

```
Strike:  25200   25300   25400   25500   25600   25700
CE IV:   0.1352  0.1296  0.1253  0.1235  0.1198  0.1171
```

This means: if a strike is missing, its neighbours at the **same timestamp** predict it far better than its own past values do.

We verify this directly:

```
Cross-sectional LOO-MSE  : 0.000050   
Temporal LOO-MSE         : 0.000520   ← 10× worse
```

### Algorithm

```
For each row (timestamp):
    ┌── CE pass ──────────────────────────────────────────┐
    │  Collect observed (strike, IV) pairs for CE         │
    │  Fit linear interpolant via scipy interp1d          │
    │  Predict each missing CE strike by interpolation    │
    │  (or linear extrapolation for edge strikes)         │
    └─────────────────────────────────────────────────────┘
    ┌── PE pass ──────────────────────────────────────────┐
    │  Same procedure, independently for PE               │
    └─────────────────────────────────────────────────────┘

Fallback (< 2 observed in a row):
    pandas .interpolate(method='linear') along time axis

Final safety net:
    Column median for any remaining NaNs
```

### Design Decisions

**Why linear and not cubic/quadratic?**
Higher-order fits were tested and performed worse. With 10–12 observed points per row, cubic splines overfit to noise and extrapolate badly at the wings. Linear outperformed cubic and quadratic.

**Why separate CE and PE?**
CE strikes span 25200–26500, PE strikes span 23800–25100 — no overlap. There is a structural level shift between the two wings of the smile. Joint fitting made predictions worse .

**Why not temporal as primary?**
IV has lag-1 autocorrelation of 0.99+, which seems attractive. But the cross-sectional structure is 10× more informative for predicting a missing strike. Temporal is used only as a fallback for degenerate rows.

**No lookahead bias.**
The cross-sectional approach uses only other strikes at the **same timestamp**. No future rows are touched at any point. The problem statement rules explicitly allow same-timestamp cross-sectional features.

---

## Project Structure

```
NIFTY-IV-SURFACE/
│
├── data/
│   └── dataset.csv                    # original dataset with missing values
│
├── notebooks/
│   └── iv_surface_reconstruction.ipynb # complete pipeline
│
├── submissions/
│   └── generated submission files
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Reproducing the Submission

All steps are in `notebooks/eda.ipynb`. Run cells top to bottom:

```bash
# 1. Clone the repo
git clone <your-repo-url>
cd NIFTY-IV-SURFACE

# 2. Install dependencies
pip install -r requirements.txt

# 3. Open and run the notebook
jupyter notebook notebooks/iv_surface_reconstruction.ipynb
```

The notebook will:
1. Load data/dataset.csv
2. Perform leave-one-out cross-validation
3. Reconstruct all missing IV values
4. Generate a fully reconstructed IV surface
5. Create the final Kaggle submission file in the required format
---


## Validation

Leave-one-out cross-validation on rows with ≥ 13 observed strikes (4,911 test points):

```python
for each row with 13+ observed strikes:
    for each observed strike:
        temporarily remove it
        predict it using the remaining strikes
        record squared error

LOO_MSE = mean(all squared errors)
```

This is a conservative lower-bound estimate because it tests on interior points; the actual missing values include edge strikes where extrapolation introduces slightly higher error.


## Key Takeaway

The IV surface has strong **cross-sectional structure** at every timestamp. A missing strike is much better predicted by its neighbours in strike space than by its own history in time. Exploiting this single insight gives an improvement over the naive baseline.