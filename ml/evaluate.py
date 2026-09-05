import os
import json
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
import sys
sys.path.append(os.path.dirname(__file__))
from features import build_account_features, get_feature_names

def evaluate_model():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data"))
    accounts_path = os.path.join(base_dir, "processed", "accounts_processed.csv")
    transactions_path = os.path.join(base_dir, "raw", "transactions.csv")
    models_dir = os.path.join(os.path.dirname(__file__), "models")
    model_path = os.path.join(models_dir, "random_forest.joblib")
    
    if not os.path.exists(model_path):
        print("Model not found. Train the model first.")
        return
        
    model = joblib.load(model_path)
    
    accounts_df = pd.read_csv(accounts_path)
    transactions_df = pd.read_csv(transactions_path)
    features_df, labels = build_account_features(accounts_df, transactions_df)
    
    X = features_df.drop(columns=['account_id'])
    y = labels
    
    # We must use the exact same random state to evaluate on the exact same held-out set
    _, X_test, _, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    
    try:
        roc_auc = roc_auc_score(y_test, y_prob)
    except ValueError:
        roc_auc = "N/A (Only one class present in test set)"
        
    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel() if cm.size == 4 else ("N/A", "N/A", "N/A", "N/A")
    
    print("\nMODEL EVALUATION")
    print("----------------")
    print("Dataset: Synthetic")
    print(f"Test samples: {len(X_test)}\n")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1 Score: {f1:.4f}")
    print(f"ROC-AUC: {roc_auc if isinstance(roc_auc, str) else f'{roc_auc:.4f}'}\n")
    
    print("Confusion Matrix:")
    print(cm)
    
    # Save metrics for the API
    metrics = {
        "dataset": "Synthetic",
        "test_samples": len(X_test),
        "precision": float(precision),
        "recall": float(recall),
        "f1_score": float(f1),
        "roc_auc": float(roc_auc) if not isinstance(roc_auc, str) else None,
        "confusion_matrix": cm.tolist()
    }
    
    # Add Feature Importance
    importances = model.feature_importances_
    feature_names = get_feature_names()
    feat_importances = sorted(zip(feature_names, importances), key=lambda x: x[1], reverse=True)
    
    print("\nFeature Importance")
    print("------------------")
    importance_dict = {}
    for feat, imp in feat_importances:
        print(f"{feat:30} {imp*100:.2f}%")
        importance_dict[feat] = float(imp)
        
    metrics["feature_importance"] = importance_dict
    
    with open(os.path.join(models_dir, "metrics.json"), "w") as f:
        json.dump(metrics, f, indent=4)

if __name__ == "__main__":
    evaluate_model()
