import pandas as pd
import json
import os
from .feature_engineering import generate_features
from .rule_engine import RuleEngine
from .risk_scoring import calculate_risk
from .explainability import generate_explanation

class MuleDetector:
    def __init__(self, threshold=50):
        self.rule_engine = RuleEngine()
        self.suspicious_threshold = threshold
        self.transactions_df = None
        
    def load_transactions(self, tx_path="data/raw/transactions.csv"):
        if os.path.exists(tx_path):
            self.transactions_df = pd.read_csv(tx_path)

    def detect_account(self, features_dict):
        triggered_rules = self.rule_engine.evaluate(features_dict)
        risk_score, risk_level, risk_breakdown = calculate_risk(triggered_rules)
        
        is_suspicious = risk_score >= self.suspicious_threshold
        explanation = generate_explanation(triggered_rules) if is_suspicious else ""
        
        return {
            "account_id": features_dict["account_id"],
            "bank_id": features_dict["bank_id"],
            "risk_score": risk_score,
            "risk_level": risk_level,
            "is_suspicious": is_suspicious,
            "triggered_rules": [r["rule"] for r in triggered_rules],
            "explanation": explanation
        }

    def detect_all_accounts(self, features_path="data/processed/features.csv", output_path="data/processed/detection_results.csv"):
        print(f"Running detection on features from {features_path}")
        df = pd.read_csv(features_path)
        
        results = []
        for _, row in df.iterrows():
            res = self.detect_account(row.to_dict())
            results.append(res)
            
        results_df = pd.DataFrame(results)
        
        # Merge back ground truth strictly for evaluation downstream
        eval_cols = df[['account_id', 'is_mule', 'network_id']]
        results_df = results_df.merge(eval_cols, on='account_id', how='left')
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        results_df.to_csv(output_path, index=False)
        print(f"Detection results saved to {output_path}")
        return results_df

    def get_connected_accounts(self, account_id):
        """Basic dataframe helper to find 1-hop connected accounts. Will be replaced by Neo4j."""
        if self.transactions_df is None:
            self.load_transactions()
            
        if self.transactions_df is None:
            return []
            
        incoming = self.transactions_df[self.transactions_df['receiver_account'] == account_id]['sender_account'].unique().tolist()
        outgoing = self.transactions_df[self.transactions_df['sender_account'] == account_id]['receiver_account'].unique().tolist()
        return list(set(incoming + outgoing))
