from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import (
    GradientBoostingClassifier,
    RandomForestClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_validate
from sklearn.tree import DecisionTreeClassifier

from src.config import CV_FOLDS, RANDOM_STATE
from src.preprocessing import build_pipeline


@dataclass(frozen=True)
class ModelSpec:
    name: str
    estimator: object
    scale_features: bool
    notes: str = ""


def get_model_specs() -> list[ModelSpec]:
    return [
        ModelSpec(
            "Logistic Regression",
            LogisticRegression(max_iter=1000, random_state=RANDOM_STATE),
            True,
        ),
        ModelSpec("Decision Tree", DecisionTreeClassifier(random_state=RANDOM_STATE), False),
        ModelSpec(
            "Random Forest",
            RandomForestClassifier(
                n_estimators=200,
                random_state=RANDOM_STATE,
                n_jobs=-1,
            ),
            False,
        ),
        ModelSpec(
            "Gradient Boosting",
            GradientBoostingClassifier(random_state=RANDOM_STATE),
            False,
        ),
    ]


def get_cv() -> StratifiedKFold:
    return StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)


def get_scoring() -> dict[str, str]:
    return {
        "accuracy": "accuracy",
        "precision": "precision",
        "recall": "recall",
        "f1": "f1",
        "roc_auc": "roc_auc",
    }


def cross_validate_models(model_specs, X_train, y_train, cv) -> pd.DataFrame:
    rows = []
    for spec in model_specs:
        pipeline = build_pipeline(clone(spec.estimator), spec.scale_features)
        scores = cross_validate(
            pipeline,
            X_train,
            y_train,
            cv=cv,
            scoring=get_scoring(),
            n_jobs=1,
            error_score="raise",
        )
        rows.append(
            {
                "Model": spec.name,
                "CV Accuracy": scores["test_accuracy"].mean(),
                "CV Precision": scores["test_precision"].mean(),
                "CV Recall": scores["test_recall"].mean(),
                "CV F1-Score": scores["test_f1"].mean(),
                "CV ROC-AUC": scores["test_roc_auc"].mean(),
                "CV Fit Time": scores["fit_time"].mean(),
                "Notes": spec.notes or "Baseline cross-validation run.",
            }
        )
    return pd.DataFrame(rows).sort_values(
        by=["CV F1-Score", "CV Recall", "CV Accuracy"],
        ascending=False,
    )


def get_param_grids() -> dict[str, dict[str, list]]:
    return {
        "Logistic Regression": {
            "model__C": [0.01, 0.1, 1, 10],
            "model__solver": ["lbfgs", "liblinear"],
        },
        "Decision Tree": {
            "model__max_depth": [5, 10, 20, None],
            "model__min_samples_split": [2, 5, 10],
            "model__min_samples_leaf": [1, 2, 4],
        },
        "Random Forest": {
            "model__n_estimators": [100, 200, 300],
            "model__max_depth": [None, 15, 20],
            "model__min_samples_split": [2, 5],
            "model__min_samples_leaf": [1, 2],
        },
        "Gradient Boosting": {
            "model__n_estimators": [100, 200, 300],
            "model__learning_rate": [0.05, 0.1, 0.15],
            "model__max_depth": [2, 3, 4],
            "model__subsample": [0.8, 1.0],
        },
    }


def get_models_for_tuning(cv_results: pd.DataFrame, limit: int = 4) -> list[str]:
    tuning_grids = get_param_grids()
    candidates = []
    for model_name in cv_results["Model"].tolist():
        if model_name in tuning_grids:
            candidates.append(model_name)
        if len(candidates) == limit:
            break
    return candidates


def fit_models(model_specs, X_train, y_train, cv) -> tuple[dict[str, object], dict[str, str]]:
    fitted_models: dict[str, object] = {}
    model_notes: dict[str, str] = {}

    cv_results = cross_validate_models(model_specs, X_train, y_train, cv)
    tuning_targets = set(get_models_for_tuning(cv_results))
    tuning_grids = get_param_grids()

    for spec in model_specs:
        pipeline = build_pipeline(clone(spec.estimator), spec.scale_features)
        if spec.name in tuning_targets:
            search = GridSearchCV(
                estimator=pipeline,
                param_grid=tuning_grids[spec.name],
                scoring="f1",
                cv=cv,
                n_jobs=1,
                refit=True,
            )
            search.fit(X_train, y_train)
            fitted_models[spec.name] = search.best_estimator_
            model_notes[spec.name] = f"Tuned with GridSearchCV. Best params: {search.best_params_}"
        else:
            pipeline.fit(X_train, y_train)
            fitted_models[spec.name] = pipeline
            model_notes[spec.name] = spec.notes or "Baseline pipeline fit without hyperparameter tuning."

    return fitted_models, model_notes
