import os
import json
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import sys
sys.path.append(os.path.dirname(__file__))
from features import build_account_features, get_feature_names

def train_model():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data"))
    accounts_path = os.path.join(base_dir, "processed", "accounts_processed.csv")
    transactions_path = os.path.join(base_dir, "raw", "transactions.csv")
    
    print("Loading datasets...")
    accounts_df = pd.read_csv(accounts_path)
    transactions_df = pd.read_csv(transactions_path)
    
    print("Building features...")
    features_df, labels = build_account_features(accounts_df, transactions_df)
    
    # Check for target leakage
    if 'is_mule' in features_df.columns or 'network_id' in features_df.columns:
        raise ValueError("Data Leakage Detected! Features DataFrame contains target or sensitive information.")
    
    # Ensure account_id is not used as a feature
    X = features_df.drop(columns=['account_id'])
    y = labels
    
    print(f"Accounts: {len(X)}")
    print(f"Features: {X.shape[1]}")
    
    # Train / Test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"Training samples: {len(X_train)}")
    print(f"Testing samples: {len(X_test)}")
    print("\nModel: Random Forest")
    
    # Train
    model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, class_weight='balanced')
    model.fit(X_train, y_train)
    
    # Save model
    models_dir = os.path.join(os.path.dirname(__file__), "models")
    os.makedirs(models_dir, exist_ok=True)
    model_path = os.path.join(models_dir, "random_forest.joblib")
    
    joblib.dump(model, model_path)
    
    # Save metadata
    metadata = {
        "features": get_feature_names(),
        "model": "RandomForestClassifier",
        "dataset": "Synthetic"
    }
    with open(os.path.join(models_dir, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=4)
        
    print("\nTraining complete.")
    print("Model saved successfully.")

if __name__ == "__main__":
    train_model()
