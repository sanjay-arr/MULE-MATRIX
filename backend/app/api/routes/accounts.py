from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
import math
import ast
import pandas as pd

from backend.app.schemas.account_schema import AccountListResponse, AccountDetailResponse, AccountNeighborsResponse, NeighborAccount, MLPredictionResponse
from backend.app.core.data import data_store
from backend.app.core.database import neo4j_conn
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../")))
from ml.predict import predict_account

router = APIRouter()

@router.get("", response_model=AccountListResponse)
def get_accounts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    bank_id: Optional[str] = None,
    risk_level: Optional[str] = None,
    search: Optional[str] = None
):
    if data_store.detection_df is None or data_store.accounts_df is None:
        raise HTTPException(status_code=500, detail="Data not loaded")

    # Merge accounts with detection data for filtering
    df = data_store.accounts_df.merge(data_store.detection_df[['account_id', 'risk_score', 'risk_level', 'is_suspicious']], on='account_id', how='left')

    if bank_id:
        df = df[df['bank_id'] == bank_id]
    if risk_level:
        df = df[df['risk_level'] == risk_level]
    if search:
        search = search.lower()
        df = df[df['account_id'].str.lower().str.contains(search) | df['bank_id'].str.lower().str.contains(search)]

    total = len(df)
    start = (page - 1) * page_size
    end = start + page_size
    
    paginated = df.iloc[start:end]
    
    accounts = []
    for _, row in paginated.iterrows():
        accounts.append({
            "account_id": row['account_id'],
            "bank_id": row['bank_id'],
            "account_type": row.get('account_type', 'UNKNOWN'),
            "risk_level": row.get('risk_level', None),
            "is_suspicious": bool(row.get('is_suspicious', False))
        })

    return {
        "accounts": accounts,
        "total": total,
        "page": page,
        "page_size": page_size
    }

@router.get("/{account_id}", response_model=AccountDetailResponse)
def get_account(account_id: str):
    if data_store.detection_df is None or data_store.accounts_df is None:
        raise HTTPException(status_code=500, detail="Data not loaded")

    acc_df = data_store.accounts_df[data_store.accounts_df['account_id'] == account_id]
    det_df = data_store.detection_df[data_store.detection_df['account_id'] == account_id]

    if acc_df.empty:
        raise HTTPException(status_code=404, detail="Account not found")

    acc = acc_df.iloc[0]
    det = det_df.iloc[0] if not det_df.empty else None

    try:
        rules = ast.literal_eval(det.get('triggered_rules', '[]')) if det is not None else []
    except:
        rules = []

    explanation = det.get('explanation', '') if det is not None else ''
    explanations = [line.strip() for line in str(explanation).split('\n') if line.strip()] if pd.notna(explanation) else []

    return {
        "account_id": acc['account_id'],
        "bank_id": acc['bank_id'],
        "account_type": acc.get('account_type', 'UNKNOWN'),
        "risk_score": float(det['risk_score']) if det is not None else 0.0,
        "risk_level": det['risk_level'] if det is not None else "LOW",
        "is_suspicious": bool(det['is_suspicious']) if det is not None else False,
        "triggered_rules": rules,
        "explanations": explanations
    }

@router.get("/{account_id}/neighbors", response_model=AccountNeighborsResponse)
def get_account_neighbors(account_id: str):
    try:
        query = """
        MATCH (a:Account {account_id: $account_id})-[r:TRANSFER]-(neighbor:Account)
        RETURN neighbor.account_id AS neighbor_id, neighbor.bank_id AS bank_id, 
               neighbor.account_type AS account_type, r.amount AS amount, 
               r.transaction_id AS transaction_id,
               startNode(r).account_id = a.account_id AS is_outgoing
        """
        results = neo4j_conn.query(query, {"account_id": account_id})
        
        neighbors = []
        for res in results:
            neighbors.append({
                "account_id": res["neighbor_id"],
                "bank_id": res["bank_id"],
                "account_type": res["account_type"],
                "direction": "OUTGOING" if res["is_outgoing"] else "INCOMING",
                "amount": float(res["amount"]),
                "transaction_id": res["transaction_id"]
            })
            
        return {
            "account_id": account_id,
            "neighbors": neighbors
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database error: {str(e)}")

@router.get("/{account_id}/ml-prediction", response_model=MLPredictionResponse)
def get_ml_prediction(account_id: str):
    if data_store.accounts_df is None or data_store.transactions_df is None:
        raise HTTPException(status_code=500, detail="Data not loaded")

    result, success = predict_account(account_id, data_store.accounts_df, data_store.transactions_df)
    
    if not success:
        if "not found" in result.get("error", "").lower():
            raise HTTPException(status_code=404, detail=result["error"])
        elif "trained" in result.get("error", "").lower():
            raise HTTPException(status_code=503, detail=result["error"])
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Prediction failed"))
            
    return result
