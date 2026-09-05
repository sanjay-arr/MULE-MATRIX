from fastapi import APIRouter
from backend.app.core.data import data_store

router = APIRouter()

@router.get("")
def get_alerts():
    if data_store.detection_df is None:
        return {"alerts": []}
        
    # Generate alerts from the highest risk accounts
    df = data_store.detection_df
    suspicious = df[df['is_suspicious'] == True].sort_values(by='risk_score', ascending=False)
    
    alerts = []
    for idx, row in suspicious.head(20).iterrows():
        alert_type = "Mule Network Detected" if row['risk_level'] == 'CRITICAL' else \
                     "Cross-Bank Smurfing Pattern" if row['risk_level'] == 'HIGH' else \
                     "Suspicious Fund Flow"
                     
        rules = eval(row['triggered_rules']) if isinstance(row['triggered_rules'], str) else []
        network_id = row.get('network_id', None)
        # handle nan
        import math
        if isinstance(network_id, float) and math.isnan(network_id):
            network_id = None
        
        alerts.append({
            "id": f"ALT-{row['account_id']}",
            "account_id": row['account_id'],
            "network_id": network_id,
            "risk_level": row['risk_level'],
            "title": alert_type,
            "triggered_rules": rules,
            "description": f"Account {row['account_id']} triggered {len(rules)} rules.",
            "timestamp": "Recent",
            "status": "NEW"
        })
        
    return {"alerts": alerts}
