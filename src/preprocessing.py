from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.config import RANDOM_STATE, TEST_SIZE

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

