"""Regenerate figures that depend on visualize.py changes without full GridSearchCV rerun."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier

ROOT    = Path(__file__).resolve().parent
DATA    = ROOT / "data" / "web_page_phishing.csv"
FIGS    = ROOT / "outputs" / "figures"
TARGET  = "phishing"

# ── load + preprocess ──────────────────────────────────────────────────────────
from src.config import RANDOM_STATE, TEST_SIZE
from src.preprocessing import engineer_features, split_dataset, build_pipeline
from src.visualize import (
    plot_class_distribution,
    plot_top_target_correlations,
    plot_correlation_heatmap,
    plot_feature_histograms,
    plot_feature_importance,
)

print("Loading data…")
df_raw = pd.read_csv(DATA)
df = df_raw.drop_duplicates()
df = engineer_features(df, TARGET)

feature_cols = [c for c in df.columns if c != TARGET]
print(f"  {len(df):,} rows, {len(feature_cols)} features")

# ── EDA figures ────────────────────────────────────────────────────────────────
print("class_distribution…")
plot_class_distribution(df[TARGET], FIGS / "class_distribution.png")

print("top_correlations…")
plot_top_target_correlations(df, TARGET, FIGS / "top_correlations.png")

print("correlation_heatmap…")
plot_correlation_heatmap(df, FIGS / "correlation_heatmap.png", top_n=15)

print("feature_distributions…")
plot_feature_histograms(df, feature_cols, FIGS / "feature_distributions.png", top_n=8)

# ── feature importance — train GB with best-known params (no grid search) ─────
print("Training GB for feature importance…")
X_train, X_test, y_train, y_test = split_dataset(df, TARGET)

gb = GradientBoostingClassifier(
    n_estimators=200,
    learning_rate=0.1,
    max_depth=3,
    subsample=0.8,
    random_state=RANDOM_STATE,
)
pipeline = build_pipeline(gb, scale_features=False)
pipeline.fit(X_train, y_train)

print("feature_importance…")
plot_feature_importance(pipeline, feature_cols, FIGS / "feature_importance.png",
                        model_name="Gradient Boosting", top_n=10)

print("Done. All figures regenerated in outputs/figures/")
