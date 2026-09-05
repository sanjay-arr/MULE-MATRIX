import argparse
import random
import uuid
import json
import os
import pandas as pd
from datetime import datetime, timedelta
from generate_scenarios import generate_fraud_scenarios, random_date, generate_account_id, generate_device_id, generate_location

def validate_data(accounts, transactions):
    print("Validating data...")
    acc_ids = set(a["account_id"] for a in accounts)
    
    errors = []
    # Verify sender and receiver exist
    for t in transactions:
        if t["sender_account"] not in acc_ids:
            errors.append(f"Transaction {t['transaction_id']} sender {t['sender_account']} missing")
        if t["receiver_account"] not in acc_ids:
            errors.append(f"Transaction {t['transaction_id']} receiver {t['receiver_account']} missing")
        if t["amount"] <= 0:
            errors.append(f"Transaction {t['transaction_id']} has non-positive amount {t['amount']}")
            
    # Verify uniqueness
    txn_ids = set([t["transaction_id"] for t in transactions])
    if len(txn_ids) != len(transactions):
        errors.append("Duplicate transaction IDs found")
        
    if not any(a["account_type"] == "OFF_RAMP" for a in accounts):
        errors.append("No OFF_RAMP accounts found")
        
    if errors:
        for e in errors[:10]:
            print(f"VALIDATION ERROR: {e}")
        if len(errors) > 10:
            print(f"...and {len(errors) - 10} more errors.")
        return False
        
    print("Validation passed.")
    return True

def generate_normal_data(banks, num_accounts, num_transactions, start_date, end_date):
    accounts = []
    transactions = []
    
    # Generate normal accounts
    for i in range(num_accounts):
        acc_type = random.choices(["CUSTOMER", "BUSINESS"], weights=[0.9, 0.1])[0]
        accounts.append({
            "account_id": generate_account_id(f"{acc_type[:3]}"),
            "bank_id": random.choice(banks),
            "account_type": acc_type,
            "account_age_days": random.randint(30, 3650),
            "created_at": (start_date - timedelta(days=random.randint(30, 3650))).isoformat(),
            "device_id": generate_device_id(),
            "location": generate_location(),
            "is_mule": False,
            "network_id": "NORMAL"
        })
        
    # Add a few baseline normal off-ramps just for structural balance, though off-ramps are heavily used in fraud
    for i in range(10):
        accounts.append({
            "account_id": generate_account_id("OFF_NORM"),
            "bank_id": random.choice(banks),
            "account_type": "OFF_RAMP",
            "account_age_days": random.randint(30, 1000),
            "created_at": (start_date - timedelta(days=random.randint(30, 1000))).isoformat(),
            "device_id": generate_device_id(),
            "location": generate_location(),
            "is_mule": False,
            "network_id": "NORMAL"
        })
        
    # Generate normal transactions
    for i in range(num_transactions):
        sender = random.choice(accounts)
        receiver = random.choice(accounts)
        while sender["account_id"] == receiver["account_id"]:
            receiver = random.choice(accounts)
            
        t_time = random_date(start_date, end_date)
        tx_type = random.choice(["TRANSFER", "UPI_SIMULATED", "BANK_TRANSFER", "WALLET_TRANSFER"])
        if receiver["account_type"] == "OFF_RAMP":
            tx_type = "OFF_RAMP"
            
        transactions.append({
            "transaction_id": f"TXN_{uuid.uuid4().hex[:10].upper()}",
            "timestamp": t_time.isoformat(),
            "sender_account": sender["account_id"],
            "receiver_account": receiver["account_id"],
            "sender_bank": sender["bank_id"],
            "receiver_bank": receiver["bank_id"],
            "amount": random.randint(100, 50000),
            "transaction_type": tx_type,
            "device_id": sender["device_id"],
            "location": sender["location"],
            "is_suspicious": False,
            "network_id": "NORMAL"
        })
        
    return accounts, transactions

def main():
    parser = argparse.ArgumentParser(description="Mule Matrix Synthetic Data Generator")
    parser.add_argument("--accounts", type=int, default=1500, help="Approximate number of accounts")
    parser.add_argument("--transactions", type=int, default=10000, help="Approximate number of normal transactions")
    parser.add_argument("--networks", type=int, default=20, help="Number of fraud networks to generate")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for deterministic generation")
    args = parser.parse_args()
    
    random.seed(args.seed)
    
    banks = ["BANK_A", "BANK_B", "BANK_C", "BANK_D", "BANK_E"]
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2025, 12, 31)
    
    print(f"Generating base normal data (Seed: {args.seed})...")
    accounts, transactions = generate_normal_data(banks, args.accounts, args.transactions, start_date, end_date)
    
    print(f"Generating {args.networks} fraud scenarios...")
    f_accs, f_txns, networks_meta = generate_fraud_scenarios(banks, args.networks, start_date, end_date)
    
    accounts.extend(f_accs)
    transactions.extend(f_txns)
    
    # Sort transactions by timestamp
    transactions.sort(key=lambda x: x["timestamp"])
    
    # Validate
    if not validate_data(accounts, transactions):
        print("Validation failed. Exiting.")
        return
        
    # Save raw data
    raw_dir = "data/raw"
    os.makedirs(raw_dir, exist_ok=True)
    
    df_acc = pd.DataFrame(accounts)
    df_acc.to_csv(os.path.join(raw_dir, "accounts.csv"), index=False)
    
    df_txn = pd.DataFrame(transactions)
    df_txn.to_csv(os.path.join(raw_dir, "transactions.csv"), index=False)
    
    # Basic processed data
    proc_dir = "data/processed"
    os.makedirs(proc_dir, exist_ok=True)
    df_acc.to_csv(os.path.join(proc_dir, "accounts_processed.csv"), index=False)
    df_txn.to_csv(os.path.join(proc_dir, "transactions_processed.csv"), index=False)
    
    # Save scenarios
    scenarios_dir = "data/scenarios"
    os.makedirs(scenarios_dir, exist_ok=True)
    for net_id, meta in networks_meta.items():
        with open(os.path.join(scenarios_dir, f"{net_id.lower()}.json"), "w") as f:
            json.dump(meta, f, indent=2)
            
    with open(os.path.join(scenarios_dir, "normal_network.json"), "w") as f:
        json.dump({"type": "NORMAL", "description": "Baseline normal transactions"}, f, indent=2)
        
    # Create the requested summary scenario files for demo purposes
    for fname in ["mule_network_1.json", "mule_network_2.json", "cross_bank_attack.json"]:
        if list(networks_meta.keys()):
            # Just copy the first few as aliases
            import shutil
            target_net = list(networks_meta.keys())[0]
            shutil.copy(os.path.join(scenarios_dir, f"{target_net.lower()}.json"), os.path.join(scenarios_dir, fname))
            
    # Print summary
    mule_accs = df_acc[df_acc['is_mule'] == True]
    normal_accs = df_acc[df_acc['is_mule'] == False]
    off_ramps = df_acc[df_acc['account_type'] == 'OFF_RAMP']
    susp_txns = df_txn[df_txn['is_suspicious'] == True]
    cross_bank_txns = df_txn[df_txn['sender_bank'] != df_txn['receiver_bank']]
    
    print("\n========================================")
    print("MULE MATRIX SYNTHETIC DATASET")
    print("========================================")
    print(f"Accounts: {len(df_acc)}")
    print(f"Transactions: {len(df_txn)}")
    print(f"Banks: {len(banks)}")
    print(f"Mule Accounts: {len(mule_accs)}")
    print(f"Normal Accounts: {len(normal_accs)}")
    print(f"Mule Networks: {args.networks}")
    print(f"Cross-Bank Transactions: {len(cross_bank_txns)}")
    print(f"Off-Ramp Accounts: {len(off_ramps)}")
    print(f"Suspicious Transactions: {len(susp_txns)}")
    
    print("\nNetwork breakdown:")
    for net_id, meta in list(networks_meta.items())[:5]:
        print(f"{net_id}: {meta['type']} ({len(meta['accounts_involved'])} accounts, {meta['transaction_count']} txns)")
    if len(networks_meta) > 5:
        print("...")
    print("========================================\n")

if __name__ == "__main__":
    main()
