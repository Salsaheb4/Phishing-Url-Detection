from __future__ import annotations

import argparse
from pathlib import Path

import joblib

from src import config
from src.data_loader import (
    build_class_distribution_table,
    build_dataset_summary_table,
    build_duplicate_summary_table,
    build_missing_values_table,
    detect_target_column,
    load_dataset,
    prepare_dataset,
)
from src.evaluate_models import evaluate_models, select_best_model
from src.preprocessing import engineer_features, split_dataset
from src.train_models import cross_validate_models, fit_models, get_cv, get_model_specs
from src.utils import ensure_directories, save_dataframe, save_json, safe_metric
from src.visualize import (
    plot_class_distribution,
    plot_confusion_matrix,
    plot_correlation_heatmap,
    plot_feature_histograms,
    plot_feature_importance,
    plot_model_comparison,
    plot_roc_curves,
    plot_top_target_correlations,
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Train and evaluate phishing URL classifiers on a CSV dataset."
    )
    parser.add_argument(
        "--data",
        required=True,
        help="Path to the phishing dataset CSV file.",
    )
    parser.add_argument(
        "--target",
        default=None,
        help="Optional target column override. Auto-detected if omitted.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    project_root = Path(__file__).resolve().parent
    data_path = Path(args.data)
    if not data_path.is_absolute():
        data_path = project_root / data_path

    ensure_directories(
        [
            config.DATA_DIR,
            config.NOTEBOOKS_DIR,
            config.FIGURES_DIR,
            config.TABLES_DIR,
            config.MODELS_DIR,
            config.PAPER_DIR,
            config.PRESENTATION_DIR,
        ]
    )

    original_df = load_dataset(str(data_path))
    target_col = detect_target_column(
        original_df,
        target_override=args.target,
        candidates=config.TARGET_COLUMN_CANDIDATES,
    )
    cleaned_df, metadata = prepare_dataset(original_df, target_col)
    cleaned_df = engineer_features(cleaned_df, target_col)

    print("Dataset loaded successfully.")
    print(f"Shape: {original_df.shape}")
    print(f"Target column: {target_col}")

    missing_values_table = build_missing_values_table(cleaned_df)
    duplicate_summary_table = build_duplicate_summary_table(metadata)
    class_distribution_table = build_class_distribution_table(cleaned_df[target_col])
    dataset_summary_table = build_dataset_summary_table(
        original_df=original_df,
        cleaned_df=cleaned_df,
        target_col=target_col,
        metadata=metadata,
    )

    save_dataframe(dataset_summary_table, config.DATASET_SUMMARY_FILE)
    save_dataframe(missing_values_table, config.MISSING_VALUES_FILE)
    save_dataframe(duplicate_summary_table, config.DUPLICATE_SUMMARY_FILE)
    save_dataframe(class_distribution_table, config.CLASS_DISTRIBUTION_FILE)

    total_missing = int(missing_values_table["missing_count"].sum())
    duplicate_rows = int(metadata["duplicate_rows_removed"])
    class_distribution = {
        int(row.class_label): int(row.count)
        for row in class_distribution_table.itertuples(index=False)
    }

    print(f"Missing values: {total_missing}")
    print(f"Duplicate rows: {duplicate_rows}")
    print(f"Class distribution: {class_distribution}")

    X_train, X_test, y_train, y_test = split_dataset(cleaned_df, target_col)

    model_specs = get_model_specs()
    cv = get_cv()

    print("Training models...")
    cv_results = cross_validate_models(model_specs, X_train, y_train, cv)
    save_dataframe(cv_results, config.CROSS_VALIDATION_RESULTS_FILE)

    fitted_models, model_notes = fit_models(model_specs, X_train, y_train, cv)
    model_results, evaluations = evaluate_models(fitted_models, X_test, y_test, model_notes)
    save_dataframe(model_results, config.MODEL_RESULTS_FILE)
    print(f"Model results saved to {config.MODEL_RESULTS_FILE.relative_to(project_root)}")

    best_model_name = select_best_model(model_results)
    best_model = fitted_models[best_model_name]
    best_evaluation = evaluations[best_model_name]

    joblib.dump(best_model, config.BEST_MODEL_FILE)
    best_metrics = {
        metric: safe_metric(best_evaluation.metrics[metric])
        for metric in ("Accuracy", "Precision", "Recall", "F1-Score", "ROC-AUC")
    }
    save_json(
        {
            "best_model_name": best_model_name,
            "target_column": target_col,
            "feature_columns": cleaned_df.drop(columns=[target_col]).columns.tolist(),
            "metrics": best_metrics,
        },
        config.BEST_MODEL_METADATA_FILE,
    )

    feature_names = cleaned_df.drop(columns=[target_col]).columns.tolist()
    histogram_features = [
        feature for feature in config.SELECTED_HISTOGRAM_FEATURES if feature in feature_names
    ]

    plot_class_distribution(cleaned_df[target_col], config.CLASS_DISTRIBUTION_FIGURE)
    plot_feature_histograms(cleaned_df, histogram_features, config.FEATURE_DISTRIBUTIONS_FIGURE)
    plot_correlation_heatmap(cleaned_df, config.CORRELATION_HEATMAP_FIGURE)
    plot_top_target_correlations(cleaned_df, target_col, config.TOP_CORRELATIONS_FIGURE)
    plot_model_comparison(model_results, "Accuracy", config.MODEL_COMPARISON_ACCURACY_FIGURE)
    plot_model_comparison(model_results, "F1-Score", config.MODEL_COMPARISON_F1_FIGURE)
    plot_confusion_matrix(
        best_evaluation.confusion_matrix,
        config.CONFUSION_MATRIX_FIGURE,
        best_model_name,
    )

    roc_curve_map = {
        name: evaluation.roc_curve_data
        for name, evaluation in evaluations.items()
        if evaluation.roc_curve_data is not None
    }
    plot_roc_curves(roc_curve_map, config.ROC_CURVES_FIGURE)

    tree_models = [
        name
        for name, model in fitted_models.items()
        if hasattr(model.named_steps["model"], "feature_importances_")
    ]
    if tree_models:
        feature_importance_model_name = (
            best_model_name if best_model_name in tree_models else tree_models[0]
        )
        plot_feature_importance(
            fitted_models[feature_importance_model_name],
            feature_names,
            config.FEATURE_IMPORTANCE_FIGURE,
            feature_importance_model_name,
        )

    print(f"Best model: {best_model_name}")
    print("Best model test metrics:")
    for metric_name, value in best_metrics.items():
        print(f"{metric_name}: {value}")
    print(f"Figures saved to {config.FIGURES_DIR.relative_to(project_root)}/")
    print(f"Best model saved to {config.BEST_MODEL_FILE.relative_to(project_root)}")


if __name__ == "__main__":
    main()
