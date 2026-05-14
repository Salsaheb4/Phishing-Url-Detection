"""Data loading, cleaning, summary tables, feature engineering, train/test split, and sklearn pipeline builder."""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.config import RANDOM_STATE, TEST_SIZE


# ── Loading ───────────────────────────────────────────────────────────
def load_dataset(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    if df.empty:
        raise ValueError(f"Dataset at {path} is empty.")
    return df


def detect_target_column(
    df: pd.DataFrame,
    target_override: str | None = None,
    candidates: tuple[str, ...] = ("class", "label", "status", "phishing", "target"),
) -> str:
    columns_by_lower = {column.lower(): column for column in df.columns}

    if target_override:
        if target_override in df.columns:
            return target_override
        lowered = target_override.lower()
        if lowered in columns_by_lower:
            return columns_by_lower[lowered]
        available = ", ".join(df.columns)
        raise ValueError(
            f"Target column '{target_override}' was not found. Available columns: {available}"
        )

    for candidate in candidates:
        if candidate.lower() in columns_by_lower:
            return columns_by_lower[candidate.lower()]

    available = ", ".join(df.columns)
    raise ValueError(
        "Could not auto-detect the target column. "
        f"Provide --target explicitly. Available columns: {available}"
    )


def coerce_binary_target(series: pd.Series) -> pd.Series:
    unique_values = sorted(series.dropna().unique().tolist())

    if set(unique_values).issubset({0, 1}):
        return series.astype(int)

    if set(unique_values).issubset({False, True}):
        return series.astype(int)

    normalized = series.astype(str).str.strip().str.lower()
    mapping = {
        "0": 0,
        "1": 1,
        "false": 0,
        "true": 1,
        "legitimate": 0,
        "benign": 0,
        "safe": 0,
        "phishing": 1,
        "malicious": 1,
    }
    mapped = normalized.map(mapping)
    if mapped.isna().any():
        unique_display = ", ".join(map(str, unique_values))
        raise ValueError(
            "Target column could not be coerced to binary values. "
            f"Observed unique values: {unique_display}"
        )
    return mapped.astype(int)


def prepare_dataset(df: pd.DataFrame, target_col: str) -> tuple[pd.DataFrame, dict[str, Any]]:
    original_shape = df.shape
    duplicate_rows = int(df.duplicated().sum())
    cleaned_df = df.drop_duplicates().reset_index(drop=True)

    y = coerce_binary_target(cleaned_df[target_col])
    X = cleaned_df.drop(columns=[target_col]).apply(pd.to_numeric, errors="coerce")

    cleaned_df = X.copy()
    cleaned_df[target_col] = y

    metadata = {
        "original_rows": int(original_shape[0]),
        "original_columns": int(original_shape[1]),
        "cleaned_rows": int(cleaned_df.shape[0]),
        "cleaned_columns": int(cleaned_df.shape[1]),
        "duplicate_rows_removed": duplicate_rows,
        "feature_count": int(cleaned_df.shape[1] - 1),
    }
    return cleaned_df, metadata


# ── Summary tables ────────────────────────────────────────────────────
def build_dataset_summary_table(
    original_df: pd.DataFrame,
    cleaned_df: pd.DataFrame,
    target_col: str,
    metadata: dict[str, Any],
) -> pd.DataFrame:
    rows = [
        {"section": "dataset", "item": "original_rows", "value": metadata["original_rows"]},
        {"section": "dataset", "item": "original_columns", "value": metadata["original_columns"]},
        {"section": "dataset", "item": "cleaned_rows", "value": metadata["cleaned_rows"]},
        {"section": "dataset", "item": "cleaned_columns", "value": metadata["cleaned_columns"]},
        {"section": "dataset", "item": "feature_count", "value": metadata["feature_count"]},
        {"section": "dataset", "item": "target_column", "value": target_col},
    ]

    for column, dtype in original_df.dtypes.items():
        rows.append({"section": "dtype", "item": column, "value": str(dtype)})

    preview_rows = original_df.head(3).to_dict(orient="records")
    rows.append({"section": "preview", "item": "head_rows_json", "value": str(preview_rows)})
    rows.append({"section": "dataset", "item": "cleaned_shape", "value": str(cleaned_df.shape)})

    return pd.DataFrame(rows)


def build_missing_values_table(df: pd.DataFrame) -> pd.DataFrame:
    missing_counts = df.isnull().sum()
    missing_pct = (missing_counts / len(df)).mul(100).round(4)
    return pd.DataFrame(
        {
            "column": missing_counts.index,
            "missing_count": missing_counts.values,
            "missing_percent": missing_pct.values,
        }
    )


def build_duplicate_summary_table(metadata: dict[str, Any]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "original_rows": metadata["original_rows"],
                "cleaned_rows": metadata["cleaned_rows"],
                "duplicate_rows_removed": metadata["duplicate_rows_removed"],
            }
        ]
    )


def build_class_distribution_table(target: pd.Series) -> pd.DataFrame:
    counts = target.value_counts().sort_index()
    proportions = target.value_counts(normalize=True).sort_index().round(4)
    return pd.DataFrame(
        {
            "class_label": counts.index,
            "count": counts.values,
            "proportion": proportions.values,
        }
    )


# ── Feature engineering, split, pipeline ──────────────────────────────
_SPECIAL_CHAR_COLS = [
    "n_exclamation", "n_space", "n_tilde", "n_comma", "n_plus",
    "n_asterisk", "n_hastag", "n_dollar", "n_percent", "n_at",
]


def engineer_features(df: pd.DataFrame, target_col: str) -> pd.DataFrame:
    df = df.copy()
    present = [c for c in _SPECIAL_CHAR_COLS if c in df.columns]
    df["total_special_chars"] = df[present].sum(axis=1)
    df["symbol_ratio"] = df["total_special_chars"] / (df["url_length"] + 1)
    df["has_redirect"] = (df["n_redirection"] > 0).astype(int)
    df["has_at"] = (df["n_at"] > 0).astype(int)
    df["slash_dot_ratio"] = df["n_slash"] / (df["n_dots"] + 1)
    df["url_length_log"] = np.log1p(df["url_length"])
    return df


def split_dataset(df, target_col):
    X = df.drop(columns=[target_col])
    y = df[target_col]
    return train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )


def build_pipeline(model, scale_features: bool) -> Pipeline:
    steps = [("imputer", SimpleImputer(strategy="median"))]
    if scale_features:
        steps.append(("scaler", StandardScaler()))
    steps.append(("model", model))
    return Pipeline(steps=steps)
