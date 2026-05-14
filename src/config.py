"""Project paths, constants, and small IO helpers."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

# ── Paths ─────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
FIGURES_DIR = OUTPUTS_DIR / "figures"
TABLES_DIR = OUTPUTS_DIR / "tables"
MODELS_DIR = OUTPUTS_DIR / "models"
PAPER_DIR = PROJECT_ROOT / "paper"
PRESENTATION_DIR = PROJECT_ROOT / "presentation"

# ── Hyperparameters / experiment settings ─────────────────────────────
RANDOM_STATE = 42
TEST_SIZE = 0.20
CV_FOLDS = 5

TARGET_COLUMN_CANDIDATES = ("class", "label", "status", "phishing", "target")

SELECTED_HISTOGRAM_FEATURES = (
    "url_length",
    "n_dots",
    "n_hypens",
    "n_slash",
    "n_questionmark",
    "n_redirection",
    "symbol_ratio",
    "slash_dot_ratio",
)

# ── Output file paths ─────────────────────────────────────────────────
DATASET_SUMMARY_FILE = TABLES_DIR / "dataset_summary.csv"
MISSING_VALUES_FILE = TABLES_DIR / "missing_values.csv"
DUPLICATE_SUMMARY_FILE = TABLES_DIR / "duplicate_summary.csv"
CLASS_DISTRIBUTION_FILE = TABLES_DIR / "class_distribution.csv"
CROSS_VALIDATION_RESULTS_FILE = TABLES_DIR / "cross_validation_results.csv"
MODEL_RESULTS_FILE = TABLES_DIR / "model_results.csv"
LITERATURE_COMPARISON_FILE = TABLES_DIR / "literature_comparison.csv"

CLASS_DISTRIBUTION_FIGURE = FIGURES_DIR / "class_distribution.png"
FEATURE_DISTRIBUTIONS_FIGURE = FIGURES_DIR / "feature_distributions.png"
CORRELATION_HEATMAP_FIGURE = FIGURES_DIR / "correlation_heatmap.png"
TOP_CORRELATIONS_FIGURE = FIGURES_DIR / "top_correlations.png"
MODEL_COMPARISON_ACCURACY_FIGURE = FIGURES_DIR / "model_comparison_accuracy.png"
MODEL_COMPARISON_F1_FIGURE = FIGURES_DIR / "model_comparison_f1.png"
CONFUSION_MATRIX_FIGURE = FIGURES_DIR / "confusion_matrix_best_model.png"
ROC_CURVES_FIGURE = FIGURES_DIR / "roc_curves.png"
FEATURE_IMPORTANCE_FIGURE = FIGURES_DIR / "feature_importance.png"

BEST_MODEL_FILE = MODELS_DIR / "best_model.pkl"
BEST_MODEL_METADATA_FILE = MODELS_DIR / "best_model_metadata.json"


# ── IO helpers ────────────────────────────────────────────────────────
def ensure_directories(paths: Iterable[Path]) -> None:
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def save_dataframe(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def save_json(data: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file_obj:
        json.dump(data, file_obj, indent=2)


def safe_metric(value: float | None) -> float | None:
    if value is None or pd.isna(value):
        return None
    return round(float(value), 4)
