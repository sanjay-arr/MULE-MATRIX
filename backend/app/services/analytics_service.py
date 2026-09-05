from backend.app.core.database import neo4j_conn
from backend.app.core.data import data_store

class AnalyticsService:
    def __init__(self):
        self.conn = neo4j_conn

    def get_overview_metrics(self):
        metrics = {
            "total_accounts": 0,
            "total_transactions": 0,
            "suspicious_accounts": 0,
            "high_risk_accounts": 0,
            "critical_accounts": 0,
            "mule_networks": 0,
            "banks_involved": 0,
            "cross_bank_transactions": 0,
            "off_ramp_accounts": 0,
            "total_transaction_value": 0.0
        }

        try:
            # 1. total_accounts
            res = self.conn.query("MATCH (a:Account) RETURN count(a) AS c")
            metrics["total_accounts"] = res[0]["c"] if res else 0

            # 2. total_transactions
            res = self.conn.query("MATCH ()-[t:TRANSFER]->() RETURN count(t) AS c")
            metrics["total_transactions"] = res[0]["c"] if res else 0

            # 7. banks_involved
            res = self.conn.query("MATCH (a:Account) RETURN count(distinct a.bank_id) AS c")
            metrics["banks_involved"] = res[0]["c"] if res else 0

            # 8. cross_bank_transactions
            res = self.conn.query("MATCH ()-[t:TRANSFER]->() WHERE t.sender_bank <> t.receiver_bank RETURN count(t) AS c")
            metrics["cross_bank_transactions"] = res[0]["c"] if res else 0

            # 9. off_ramp_accounts
            res = self.conn.query("MATCH (a:Account {account_type: 'OFF_RAMP'}) RETURN count(a) AS c")
            metrics["off_ramp_accounts"] = res[0]["c"] if res else 0

            # 10. total_transaction_value
            res = self.conn.query("MATCH ()-[t:TRANSFER]->() RETURN sum(t.amount) AS c")
            metrics["total_transaction_value"] = res[0]["c"] if res else 0.0

            # Metrics based on detection data (not stored in Neo4j schema directly)
            df = data_store.detection_df
            if df is not None and not df.empty:
                # 3. suspicious_accounts
                metrics["suspicious_accounts"] = int(df['is_suspicious'].sum())
                # 4. high_risk_accounts
                metrics["high_risk_accounts"] = int((df['risk_level'] == 'HIGH').sum())
                # 5. critical_accounts
                metrics["critical_accounts"] = int((df['risk_level'] == 'CRITICAL').sum())
                # 6. mule_networks
                metrics["mule_networks"] = len(df[df['is_suspicious'] == True]['network_id'].unique()) if 'network_id' in df.columns else 0

        except Exception as e:
            print(f"Error querying Neo4j for analytics: {e}")

        return metrics

    def get_risk_distribution(self):
        # We rely on data_store because risk_level is in detection_df
        df = data_store.detection_df
        if df is None or df.empty:
            return {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
            
        counts = df['risk_level'].value_counts()
        return {
            "LOW": int(counts.get("LOW", 0)),
            "MEDIUM": int(counts.get("MEDIUM", 0)),
            "HIGH": int(counts.get("HIGH", 0)),
            "CRITICAL": int(counts.get("CRITICAL", 0))
        }

    def get_bank_risk(self):
        # We join account and detection data
        acc_df = data_store.accounts_df
        det_df = data_store.detection_df
        
        if acc_df is None or det_df is None or acc_df.empty or det_df.empty:
            return []
            
        df = acc_df.merge(det_df[['account_id', 'risk_score', 'risk_level', 'is_suspicious']], on='account_id')
        
        results = []
        for bank_id, group in df.groupby('bank_id'):
            results.append({
                "bank_id": bank_id,
                "total_accounts": len(group),
                "suspicious_accounts": int(group['is_suspicious'].sum()),
                "average_risk": float(group['risk_score'].mean()),
                "high_risk": int((group['risk_level'] == 'HIGH').sum()),
                "critical_risk": int((group['risk_level'] == 'CRITICAL').sum())
            })
            
        return results

analytics_service = AnalyticsService()
