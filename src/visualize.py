from __future__ import annotations

import math

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

try:
    import seaborn as sns
    sns.set_theme(style="whitegrid", palette="muted", font_scale=1.3)
except ImportError:
    sns = None

_PALETTE = {
    "blue":       "#1d3557",
    "teal":       "#2a9d8f",
    "orange":     "#e76f51",
    "dark":       "#264653",
    "yellow":     "#e9c46a",
    "lightblue":  "#457b9d",
    "green":      "#52b788",
    "purple":     "#7b2d8b",
}

_MODEL_COLORS = [
    "#1d3557", "#2a9d8f", "#e76f51", "#e9c46a",
    "#457b9d", "#264653", "#52b788", "#7b2d8b",
]


def _save_figure(output_path):
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def _annotate_bars(ax, fmt="{:.3f}", fontsize=9, offset_frac=0.005):
    ylim = ax.get_ylim()
    span = ylim[1] - ylim[0]
    for patch in ax.patches:
        h = patch.get_height()
        if h == 0:
            continue
        ax.text(
            patch.get_x() + patch.get_width() / 2.0,
            h + span * offset_frac,
            fmt.format(h),
            ha="center",
            va="bottom",
            fontsize=fontsize,
            fontweight="bold",
        )


def plot_class_distribution(target: pd.Series, output_path) -> None:
    counts = target.value_counts().sort_index()
    labels = ["Legitimate (0)", "Phishing (1)"]
    colors = [_PALETTE["teal"], _PALETTE["orange"]]
    total = counts.sum()

    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(
        labels[: len(counts)],
        counts.values,
        color=colors[: len(counts)],
        edgecolor="white",
        linewidth=0.8,
        zorder=3,
    )
    ax.set_title("Class Distribution", fontsize=13, fontweight="bold", pad=10)
    ax.set_ylabel("Count", fontsize=11)
    ax.set_xlabel("Class", fontsize=11)
    ax.yaxis.grid(True, linestyle="--", alpha=0.7, zorder=0)
    ax.set_axisbelow(True)

    for bar, count in zip(bars, counts.values):
        pct = 100 * count / total
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + total * 0.01,
            f"{count:,}\n({pct:.1f}%)",
            ha="center", va="bottom", fontsize=10, fontweight="bold",
        )

    _save_figure(output_path)


def plot_feature_histograms(df: pd.DataFrame, feature_names, output_path, top_n: int = 8) -> None:
    if not feature_names:
        return
    # Select top_n features by absolute correlation with target, else by variance
    names = list(feature_names)
    if "phishing" in df.columns:
        corrs = df[names].corrwith(df["phishing"]).abs().sort_values(ascending=False)
        names = corrs.index[:top_n].tolist()
    else:
        variances = df[names].var().sort_values(ascending=False)
        names = variances.index[:top_n].tolist()

    rows = math.ceil(len(names) / 2)
    fig, axes = plt.subplots(rows, 2, figsize=(10, 3.5 * rows), squeeze=False)
    axes = axes.flatten()
    for ax, feature in zip(axes, names):
        data = df[feature].dropna()
        p01 = data.quantile(0.01)
        p99 = data.quantile(0.99)
        plot_data = data.clip(lower=p01, upper=p99) if p99 > p01 else data
        ax.hist(plot_data, bins=35, color=_PALETTE["lightblue"], edgecolor="white", alpha=0.9, zorder=3)
        ax.set_title(feature, fontsize=12, fontweight="bold")
        ax.set_xlabel(feature, fontsize=10)
        ax.set_ylabel("Frequency", fontsize=10)
        ax.yaxis.grid(True, linestyle="--", alpha=0.6, zorder=0)
        ax.set_axisbelow(True)
        ax.tick_params(axis="both", labelsize=9)
    for ax in axes[len(names):]:
        ax.axis("off")
    fig.suptitle("Top Feature Distributions (clipped to 1st–99th percentile)", fontsize=13, fontweight="bold", y=1.01)
    _save_figure(output_path)


def plot_correlation_heatmap(df: pd.DataFrame, output_path, top_n: int = 15) -> None:
    # Keep top_n features most correlated with target (+ target col itself)
    num_df = df.select_dtypes(include="number")
    if "phishing" in num_df.columns:
        corrs = num_df.drop(columns=["phishing"]).corrwith(num_df["phishing"]).abs()
        top_cols = corrs.sort_values(ascending=False).index[:top_n].tolist() + ["phishing"]
        num_df = num_df[top_cols]
    correlation = num_df.corr()
    n = len(correlation)
    size = max(9, n * 0.65)
    fig, ax = plt.subplots(figsize=(size, size * 0.85))
    if sns is not None:
        sns.heatmap(
            correlation,
            cmap="coolwarm",
            center=0,
            square=True,
            linewidths=0.5,
            annot=False,
            ax=ax,
        )
        ax.tick_params(axis="both", labelsize=11)
    else:
        im = ax.imshow(correlation, cmap="coolwarm", aspect="auto")
        plt.colorbar(im, ax=ax)
        ax.set_xticks(range(n))
        ax.set_xticklabels(correlation.columns, rotation=45, ha="right", fontsize=10)
        ax.set_yticks(range(n))
        ax.set_yticklabels(correlation.index, fontsize=10)
    ax.set_title(f"Feature Correlation Heatmap (top {top_n} by target correlation)",
                 fontsize=13, fontweight="bold", pad=12)
    _save_figure(output_path)


def plot_top_target_correlations(df: pd.DataFrame, target_col: str, output_path) -> None:
    correlations = (
        df.corr(numeric_only=True)[target_col]
        .drop(target_col)
        .abs()
        .sort_values(ascending=False)
    )
    colors = [_PALETTE["blue"] if v >= 0.1 else _PALETTE["lightblue"] for v in correlations.values]

    fig, ax = plt.subplots(figsize=(11, 5))
    bars = ax.bar(correlations.index, correlations.values, color=colors, edgecolor="white", zorder=3)
    ax.set_title("Absolute Correlation with Target (Phishing Label)", fontsize=13, fontweight="bold", pad=10)
    ax.set_ylabel("Absolute Pearson Correlation", fontsize=11)
    ax.set_xlabel("Feature", fontsize=11)
    ax.set_ylim(0, correlations.max() * 1.18)
    ax.yaxis.grid(True, linestyle="--", alpha=0.7, zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(axis="x", rotation=45, labelsize=10)
    ax.tick_params(axis="y", labelsize=10)
    for lbl in ax.get_xticklabels():
        lbl.set_ha("right")
        lbl.set_rotation_mode("anchor")
    _annotate_bars(ax, fmt="{:.3f}", fontsize=9)
    _save_figure(output_path)



def plot_model_comparison(results_df: pd.DataFrame, metric_name: str, output_path) -> None:
    ordered = results_df.sort_values(by=metric_name, ascending=False).reset_index(drop=True)
    colors = [_MODEL_COLORS[i % len(_MODEL_COLORS)] for i in range(len(ordered))]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(
        ordered["Model"],
        ordered[metric_name],
        color=colors,
        edgecolor="white",
        linewidth=0.8,
        zorder=3,
    )
    ax.set_title(f"Model Comparison — {metric_name}", fontsize=13, fontweight="bold", pad=10)
    ax.set_ylabel(metric_name, fontsize=11)
    ax.set_ylim(0, 1.12)
    ax.yaxis.grid(True, linestyle="--", alpha=0.7, zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(axis="x", rotation=25)
    _annotate_bars(ax, fmt="{:.4f}", fontsize=9)
    _save_figure(output_path)


def plot_confusion_matrix(matrix, output_path, model_name: str) -> None:
    fig, ax = plt.subplots(figsize=(6, 5))
    labels = ["Legitimate", "Phishing"]
    total = matrix.sum()
    annot = np.array([
        [f"{v}\n({100*v/total:.1f}%)" for v in row]
        for row in matrix
    ])

    if sns is not None:
        sns.heatmap(
            matrix,
            annot=annot,
            fmt="",
            cmap="Blues",
            xticklabels=labels,
            yticklabels=labels,
            linewidths=0.5,
            linecolor="white",
            ax=ax,
            cbar_kws={"shrink": 0.8},
        )
    else:
        im = ax.imshow(matrix, cmap="Blues")
        plt.colorbar(im, ax=ax, shrink=0.8)
        for (r, c), val in np.ndenumerate(matrix):
            ax.text(c, r, annot[r][c], ha="center", va="center", fontsize=10)
        ax.set_xticks([0, 1])
        ax.set_xticklabels(labels)
        ax.set_yticks([0, 1])
        ax.set_yticklabels(labels)

    ax.set_title(f"Confusion Matrix — {model_name}", fontsize=13, fontweight="bold", pad=10)
    ax.set_xlabel("Predicted Label", fontsize=11)
    ax.set_ylabel("Actual Label", fontsize=11)
    _save_figure(output_path)


def plot_roc_curves(roc_curve_map, output_path) -> bool:
    if not roc_curve_map:
        return False

    from sklearn.metrics import auc as sk_auc

    line_styles = ["-", "--", "-.", ":"]
    fig, ax = plt.subplots(figsize=(7, 6))

    for i, (model_name, (fpr, tpr)) in enumerate(roc_curve_map.items()):
        roc_auc = sk_auc(fpr, tpr)
        color = _MODEL_COLORS[i % len(_MODEL_COLORS)]
        ls = line_styles[i % len(line_styles)]
        ax.plot(fpr, tpr, linewidth=2, color=color, linestyle=ls,
                label=f"{model_name} (AUC = {roc_auc:.4f})")

    ax.plot([0, 1], [0, 1], linestyle="--", color="gray", linewidth=1, label="Random Classifier")
    ax.fill_between([0, 1], [0, 1], alpha=0.05, color="gray")

    ax.set_title("ROC Curves — All Models", fontsize=13, fontweight="bold", pad=10)
    ax.set_xlabel("False Positive Rate", fontsize=11)
    ax.set_ylabel("True Positive Rate", fontsize=11)
    ax.legend(fontsize=9, loc="lower right", framealpha=0.9)
    ax.xaxis.grid(True, linestyle="--", alpha=0.6)
    ax.yaxis.grid(True, linestyle="--", alpha=0.6)
    ax.set_xlim([-0.01, 1.01])
    ax.set_ylim([-0.01, 1.05])
    _save_figure(output_path)
    return True


def plot_feature_importance(model, feature_names, output_path, model_name: str, top_n: int = 10) -> bool:
    final_estimator = model.named_steps["model"]
    if not hasattr(final_estimator, "feature_importances_"):
        return False

    importances = (
        pd.Series(final_estimator.feature_importances_, index=feature_names)
        .sort_values(ascending=False)
        .head(top_n)
    )
    colors = [_PALETTE["yellow"] if imp >= importances.mean() else _PALETTE["lightblue"]
              for imp in importances.values]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(importances.index, importances.values, color=colors, edgecolor="white", zorder=3)
    ax.set_title(f"Top {top_n} Feature Importances — {model_name}", fontsize=14, fontweight="bold", pad=12)
    ax.set_ylabel("Importance Score", fontsize=12)
    ax.set_xlabel("Feature", fontsize=12)
    ax.set_ylim(0, importances.max() * 1.20)
    ax.yaxis.grid(True, linestyle="--", alpha=0.7, zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(axis="x", rotation=40, labelsize=11)
    ax.tick_params(axis="y", labelsize=10)
    for lbl in ax.get_xticklabels():
        lbl.set_ha("right")
        lbl.set_rotation_mode("anchor")
    _annotate_bars(ax, fmt="{:.4f}", fontsize=9)
    _save_figure(output_path)
    return True
