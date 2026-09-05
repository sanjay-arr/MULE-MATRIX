import pandas as pd
import os
import sys

class DataStore:
    def __init__(self):
        self.accounts_df = None
        self.detection_df = None
        self.transactions_df = None
        self.pipeline_initialized = False

    def _initialize_data_pipeline(self, base_dir):
        print("Initializing Mule Matrix Data Pipeline for Production...")
        root_dir = os.path.abspath(os.path.join(base_dir, "../../.."))
        old_cwd = os.getcwd()
        old_argv = sys.argv
        
        try:
            os.chdir(root_dir)
            if root_dir not in sys.path:
                sys.path.append(root_dir)
            
            # 1. Generate Data
            print("Generating synthetic data...")
            import scripts.generate_data as generate_data
            sys.argv = ["generate_data.py", "--accounts", "1500", "--transactions", "10000", "--networks", "10"]
            generate_data.main()
            
            # 2. Extract Features
            print("Extracting features...")
            from backend.app.detection.feature_engineering import generate_features
            generate_features()
            
            # 3. Detect Accounts
            print("Running mule detector...")
            from backend.app.detection.mule_detector import MuleDetector
            detector = MuleDetector()
            detector.detect_all_accounts()
            
            # 4. Train Model
            print("Training ML model...")
            from ml.train import train_model
            train_model()
            
        except Exception as e:
            import traceback
            print(f"Error initializing data pipeline: {e}")
            print("--- DATA PIPELINE TRACEBACK ---")
            traceback.print_exc()
            print("-------------------------------")
        finally:
            os.chdir(old_cwd)
            sys.argv = old_argv
            print("Data Pipeline Initialization Complete!")

    def load_data(self):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data"))
        
        accounts_path = os.path.join(base_dir, "processed", "accounts_processed.csv")
        detection_path = os.path.join(base_dir, "processed", "detection_results.csv")
        transactions_path = os.path.join(base_dir, "raw", "transactions.csv")

        if not (os.path.exists(accounts_path) and os.path.exists(detection_path) and os.path.exists(transactions_path)):
            if not self.pipeline_initialized:
                self._initialize_data_pipeline(os.path.dirname(__file__))
                self.pipeline_initialized = True
        
        if os.path.exists(accounts_path):
            self.accounts_df = pd.read_csv(accounts_path)

        if os.path.exists(detection_path):
            self.detection_df = pd.read_csv(detection_path)
            
        transactions_path = os.path.join(base_dir, "raw", "transactions.csv")
        if os.path.exists(transactions_path):
            self.transactions_df = pd.read_csv(transactions_path)

data_store = DataStore()
data_store.load_data()
