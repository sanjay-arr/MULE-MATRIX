import pandas as pd
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.app.services.graph_service import GraphService

def main():
    print("========================================")
    print("MULE MATRIX — NEO4J LOAD")
    print("========================================\n")
    
    gs = GraphService()
    print("Connecting to Neo4j...")
    gs.connect_to_neo4j()
    
    print("Clearing database...")
    gs.clear_database()
    
    print("Creating constraints...")
    gs.create_constraints()
    
    print("Loading datasets...")
    accounts_df = pd.read_csv("data/processed/accounts_processed.csv")
    txns_df = pd.read_csv("data/processed/transactions_processed.csv")
    
    acc_count = gs.load_accounts(accounts_df)
    print(f"Accounts loaded: {acc_count}")
    
    tx_count = gs.load_transactions(txns_df)
    print(f"Transactions loaded: {tx_count}")
    
    print("\nVerifying database state...")
    stats = gs.get_network_statistics()
    
    print(f"Banks represented: {stats.get('banks', 0)}")
    print(f"Cross-bank transactions: {stats.get('cross_bank_transactions', 0)}")
    print(f"Off-ramp accounts: {stats.get('off_ramp_accounts', 0)}")
    
    print("\nDatabase verification:")
    print(f"Accounts in Neo4j: {stats.get('accounts', 0)} (PASS if matches {acc_count})")
    print(f"Transfers in Neo4j: {stats.get('transactions', 0)} (PASS if matches {tx_count})")
    
    print("\n========================================")
    print("LOAD COMPLETE")
    print("========================================")

if __name__ == "__main__":
    main()
