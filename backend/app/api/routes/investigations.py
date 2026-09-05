from fastapi import APIRouter, HTTPException
import uuid

from backend.app.schemas.investigation_schema import InvestigationCreate, InvestigationResponse, InvestigationReportResponse
from backend.app.services.graph_service import GraphService
from backend.app.services.network_service import NetworkService
from backend.app.services.investigation_service import InvestigationService
from backend.app.core.data import data_store
from backend.app.api.routes.networks import _network_cache, _ensure_networks

router = APIRouter()

gs = GraphService()
ns = NetworkService(graph_service=gs, risk_results_df=data_store.detection_df)
inv_service = InvestigationService(network_service=ns)

_investigations_cache = {}

@router.post("", response_model=InvestigationResponse)
def create_investigation(payload: InvestigationCreate):
    account_id = payload.account_id
    
    if not account_id and payload.network_id:
        # Find the highest risk account for this network from the networks cache
        _ensure_networks()
        net = _network_cache.get(payload.network_id)
        if net:
            account_id = net.get("highest_risk_account")
                
    if not account_id:
        raise HTTPException(status_code=400, detail="Must provide account_id or valid network_id")
        
    # Check if account exists
    if data_store.accounts_df is None or data_store.accounts_df[data_store.accounts_df['account_id'] == account_id].empty:
        raise HTTPException(status_code=404, detail="Account not found")
        
    net = ns.reconstruct_network(account_id)
    if not net:
        raise HTTPException(status_code=500, detail="No network found or graph connection failed")
        
    _network_cache[net["network_id"]] = net
    
    threat_level = "LOW"
    if net['average_risk_score'] > 80:
        threat_level = "CRITICAL"
    elif net['average_risk_score'] > 60:
        threat_level = "HIGH"
    elif net['average_risk_score'] > 40:
        threat_level = "MEDIUM"

    report = {
        "network_id": net['network_id'],
        "threat_level": threat_level,
        "accounts_involved": net['total_accounts'],
        "banks_involved": net['number_of_banks'],
        "suspicious_amount": net['total_amount'],
        "cross_bank_transactions": net['cross_bank_transactions'],
        "max_hops": net['max_hops'],
        "highest_risk_account": net['highest_risk_account'],
        "off_ramps_found": net['off_ramp_connections'],
        "off_ramps": net['off_ramps'],
        "money_trail": []
    }
        
    # Get risk score and rules
    det_df = data_store.detection_df
    risk_score = 0
    risk_level = "LOW"
    rules_evidence = []
    if det_df is not None:
        match = det_df[det_df['account_id'] == account_id]
        if not match.empty:
            risk_score = float(match.iloc[0]['risk_score'])
            risk_level = match.iloc[0]['risk_level']
            import ast
            try:
                rules = ast.literal_eval(match.iloc[0]['triggered_rules'])
                if isinstance(rules, list):
                    rules_evidence = rules
            except:
                pass
            
    investigation_id = f"INV-{str(uuid.uuid4())[:8].upper()}"
    
    # Get off-ramp from off_ramps list
    off_ramp_account = report.get("off_ramps", [None])[0] if report.get("off_ramps") else None
    
    # Build rich evidence list using explanations
    evidence_items = []
    if det_df is not None:
        match = det_df[det_df['account_id'] == account_id]
        if not match.empty:
            explanation = match.iloc[0].get('explanation', '')
            import pandas as pd
            if pd.notna(explanation) and str(explanation).strip():
                evidence_items = [line.strip() for line in str(explanation).split('\n') if line.strip() and not line.strip().startswith('WHY')]
    if not evidence_items:
        evidence_items = [f"Rule triggered: {r}" for r in rules_evidence]
    
    response = {
        "investigation_id": investigation_id,
        "account_id": account_id,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "network_id": report.get("network_id"),
        "money_trail": report.get("money_trail", []),
        "connected_accounts": [account_id],
        "banks_involved": [str(b) for b in range(report.get("banks_involved", 1))],
        "off_ramps": report.get("off_ramps", []),
        "off_ramp_account": off_ramp_account,
        "triggered_rules": rules_evidence,
        "evidence": evidence_items
    }
    
    # Enrich connected_accounts from network
    response["connected_accounts"] = net["accounts"]
    response["banks_involved"] = net["banks"]
    
    _investigations_cache[investigation_id] = response
    return response

@router.get("/{investigation_id}", response_model=InvestigationResponse)
def get_investigation(investigation_id: str):
    inv = _investigations_cache.get(investigation_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")
    return inv

@router.get("/{investigation_id}/report", response_model=InvestigationReportResponse)
def get_investigation_report(investigation_id: str):
    inv = _investigations_cache.get(investigation_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")
        
    return {
        "investigation_id": investigation_id,
        "summary": f"Investigation into account {inv['account_id']}. Risk level is {inv['risk_level']}.",
        "risk_assessment": {
            "score": inv["risk_score"],
            "level": inv["risk_level"]
        },
        "network_analysis": {
            "network_id": inv["network_id"],
            "connected_accounts_count": len(inv["connected_accounts"]),
            "off_ramps_found": len(inv["off_ramps"])
        },
        "conclusion": "Further manual review required." if inv["risk_score"] > 50 else "No immediate action required."
    }
