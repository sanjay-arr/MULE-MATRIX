import pandas as pd
import os

class DataStore:
    def __init__(self):
        self.accounts_df = None
        self.detection_df = None
        self.transactions_df = None

    def load_data(self):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data"))
        
        accounts_path = os.path.join(base_dir, "processed", "accounts_processed.csv")
        if os.path.exists(accounts_path):
            self.accounts_df = pd.read_csv(accounts_path)

        detection_path = os.path.join(base_dir, "processed", "detection_results.csv")
        if os.path.exists(detection_path):
            self.detection_df = pd.read_csv(detection_path)
            
        transactions_path = os.path.join(base_dir, "raw", "transactions.csv")
        if os.path.exists(transactions_path):
            self.transactions_df = pd.read_csv(transactions_path)

data_store = DataStore()
data_store.load_data()
