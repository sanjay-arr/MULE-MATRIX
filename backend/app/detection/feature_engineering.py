import pandas as pd
import numpy as np
import os

def generate_features(accounts_path="data/raw/accounts.csv", 
                      transactions_path="data/raw/transactions.csv", 
                      output_path="data/processed/features.csv"):
    print("Generating behavioural features...")
    
    accounts_df = pd.read_csv(accounts_path)
    transactions_df = pd.read_csv(transactions_path)
    
    # Ensure timestamps are parsed
    transactions_df['timestamp'] = pd.to_datetime(transactions_df['timestamp'])
    accounts_df['created_at'] = pd.to_datetime(accounts_df['created_at'])
    
    features = []
    
    # Pre-calculate off-ramps to optimize off-ramp connection lookup
    off_ramp_accounts = set(accounts_df[accounts_df['account_type'] == 'OFF_RAMP']['account_id'])
    
    # Sort transactions once for temporal features
    transactions_df = transactions_df.sort_values(by=['timestamp'])
    
    for _, account in accounts_df.iterrows():
        acc_id = account['account_id']
        is_mule = account['is_mule']
        network_id = account['network_id']
        bank_id = account['bank_id']
        age_days = account['account_age_days']
        
        # Get transactions for this account
        incoming = transactions_df[transactions_df['receiver_account'] == acc_id].copy()
        outgoing = transactions_df[transactions_df['sender_account'] == acc_id].copy()
        all_txns = pd.concat([incoming, outgoing]).drop_duplicates('transaction_id').sort_values('timestamp')
        
        # 1. BASIC
        in_count = len(incoming)
        out_count = len(outgoing)
        total_txns = in_count + out_count
        
        total_received = incoming['amount'].sum() if in_count > 0 else 0.0
        total_sent = outgoing['amount'].sum() if out_count > 0 else 0.0
        
        amounts = all_txns['amount'] if total_txns > 0 else pd.Series([], dtype=float)
        avg_amt = amounts.mean() if total_txns > 0 else 0.0
        med_amt = amounts.median() if total_txns > 0 else 0.0
        std_amt = amounts.std() if total_txns > 1 else 0.0
        if pd.isna(std_amt): std_amt = 0.0
        
        # 2. COUNTERPARTY
        unique_senders = incoming['sender_account'].nunique()
        unique_receivers = outgoing['receiver_account'].nunique()
        unique_counterparties = len(set(incoming['sender_account']).union(set(outgoing['receiver_account'])))
        
        # 3. VELOCITY & PASS-THROUGH
        rapid_transfers = 0
        min_delay = -1.0
        delays = []
        
        if in_count > 0 and out_count > 0:
            for _, out_tx in outgoing.iterrows():
                # Find most recent incoming transaction before this outgoing transaction
                prior_in = incoming[incoming['timestamp'] <= out_tx['timestamp']]
                if not prior_in.empty:
                    delay = (out_tx['timestamp'] - prior_in.iloc[-1]['timestamp']).total_seconds()
                    delays.append(delay)
                    if min_delay == -1 or delay < min_delay:
                        min_delay = delay
                    if delay < 3600: # Less than 1 hour is rapid
                        rapid_transfers += 1
                        
        avg_delay = np.mean(delays) if delays else -1.0
        rapid_ratio = rapid_transfers / out_count if out_count > 0 else 0.0
        
        pass_through_ratio = total_sent / total_received if total_received > 0 else (1.0 if total_sent > 0 else 0.0)
        retained = total_received - total_sent
        retained_ratio = retained / total_received if total_received > 0 else 0.0
        
        # 4. CROSS-BANK
        banks_involved = set()
        banks_involved.add(bank_id)
        banks_involved.update(incoming['sender_bank'])
        banks_involved.update(outgoing['receiver_bank'])
        unique_banks = len(banks_involved)
        
        cross_bank_txns = len(incoming[incoming['sender_bank'] != bank_id]) + len(outgoing[outgoing['receiver_bank'] != bank_id])
        cross_bank_ratio = cross_bank_txns / total_txns if total_txns > 0 else 0.0
        
        # 5. FLOW PATTERNS
        fan_in_ratio = unique_senders / in_count if in_count > 0 else 0.0
        fan_out_ratio = unique_receivers / out_count if out_count > 0 else 0.0
        
        # 6. OFF-RAMP
        off_ramp_conn = len(outgoing[outgoing['receiver_account'].isin(off_ramp_accounts)])
        off_ramp_ratio = off_ramp_conn / out_count if out_count > 0 else 0.0
        
        # 7. TEMPORAL
        active_days = (all_txns['timestamp'].max() - all_txns['timestamp'].min()).days if total_txns > 1 else 1
        active_days = max(1, active_days)
        active_hours = active_days * 24
        
        txns_per_day = total_txns / active_days
        txns_per_hour = total_txns / active_hours
        
        burst_count = 0
        if total_txns > 3:
            # Simple burst calculation: 3+ txns in same hour
            grouped_hours = all_txns.groupby(all_txns['timestamp'].dt.floor('h')).size()
            burst_count = len(grouped_hours[grouped_hours >= 3])

        feat_dict = {
            "account_id": acc_id,
            "bank_id": bank_id,
            
            # Basic
            "transaction_count": total_txns,
            "incoming_transaction_count": in_count,
            "outgoing_transaction_count": out_count,
            "total_received": total_received,
            "total_sent": total_sent,
            "average_transaction_amount": avg_amt,
            "median_transaction_amount": med_amt,
            "amount_std": std_amt,
            "account_age_days": age_days,
            
            # Counterparty
            "unique_senders": unique_senders,
            "unique_receivers": unique_receivers,
            "unique_counterparties": unique_counterparties,
            
            # Velocity
            "average_transfer_delay": avg_delay,
            "minimum_transfer_delay": min_delay,
            "rapid_transfer_count": rapid_transfers,
            "rapid_transfer_ratio": rapid_ratio,
            
            # Pass-Through
            "pass_through_ratio": pass_through_ratio,
            "retained_amount_ratio": retained_ratio,
            
            # Cross-Bank
            "unique_banks_involved": unique_banks,
            "cross_bank_transaction_count": cross_bank_txns,
            "cross_bank_ratio": cross_bank_ratio,
            
            # Flow Patterns
            "fan_in_count": unique_senders,
            "fan_out_count": unique_receivers,
            "fan_in_ratio": fan_in_ratio,
            "fan_out_ratio": fan_out_ratio,
            
            # Off-Ramp
            "off_ramp_connection_count": off_ramp_conn,
            "off_ramp_ratio": off_ramp_ratio,
            
            # Temporal
            "transactions_per_hour": txns_per_hour,
            "transactions_per_day": txns_per_day,
            "burst_count": burst_count,
            
            # Target labels (FOR EVALUATION ONLY)
            "is_mule": is_mule,
            "network_id": network_id
        }
        
        features.append(feat_dict)
        
    features_df = pd.DataFrame(features)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    features_df.to_csv(output_path, index=False)
    print(f"Features saved to {output_path}")
    return features_df

if __name__ == "__main__":
    generate_features()
