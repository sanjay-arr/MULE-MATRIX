from fastapi import APIRouter, HTTPException
from backend.app.core.data import data_store
from backend.app.core.database import neo4j_conn
import ast

router = APIRouter()

# ============================================================
# DETERMINISTIC DEMO SCENARIO
# Account CUS_7E3E2ACD — CRITICAL, BANK_A, 7 triggered rules
# Discovered via Neo4j cross-bank trail analysis
# ============================================================
DEMO_ACCOUNT_ID = "CUS_7E3E2ACD"

@router.get("/scenario")
def get_demo_scenario():
    """Returns the deterministic demo scenario for hackathon presentation."""
    
    # Fetch account details
    if data_store.accounts_df is None or data_store.detection_df is None:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    acc_df = data_store.accounts_df[data_store.accounts_df['account_id'] == DEMO_ACCOUNT_ID]
    det_df = data_store.detection_df[data_store.detection_df['account_id'] == DEMO_ACCOUNT_ID]
    
    if acc_df.empty:
        raise HTTPException(status_code=404, detail=f"Demo account {DEMO_ACCOUNT_ID} not found in dataset")
    
    acc = acc_df.iloc[0]
    det = det_df.iloc[0] if not det_df.empty else None
    
    try:
        rules = ast.literal_eval(det.get('triggered_rules', '[]')) if det is not None else []
    except:
        rules = []
    
    # Find connected off-ramp accounts via Neo4j
    off_ramp_query = """
    MATCH (a:Account {account_id: $account_id})-[:TRANSFER]->(neighbor:Account)
    WHERE neighbor.account_type = 'OFF_RAMP'
    RETURN neighbor.account_id AS off_ramp_id, neighbor.bank_id AS off_ramp_bank
    LIMIT 1
    """
    
    cross_bank_query = """
    MATCH (a:Account {account_id: $account_id})-[t:TRANSFER]->(neighbor:Account)
    WHERE a.bank_id <> neighbor.bank_id
    RETURN COUNT(t) AS cross_bank_count
    """
    
    # Count connected suspicious accounts
    connected_query = """
    MATCH (a:Account {account_id: $account_id})-[:TRANSFER]-(neighbor:Account)
    RETURN COUNT(DISTINCT neighbor) AS connected_count, 
           COLLECT(DISTINCT neighbor.bank_id)[..10] AS banks
    """
    
    off_ramp_id = None
    off_ramp_bank = None
    cross_bank_count = 0
    connected_count = 0
    banks = []
    
    try:
        off_results = neo4j_conn.query(off_ramp_query, {"account_id": DEMO_ACCOUNT_ID})
        if off_results:
            off_ramp_id = off_results[0]["off_ramp_id"]
            off_ramp_bank = off_results[0]["off_ramp_bank"]
            
        cross_results = neo4j_conn.query(cross_bank_query, {"account_id": DEMO_ACCOUNT_ID})
        if cross_results:
            cross_bank_count = cross_results[0]["cross_bank_count"]
            
        conn_results = neo4j_conn.query(connected_query, {"account_id": DEMO_ACCOUNT_ID})
        if conn_results:
            connected_count = conn_results[0]["connected_count"]
            banks = conn_results[0]["banks"]
    except Exception as e:
        pass

    return {
        "scenario": {
            "title": "Operation Cross-Bank Mule Network",
            "description": "Coordinated money mule operation detected across 5 financial institutions. Account exhibits high-velocity pass-through behavior, fan-in/fan-out patterns, and direct connection to off-ramp infrastructure.",
            "account_id": DEMO_ACCOUNT_ID,
            "bank_id": str(acc.get("bank_id", "UNKNOWN")),
            "account_type": str(acc.get("account_type", "CUSTOMER")),
            "risk_score": float(det["risk_score"]) if det is not None else 0.0,
            "risk_level": str(det["risk_level"]) if det is not None else "UNKNOWN",
            "is_suspicious": bool(det["is_suspicious"]) if det is not None else False,
            "triggered_rules": rules,
            "off_ramp_account": off_ramp_id,
            "off_ramp_bank": off_ramp_bank,
            "cross_bank_transactions": int(cross_bank_count),
            "connected_accounts": int(connected_count),
            "banks_involved": banks,
        }
    }
