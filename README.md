# NIFTY IV Surface Reconstruction

Reconstructing missing implied volatility values across the NIFTY 50 options chain using weighted smile-aware interpolation and volatility surface smoothing.

---

## Problem Statement

Given partial implied volatility (IV) data across the NIFTY 50 options chain, reconstruct the complete IV surface by predicting missing values. The dataset spans multiple strikes and timestamps, with a significant fraction of IV observations missing across both call and put option wings.

Submissions are evaluated on **Mean Squared Error (MSE)** between predicted and true implied volatility values.

---

## Dataset

| Property | Value |
|---|---|
| Timestamps | 975 rows (5-minute intervals) |
| CE strikes | 14 strikes |
| PE strikes | 14 strikes |
| Total IV columns | 28 |
| Missing values | ~20% of observations |
| Additional feature | Underlying price |

Each row represents a single timestamp, while each option contract column contains the implied volatility corresponding to a specific strike and option type.

The objective is to reconstruct the missing entries while preserving the structure of the implied volatility surface.

---

## Approach

### Core Insight: Nearby Strikes Carry the Strongest Information

At any given timestamp, implied volatility is not random across strikes. The surface typically exhibits smoothness, skew, and smile-like curvature.

Rather than treating all observed strikes equally, the reconstruction prioritizes information from strikes closest to the missing target while still preserving the overall shape of the volatility smile.

The method combines:

- Linear interpolation as a stable baseline
- Distance-weighted local quadratic fitting for smile reconstruction
- Damped boundary extrapolation for sparse wings
- Temporal smoothing as a final safety net

---

### Algorithm

```text
For each timestamp:

    Separate CE and PE contracts

    For every missing strike:

        1. Compute a linear interpolation estimate

        2. Select the nearest observed strikes

        3. Fit a weighted local quadratic model
           using inverse-distance weighting

        4. Accept the fit only if it
           satisfies convexity validation

        5. Blend linear and quadratic
           estimates using predefined weights

    Apply damped extrapolation
    for boundary strikes

Fallback:

    Rolling historical average
    from previous timestamps

Final safety net:

    Forward-fill remaining gaps
    Fill any residual NaNs with 0.0
```

---

### Weighted Smile Reconstruction

For each missing IV value, the algorithm identifies the nearest observed strikes and fits a local quadratic model around the target strike.

Unlike an ordinary quadratic fit, nearby strikes receive higher importance through inverse-distance weighting. This allows the reconstruction to focus on the local geometry of the smile while reducing the influence of distant observations.

The quadratic estimate is then combined with a linear interpolation baseline:

- Linear interpolation provides stability
- Weighted quadratic fitting captures local curvature

The resulting prediction preserves smoothness while remaining robust in sparse regions.

---

### Damped Boundary Extrapolation

Missing values near the edges of the strike range are inherently more difficult because interpolation is no longer possible.

Instead of extending the surface using a constant slope indefinitely, the reconstruction applies exponential damping to the extrapolation distance.

This prevents unrealistic blowups on sparse option wings and produces more stable boundary behaviour.

---

## Design Decisions

### Why use weighted local quadratic fitting?

Implied volatility smiles are local structures. A strike that is 100 points away is typically more informative than one several hundred points away.

Inverse-distance weighting allows the reconstruction to emphasize the most relevant neighbouring strikes while still capturing curvature.

---

### Why retain linear interpolation?

Linear interpolation is stable and resistant to overfitting. It serves as a reliable baseline estimate that can be blended with the quadratic reconstruction.

This combination balances flexibility and robustness.

---

### Why validate convexity?

Local quadratic fits occasionally produce unrealistic shapes due to sparse observations or noise.

Only convex fits are accepted, helping maintain financially reasonable smile structures.

---

### Why use damped extrapolation?

Standard linear extrapolation can generate extreme values on the wings of the surface.

Damping reduces extrapolation sensitivity as the distance from observed strikes increases, improving stability in sparse regions.

---

### Why separate CE and PE contracts?

Call and put wings occupy different strike ranges and often exhibit different local structures.

Reconstructing them independently allows each wing to retain its own characteristics.

---

### Why use temporal information only as a fallback?

The primary signal comes from the cross-sectional shape of the volatility surface at the current timestamp.

Temporal information is used only when insufficient cross-sectional information exists, ensuring that the reconstruction remains primarily surface-driven.

---

### No look-ahead bias

The reconstruction uses only information available at the current timestamp during the primary interpolation stage.

The temporal safety net relies exclusively on historical observations through rolling averages and forward propagation.

No future timestamps are used during prediction.

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

All steps are contained inside:

```text
notebooks/iv_surface_reconstruction.ipynb
```

Run the notebook from top to bottom:

```bash
# Clone repository
git clone https://github.com/rounaktiwari27/Nifty-IV-Surface.git
cd Nifty-IV-Surface

# Install dependencies
pip install -r requirements.txt

# Launch notebook
jupyter notebook notebooks/iv_surface_reconstruction.ipynb
```

The notebook will:

1. Load `data/dataset.csv`
2. Reconstruct all missing implied volatility values
3. Generate `data/filled_dataset.csv`
4. Create `submissions/submission.csv` in the required Kaggle format

---

## Submission Generation

After reconstructing the full IV surface, the notebook automatically converts the completed dataset into the required competition submission format.

Only the originally missing entries are extracted and exported as:

```text
id,value
```

where:

```text
id = datetime || contract_name
```

This matches the format required by the competition organizers.

---

## Validation

The reconstruction methodology is built around well-known structural properties of implied volatility surfaces:

- Cross-sectional smoothness
- Volatility smile behaviour
- Local strike dependence
- Stable wing behaviour

Special care is taken to avoid look-ahead bias while preserving realistic surface geometry.

The combination of weighted smile reconstruction, damped extrapolation, and temporal safety nets provides a robust framework for filling missing implied volatility observations.

---

## Key Takeaway

Implied volatility surfaces contain strong local structure across neighbouring strikes.

By combining distance-weighted smile reconstruction, stable interpolation, and controlled boundary handling, missing implied volatility values can be recovered while preserving the overall shape and smoothness of the volatility surface.