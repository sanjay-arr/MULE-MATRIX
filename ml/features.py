import pandas as pd
import numpy as np
import os

def build_account_features(accounts_df, transactions_df):
    """
    Builds a DataFrame of features for each account in accounts_df.
    Returns:
        features_df: DataFrame containing only numerical features and account_id
        labels: Series containing target labels (1 for mule, 0 for normal)
    """
    # 1. Transactions where account is sender
    out_tx = transactions_df.groupby('sender_account').agg(
        outgoing_transaction_count=('transaction_id', 'count'),
        total_outgoing_amount=('amount', 'sum'),
        unique_receiving_accounts=('receiver_account', 'nunique'),
        max_outgoing_amount=('amount', 'max'),
        avg_outgoing_amount=('amount', 'mean')
    ).reset_index().rename(columns={'sender_account': 'account_id'})
    
    # 2. Transactions where account is receiver
    in_tx = transactions_df.groupby('receiver_account').agg(
        incoming_transaction_count=('transaction_id', 'count'),
        total_incoming_amount=('amount', 'sum'),
        unique_sending_accounts=('sender_account', 'nunique'),
        max_incoming_amount=('amount', 'max'),
        avg_incoming_amount=('amount', 'mean')
    ).reset_index().rename(columns={'receiver_account': 'account_id'})
    
    # 3. Cross bank txns
    cross_bank = transactions_df[transactions_df['sender_bank'] != transactions_df['receiver_bank']]
    out_cross = cross_bank.groupby('sender_account').size().reset_index(name='outgoing_cross_bank_count').rename(columns={'sender_account': 'account_id'})
    in_cross = cross_bank.groupby('receiver_account').size().reset_index(name='incoming_cross_bank_count').rename(columns={'receiver_account': 'account_id'})
    
    # Merge all to a subset of accounts_df
    df = accounts_df[['account_id', 'is_mule', 'account_age_days']].copy()
    
    df = pd.merge(df, out_tx, on='account_id', how='left')
    df = pd.merge(df, in_tx, on='account_id', how='left')
    df = pd.merge(df, out_cross, on='account_id', how='left')
    df = pd.merge(df, in_cross, on='account_id', how='left')
    
    # Fill NAs
    fill_cols = [
        'outgoing_transaction_count', 'total_outgoing_amount', 'unique_receiving_accounts', 
        'max_outgoing_amount', 'avg_outgoing_amount',
        'incoming_transaction_count', 'total_incoming_amount', 'unique_sending_accounts', 
        'max_incoming_amount', 'avg_incoming_amount',
        'outgoing_cross_bank_count', 'incoming_cross_bank_count'
    ]
    df[fill_cols] = df[fill_cols].fillna(0)
    
    # Derived features
    df['total_transaction_count'] = df['incoming_transaction_count'] + df['outgoing_transaction_count']
    df['total_transaction_amount'] = df['total_incoming_amount'] + df['total_outgoing_amount']
    df['cross_bank_transactions'] = df['outgoing_cross_bank_count'] + df['incoming_cross_bank_count']
    
    # Pass through ratio (close to 1 means money in is similar to money out)
    df['pass_through_ratio'] = np.minimum(df['total_incoming_amount'], df['total_outgoing_amount']) / \
                               (np.maximum(df['total_incoming_amount'], df['total_outgoing_amount']) + 1)
                               
    # Incoming/Outgoing ratio
    df['incoming_outgoing_ratio'] = df['total_incoming_amount'] / (df['total_outgoing_amount'] + 1)
    
    df['unique_counterparties'] = df['unique_receiving_accounts'] + df['unique_sending_accounts']
    
    df['max_transaction_amount'] = np.maximum(df['max_incoming_amount'], df['max_outgoing_amount'])
    df['avg_transaction_amount'] = df['total_transaction_amount'] / (df['total_transaction_count'] + 1)
    
    # Ensure account_age_days is numeric and handle missing
    df['account_age_days'] = df['account_age_days'].fillna(0)
    
    # Extract labels
    labels = df['is_mule'].astype(int) if 'is_mule' in df.columns else None
    
    # Drop non-feature columns
    drop_cols = ['is_mule'] if 'is_mule' in df.columns else []
    features_df = df.drop(columns=drop_cols)
    
    # Ensure standard ordering of columns (minus account_id which will be used as index later)
    feature_cols = [
        'account_id', 'account_age_days',
        'outgoing_transaction_count', 'total_outgoing_amount', 'unique_receiving_accounts',
        'max_outgoing_amount', 'avg_outgoing_amount',
        'incoming_transaction_count', 'total_incoming_amount', 'unique_sending_accounts',
        'max_incoming_amount', 'avg_incoming_amount',
        'outgoing_cross_bank_count', 'incoming_cross_bank_count',
        'total_transaction_count', 'total_transaction_amount', 'cross_bank_transactions',
        'pass_through_ratio', 'incoming_outgoing_ratio', 'unique_counterparties',
        'max_transaction_amount', 'avg_transaction_amount'
    ]
    
    # Only keep the defined feature columns
    features_df = features_df[[col for col in feature_cols if col in features_df.columns]]
    
    return features_df, labels

def get_feature_names():
    return [
        'account_age_days',
        'outgoing_transaction_count', 'total_outgoing_amount', 'unique_receiving_accounts',
        'max_outgoing_amount', 'avg_outgoing_amount',
        'incoming_transaction_count', 'total_incoming_amount', 'unique_sending_accounts',
        'max_incoming_amount', 'avg_incoming_amount',
        'outgoing_cross_bank_count', 'incoming_cross_bank_count',
        'total_transaction_count', 'total_transaction_amount', 'cross_bank_transactions',
        'pass_through_ratio', 'incoming_outgoing_ratio', 'unique_counterparties',
        'max_transaction_amount', 'avg_transaction_amount'
    ]
