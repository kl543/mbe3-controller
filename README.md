# MBE3 Heating Stage Controller (Notebook Version)

This repository contains a single, self-contained notebook **`auto_mbe3_control.ipynb`** that:
1) runs a demo control/replay workflow (real hardware configs are excluded),
2) logs results into CSV files under `data/`,
3) generates plots (Current / Voltage / Temperature vs Time) into `plots/`.

> ⚠️ Production hardware addresses, thresholds, and interlocks are **not included**. Keep real configs in a local `config.local.yaml` (git-ignored).

## Repository Layout
```text
auto_mbe3_control.ipynb   # main workflow: control + logging + plotting
data/                     # historical logs (CSV)
plots/                    # exported figures for website / reports
requirements.txt          # dependencies (numpy, pandas, matplotlib, etc.)
