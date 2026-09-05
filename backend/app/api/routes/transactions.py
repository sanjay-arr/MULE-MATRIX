from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import pandas as pd

from backend.app.schemas.transaction_schema import TransactionListResponse, TransactionDetailResponse
from backend.app.core.data import data_store

router = APIRouter()

@router.get("", response_model=TransactionListResponse)
def get_transactions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    account_id: Optional[str] = None,
    bank_id: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None
):
    if data_store.transactions_df is None:
        raise HTTPException(status_code=500, detail="Data not loaded")

    df = data_store.transactions_df

    if account_id:
        df = df[(df['sender_account'] == account_id) | (df['receiver_account'] == account_id)]
    
    if bank_id:
        df = df[(df['sender_bank'] == bank_id) | (df['receiver_bank'] == bank_id)]

    if min_amount is not None:
        df = df[df['amount'] >= min_amount]
        
    if max_amount is not None:
        df = df[df['amount'] <= max_amount]

    total = len(df)
    start = (page - 1) * page_size
    end = start + page_size
    
    paginated = df.iloc[start:end]
    
    transactions = []
    for _, row in paginated.iterrows():
        transactions.append({
            "transaction_id": row['transaction_id'],
            "sender": row['sender_account'],
            "receiver": row['receiver_account'],
            "amount": float(row['amount']),
            "timestamp": str(row['timestamp']),
            "sender_bank": row['sender_bank'],
            "receiver_bank": row['receiver_bank']
        })

    return {
        "transactions": transactions,
        "total": total,
        "page": page,
        "page_size": page_size
    }

@router.get("/{transaction_id}", response_model=TransactionDetailResponse)
def get_transaction(transaction_id: str):
    if data_store.transactions_df is None:
        raise HTTPException(status_code=500, detail="Data not loaded")

    df = data_store.transactions_df
    txn = df[df['transaction_id'] == transaction_id]

    if txn.empty:
        raise HTTPException(status_code=404, detail="Transaction not found")

    row = txn.iloc[0]
    return {
        "transaction_id": row['transaction_id'],
        "sender": row['sender_account'],
        "receiver": row['receiver_account'],
        "amount": float(row['amount']),
        "timestamp": str(row['timestamp']),
        "sender_bank": row['sender_bank'],
        "receiver_bank": row['receiver_bank']
    }
