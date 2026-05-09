from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
FIGURES_DIR = OUTPUTS_DIR / "figures"
TABLES_DIR = OUTPUTS_DIR / "tables"
MODELS_DIR = OUTPUTS_DIR / "models"
PAPER_DIR = PROJECT_ROOT / "paper"
PRESENTATION_DIR = PROJECT_ROOT / "presentation"

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

