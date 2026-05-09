from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)


@dataclass
class ModelEvaluation:
    metrics: dict[str, object]
    confusion_matrix: np.ndarray
    roc_curve_data: tuple[np.ndarray, np.ndarray] | None


def _get_score_values(model, X):
    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(X)
        return probabilities[:, 1]
    if hasattr(model, "decision_function"):
        decision_scores = model.decision_function(X)
        if hasattr(decision_scores, "ndim") and decision_scores.ndim > 1:
            return decision_scores[:, 1]
        return decision_scores
    return None


def evaluate_model(name, model, X_test, y_test, note) -> ModelEvaluation:
    predictions = model.predict(X_test)
    score_values = _get_score_values(model, X_test)

    roc_auc = np.nan
    roc_curve_data = None
    if score_values is not None:
        roc_auc = roc_auc_score(y_test, score_values)
        fpr, tpr, _ = roc_curve(y_test, score_values)
        roc_curve_data = (fpr, tpr)

    metrics = {
        "Model": name,
        "Accuracy": accuracy_score(y_test, predictions),
        "Precision": precision_score(y_test, predictions, zero_division=0),
        "Recall": recall_score(y_test, predictions, zero_division=0),
        "F1-Score": f1_score(y_test, predictions, zero_division=0),
        "ROC-AUC": roc_auc,
        "Notes": note,
    }
    matrix = confusion_matrix(y_test, predictions)
    return ModelEvaluation(metrics=metrics, confusion_matrix=matrix, roc_curve_data=roc_curve_data)


def evaluate_models(fitted_models, X_test, y_test, model_notes):
    results = []
    evaluations = {}
    for name, model in fitted_models.items():
        evaluation = evaluate_model(name, model, X_test, y_test, model_notes.get(name, ""))
        results.append(evaluation.metrics)
        evaluations[name] = evaluation

    results_df = pd.DataFrame(results).sort_values(
        by=["F1-Score", "Recall", "Accuracy", "ROC-AUC"],
        ascending=False,
    )
    return results_df, evaluations


def select_best_model(results_df: pd.DataFrame) -> str:
    sortable = results_df.copy()
    sortable["ROC-AUC"] = sortable["ROC-AUC"].fillna(-1.0)
    sortable = sortable.sort_values(
        by=["F1-Score", "Recall", "Accuracy", "ROC-AUC"],
        ascending=False,
    )
    return str(sortable.iloc[0]["Model"])

