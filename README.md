# NIFTY IV Surface Reconstruction

Reconstructing missing implied volatility values across the NIFTY 50 options chain using smile-aware cross-sectional reconstruction.

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

### Core Insight: The Volatility Smile Has Structure Beyond Linearity

At any single timestamp, implied volatility varies smoothly across strikes and typically forms a volatility smile.

Rather than assuming the smile is locally linear, the reconstruction combines:

- Linear interpolation for stability
- Local quadratic fitting for curvature awareness

The objective is to preserve the smooth shape of the smile while remaining robust in sparse or noisy regions.

### Algorithm

```text
For each timestamp:

    Separate CE and PE strikes

    For every missing strike:

        1. Compute linear interpolation estimate

        2. Select nearby observed strikes

        3. Fit a local quadratic model
           on neighbouring strikes

        4. Accept the fit only if it
           satisfies curvature validation

        5. Combine linear and quadratic
           estimates using predefined weights

    Handle edge strikes using extrapolation

Fallback:
    Forward-fill using historical observations

Final safety net:
    Row mean imputation
    Remaining NaNs filled with 0.0
```

### Smile-Aware Reconstruction

The method treats each timestamp independently and reconstructs missing values using neighbouring strikes from the same snapshot.

A local quadratic model captures the curvature of the volatility smile, while linear interpolation provides a stable baseline.

The final prediction combines both sources of information, allowing the reconstruction to adapt to different smile shapes while remaining resistant to noise and sparse observations.

---

## Design Decisions

**Why use cross-sectional information?**

At a given timestamp, neighbouring strikes contain direct information about the shape of the volatility smile. This structure is often more informative than relying primarily on temporal behaviour.

**Why combine linear and quadratic models?**

Linear interpolation is stable but ignores curvature. Quadratic fitting captures local smile geometry but can become unstable in sparse regions. Combining the two provides a balance between robustness and flexibility.

**Why separate CE and PE?**

CE strikes span 25200–26500, while PE strikes span 23800–25100. Since the two wings occupy different strike ranges and exhibit different behaviour, they are reconstructed independently.

**Why use temporal information only as a fallback?**

The primary signal comes from the cross-sectional smile at the current timestamp. Temporal information is used only when insufficient cross-sectional information is available.

**No lookahead bias.**

Cross-sectional reconstruction uses only values available at the same timestamp.

Temporal fallback operates in a forward direction and does not use future observations.

---

## Project Structure

```text
NIFTY-IV-SURFACE/
│
├── data/
│   ├── dataset.csv
│   └── filled_dataset.csv
│
├── notebooks/
│   └── iv_surface_reconstruction.ipynb
│
├── submissions/
│   ├── .gitkeep
│   └── submission.csv
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Reproducing the Submission

All steps are contained in `notebooks/iv_surface_reconstruction.ipynb`. Run the notebook cells from top to bottom:

```bash
# 1. Clone the repository
git clone https://github.com/rounaktiwari27/Nifty-IV-Surface.git
cd Nifty-IV-Surface

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch Jupyter Notebook
jupyter notebook notebooks/iv_surface_reconstruction.ipynb
```

The notebook will:

1. Load `data/dataset.csv`
2. Reconstruct all missing IV values
3. Generate `filled_dataset.csv`
4. Create the final Kaggle submission file in the required format

---

## Validation

The reconstruction approach was designed around the structural properties of implied volatility surfaces, particularly smoothness and smile behaviour across strikes.

Special care was taken to avoid look-ahead bias. Predictions are generated using information available at the current timestamp, while the temporal fallback relies only on historical observations.

---

## Key Takeaway

The implied volatility surface exhibits strong cross-sectional structure at every timestamp.

By combining stable interpolation with local smile-aware curvature modelling, missing strikes can be reconstructed while preserving the overall geometry and smoothness of the volatility surface.