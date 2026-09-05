import os
import joblib
import pandas as pd
from typing import Dict, Any, Tuple
import sys
sys.path.append(os.path.dirname(__file__))
from features import build_account_features, get_feature_names

_model = None

def get_model():
    global _model
    if _model is None:
        model_path = os.path.join(os.path.dirname(__file__), "models", "random_forest.joblib")
        if os.path.exists(model_path):
            _model = joblib.load(model_path)
    return _model

def predict_account(account_id: str, accounts_df: pd.DataFrame, transactions_df: pd.DataFrame) -> Tuple[Dict[str, Any], bool]:
    """
    Predicts if a single account is a mule.
    Returns:
        dict: The prediction results
        bool: True if prediction was successful, False otherwise
    """
    model = get_model()
    if model is None:
        return {"error": "ML model not trained or loaded."}, False
        
    # Filter for just this account to build features
    acc_df = accounts_df[accounts_df['account_id'] == account_id]
    if acc_df.empty:
        return {"error": "Account not found."}, False
        
    # We only need transactions involving this account to build its features
    txn_mask = (transactions_df['sender_account'] == account_id) | (transactions_df['receiver_account'] == account_id)
    acc_txns = transactions_df[txn_mask]
    
    # Build features just for this subset
    features_df, _ = build_account_features(acc_df, acc_txns)
    
    if features_df.empty:
        return {"error": "Could not generate features for account."}, False
        
    X = features_df.drop(columns=['account_id'], errors='ignore')
    
    # Predict
    prob = model.predict_proba(X)[0, 1]
    pred_class = int(model.predict(X)[0])
    
    # Get top contributing features (approximate local explanation using global importance)
    importances = model.feature_importances_
    feat_names = get_feature_names()
    
    # Map feature values to their importance to provide some explainability
    account_features = X.iloc[0].to_dict()
    
    result = {
        "account_id": account_id,
        "ml_prediction": "MULE" if pred_class == 1 else "NORMAL",
        "mule_probability": float(prob),
        "model": "RandomForestClassifier",
        "features": account_features
    }
    
    return result, True
