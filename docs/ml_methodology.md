# Mule Matrix - Machine Learning Methodology

## Phase 7: Machine Learning Intelligence Layer

This document outlines the approach, architecture, and methodology behind the Machine Learning intelligence layer introduced in Phase 7 of the Mule Matrix system. The goal of this phase was to augment the existing rule-based and graph-based detection engines with an explainable machine learning model capable of identifying complex, non-linear behavioral patterns indicative of money mule activity.

---

## 1. Objective and Architecture

The ML model acts as an **additional intelligence signal** alongside the established detection heuristics. We opted for a **Supervised Classification** approach using a Random Forest algorithm to predict whether an account is engaged in mule activity (`is_mule = 1`) or normal activity (`is_mule = 0`).

The architecture follows a strict separation of concerns:
1. **Feature Engineering (`ml/features.py`)**: Extracts behavioral indicators from raw transaction histories without leaking target labels.
2. **Model Training (`ml/train.py`)**: Handles the data splitting, model fitting, and persistence using `scikit-learn`.
3. **Evaluation (`ml/evaluate.py`)**: Computes rigorous performance metrics on a held-out test set to quantify the model's reliability.
4. **Inference API (`ml/predict.py`)**: A lightweight wrapper integrated into the FastAPI backend that provides real-time predictions and feature importance for the React dashboard.

---

## 2. Feature Engineering

To prevent data leakage, all explicit identifiers (e.g., `account_id`, `network_id`) and truth labels (`is_suspicious`, `is_mule`) were strictly excluded from the feature space. Instead, we engineered **21 behavioral features** derived purely from the transactional edge connections of each account:

### Volume & Frequency Metrics
- `total_transaction_count`: Total number of incoming and outgoing transactions.
- `incoming_transaction_count` / `outgoing_transaction_count`: Directional transaction frequencies.
- `total_transaction_amount`, `total_incoming_amount`, `total_outgoing_amount`: Absolute monetary volumes moved through the account.
- `max_transaction_amount`, `avg_transaction_amount`: High-water marks and typical transaction sizes.

### Network & Velocity Metrics
- `unique_counterparties`: The total number of distinct accounts this account transacts with. Mule accounts typically exhibit high fan-in (many distinct senders) or fan-out (many distinct receivers).
- `unique_sending_accounts` / `unique_receiving_accounts`: Directional counterparty diversity.
- `cross_bank_transactions`: The volume of transactions where the sender's bank differs from the receiver's bank, a strong indicator of inter-institutional money laundering.

### Behavioral Ratios
- **Pass-Through Ratio**: Calculated as `min(incoming, outgoing) / max(incoming, outgoing)`. A ratio close to 1.0 indicates that money entering the account is almost entirely moved out, a classic hallmark of intermediary mule accounts.
- **Incoming-to-Outgoing Ratio**: A directional velocity indicator assessing funds accumulation vs. dispersion.

---

## 3. Model Selection: Random Forest

We selected a **Random Forest Classifier** (`RandomForestClassifier` from `scikit-learn`) for the following reasons:

1. **Explainability**: In financial crime detection, "black box" models are often unacceptable. Random Forests provide straightforward feature importance scores, allowing investigators to understand *why* the model flagged an account.
2. **Non-Linear Relationships**: Money laundering patterns are inherently non-linear (e.g., high volume *combined* with specific pass-through ratios). Tree-based models capture these interactions natively.
3. **Robustness to Outliers**: Financial transaction data is highly skewed. Random Forests handle unscaled, skewed data and outliers gracefully.
4. **Class Imbalance**: By utilizing the `class_weight='balanced'` parameter, the model dynamically penalizes misclassifications of the minority class (mule accounts), maximizing recall.

---

## 4. Training Process

1. **Dataset Generation**: We utilize the synthetic dataset `accounts_processed.csv` and `transactions.csv`.
2. **Feature Extraction**: Features are dynamically built via pandas groupings and aggregations.
3. **Data Splitting**: We employ an 80/20 train/test split. Crucially, we use **stratified sampling** (`stratify=y`) to ensure the distribution of mule accounts is identical across both the training and testing sets.
4. **Hyperparameters**: 
   - `n_estimators=100`: Sufficient ensemble size for variance reduction without excessive computational overhead.
   - `max_depth=10`: Constrains tree depth to prevent overfitting on the synthetic dataset while maintaining generalization.
   - `random_state=42`: Ensures deterministic reproducibility.
5. **Persistence**: The resulting model is serialized to `ml/models/random_forest.joblib`.

---

## 5. Evaluation Metrics

The model is evaluated on the 20% held-out test set to ensure strict generalization. The primary metrics tracked are:

- **F1 Score**: The harmonic mean of precision and recall. Given the imbalanced nature of the dataset, F1 is the most reliable single-number summary of performance.
- **Precision**: The percentage of accounts flagged as mules that were actually mules (minimizing false positives).
- **Recall**: The percentage of actual mules that were successfully flagged (minimizing false negatives).
- **ROC-AUC**: The Area Under the Receiver Operating Characteristic Curve, quantifying the model's ability to rank risk probabilities accurately across all thresholds.

### Test Set Performance
*Based on the initial run with the synthetic dataset:*
- **Precision**: ~94.1%
- **Recall**: ~94.1%
- **F1 Score**: ~94.1%
- **ROC-AUC**: ~99.9%

**Top Feature Drivers:**
1. `total_transaction_count` (15.9%)
2. `unique_counterparties` (14.8%)
3. `unique_sending_accounts` (13.6%)
4. `cross_bank_transactions` (13.3%)

---

## 6. System Integration

The model operates seamlessly within the existing FastAPI/React architecture:
- **Backend**: Exposes `/api/ml/metrics` (for dashboard visualization) and `/api/accounts/{id}/ml-prediction` (for real-time, on-demand inference).
- **Frontend - Analytics**: Displays live performance metrics and dynamic feature importance charts.
- **Frontend - Account Explorer**: Surfaces the ML probability signal alongside the existing rule-based risk score, providing investigators with a holistic, multi-layered risk assessment.
