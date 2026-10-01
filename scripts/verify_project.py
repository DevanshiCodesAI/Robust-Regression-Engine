"""Fast, dependency-free integrity checks for the repository.

This is intentionally a smoke test rather than a notebook execution: it catches a
missing/corrupt dataset, notebook, PDF or README asset in a few seconds in CI.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "Advanced_Regression_HousePrice_Dataset.csv"
NOTEBOOK = ROOT / "Robust_Reression_Engine.ipynb"
README = ROOT / "README.md"
PDF = ROOT / "Robust_Regression_Theory_Guide.pdf"
GIFS = [
    ROOT / "assets" / "robust-regression-pipeline.gif",
    ROOT / "assets" / "model-comparison.gif",
]
EXPECTED_COLUMNS = [
    "property_id",
    "sale_date",
    "area_sqft",
    "bedrooms",
    "bathrooms",
    "location_score",
    "property_age",
    "distance_city_km",
    "near_school",
    "near_metro",
    "crime_rate_index",
    "house_price_inr",
]


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)
    print(f"PASS  {message}")


def main() -> None:
    # Dataset: verify the documented schema and known number of source records.
    with DATASET.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        row_count = sum(1 for _ in reader)
    check(header == EXPECTED_COLUMNS, "CSV has the documented 12-column schema")
    check(row_count == 3800, "CSV contains 3,800 property-sale records")

    # Notebook: basic JSON validity and enough content to be a usable notebook.
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    cells = notebook.get("cells", [])
    check(notebook.get("nbformat", 0) >= 4, "Notebook is valid nbformat v4+")
    check(len(cells) >= 20, "Notebook contains its learning and modelling steps")
    source = "\n".join("".join(cell.get("source", [])) for cell in cells)
    for term in ("Ridge", "Lasso", "RandomForestRegressor", "SVR"):
        check(term in source, f"Notebook includes {term}")

    # README assets: fail early if a link in the project front door would be broken.
    readme = README.read_text(encoding="utf-8")
    for fragment in (
        "Robust Regression Engine",
        "assets/robust-regression-pipeline.gif",
        "assets/model-comparison.gif",
        "Robust_Regression_Theory_Guide.pdf",
    ):
        check(fragment in readme, f"README references {fragment}")

    check(PDF.read_bytes().startswith(b"%PDF-"), "Theory guide is a valid PDF file")
    for gif in GIFS:
        check(gif.read_bytes().startswith(b"GIF8"), f"{gif.name} is a valid GIF file")

    print("\nAll project integrity checks passed.")


if __name__ == "__main__":
    main()
