# Presentation Outline

## Slide 1: Title

- Machine Learning-Based Detection of Phishing Web Pages Using URL Features
- Student name(s)
- Course name
- Instructor

## Slide 2: Problem Statement

- Phishing webpages attempt to steal credentials and other sensitive information.
- Manual detection and static rule lists do not scale well.
- Goal: classify URLs as phishing or legitimate using supervised machine learning.

## Slide 3: Dataset

- Kaggle Web Page Phishing Dataset
- 100,077 rows in the provided CSV, reduced to 21,891 unique rows after duplicate removal
- 19 numerical URL-based features
- Binary target column: `phishing`
- Cleaned class distribution: 6,019 legitimate and 15,872 phishing URLs

## Slide 4: Feature Examples

- URL length
- Number of dots
- Number of hyphens
- Number of slashes
- Number of question marks
- Number of redirections

## Slide 5: Methodology

- Load data and confirm the target column
- Inspect missing values, duplicates, and class balance
- Remove duplicates
- Perform a stratified 80/20 train/test split
- Scale only the models that require it
- Train, cross-validate, lightly tune, and evaluate multiple models

## Slide 6: Models Used

- Logistic Regression
- Decision Tree
- Random Forest
- Linear SVM
- K-Nearest Neighbors
- Gradient Boosting
- Extra Trees
- Optional XGBoost/LightGBM if installed

## Slide 7: Evaluation Metrics

- Accuracy
- Precision
- Recall
- F1-score
- ROC-AUC
- Confusion matrix
- Recall matters because false negatives mean phishing pages are missed

## Slide 8: Results

- Insert the model comparison table from `outputs/tables/model_results.csv`
- Insert the best-model confusion matrix from `outputs/figures/confusion_matrix_best_model.png`
- Best model: Gradient Boosting
- Accuracy: 0.8171, Precision: 0.8443, Recall: 0.9169, F1-score: 0.8791, ROC-AUC: 0.8807

## Slide 9: Comparison with Previous Work

- Include Blum et al. (2010)
- Include Sahingoz et al. (2019)
- Include Gupta et al. (2021) and Abutaha et al. (2021)
- Compare feature types, models, datasets, and reported results carefully

## Slide 10: Conclusion and Future Work

- URL features support lightweight phishing detection
- Summarize the best model after inserting actual metrics
- Discuss limitations of URL-only features
- Future work: newer datasets, richer features, and real-world validation
