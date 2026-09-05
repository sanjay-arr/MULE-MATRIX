import pytest
import os
import pandas as pd

def test_data_generation_validation():
    # If the user ran the script, the raw files should exist
    assert os.path.exists("data/raw/accounts.csv"), "Accounts file missing. Did you run generate_data.py?"
    assert os.path.exists("data/raw/transactions.csv"), "Transactions file missing. Did you run generate_data.py?"
    
    df_acc = pd.read_csv("data/raw/accounts.csv")
    df_txn = pd.read_csv("data/raw/transactions.csv")
    
    assert len(df_acc) > 0
    assert len(df_txn) > 0
    
    # Validate referential integrity
    acc_ids = set(df_acc['account_id'])
    assert df_txn['sender_account'].isin(acc_ids).all(), "Found sender not in accounts"
    assert df_txn['receiver_account'].isin(acc_ids).all(), "Found receiver not in accounts"
    
    # Validate amounts
    assert (df_txn['amount'] > 0).all(), "Found non-positive transaction amounts"
    
    # Validate uniqueness
    assert df_txn['transaction_id'].is_unique, "Duplicate transaction IDs found"
    
    # Validate off-ramps exist
    assert 'OFF_RAMP' in df_acc['account_type'].values, "No OFF_RAMP accounts generated"
    
    # Validate suspicious flags match network logic
    suspicious = df_txn[df_txn['is_suspicious'] == True]
    assert (suspicious['network_id'] != 'NORMAL').all(), "Suspicious transactions must have a network_id"
