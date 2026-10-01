"""Extract the rendered charts saved inside the modelling notebook.

The notebook already stores three PNG outputs. Keeping copies in ``assets/`` lets the
README show the exact charts from the recorded run without asking visitors to run
all models first.

Run:
    python scripts/extract_notebook_charts.py
"""
from __future__ import annotations

import base64
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "Robust_Reression_Engine.ipynb"
CHARTS = {
    60: ROOT / "assets" / "notebook_feature_importance.png",
    74: ROOT / "assets" / "notebook_ridge_lasso_coefficients.png",
    75: ROOT / "assets" / "notebook_actual_vs_predicted.png",
}


def main() -> None:
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    for cell_index, destination in CHARTS.items():
        outputs = notebook["cells"][cell_index].get("outputs", [])
        png = next(
            (output.get("data", {}).get("image/png") for output in outputs
             if output.get("data", {}).get("image/png")),
            None,
        )
        if not png:
            raise ValueError(f"Cell {cell_index} has no embedded PNG output.")
        destination.parent.mkdir(exist_ok=True)
        destination.write_bytes(base64.b64decode(png))
        print(f"Extracted {destination.relative_to(ROOT)} from notebook cell {cell_index}")


if __name__ == "__main__":
    main()
