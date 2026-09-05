import pandas as pd
import uuid

class NetworkService:
    def __init__(self, graph_service, risk_results_df=None):
        self.gs = graph_service
        # Assume risk_results_df has ['account_id', 'risk_score', 'risk_level']
        self.risk_results = risk_results_df

    def reconstruct_network(self, account_id, max_hops=3):
        """
        Reconstructs a mule network starting from a flagged account.
        Finds the weakly connected component via transfers.
        """
        # We can use the graph service to pull neighbors
        query = f"""
        MATCH p = (start:Account {{account_id: $account_id}})-[:TRANSFER*1..{max_hops}]-(connected:Account)
        RETURN 
            [n in nodes(p) | n.account_id] AS path_accounts,
            [n in nodes(p) | n.bank_id] AS path_banks,
            [n in nodes(p) | n.account_type] AS path_types,
            [r in relationships(p) | r.amount] AS amounts,
            [r in relationships(p) | r.transaction_id] AS transactions,
            [r in relationships(p) | startNode(r).bank_id <> endNode(r).bank_id] AS is_cross_bank
        """
        res = self.gs.conn.query(query, parameters={"account_id": account_id})
        
        if not res:
            return None
            
        all_accounts = set([account_id])
        all_banks = set()
        all_transactions = set()
        cross_bank_txns = 0
        total_amount = 0.0
        off_ramps = set()
        
        # Parse the paths
        for record in res:
            for acc, bank, type_ in zip(record['path_accounts'], record['path_banks'], record['path_types']):
                all_accounts.add(acc)
                all_banks.add(bank)
                if type_ == 'OFF_RAMP':
                    off_ramps.add(acc)
            
            for tx, amount, is_cb in zip(record['transactions'], record['amounts'], record['is_cross_bank']):
                if tx not in all_transactions:
                    all_transactions.add(tx)
                    total_amount += amount
                    if is_cb:
                        cross_bank_txns += 1
                        
        # Get risk data
        highest_risk = 0
        highest_risk_account = account_id
        risk_scores = []
        
        if self.risk_results is not None:
            for acc in all_accounts:
                match = self.risk_results[self.risk_results['account_id'] == acc]
                if not match.empty:
                    score = match.iloc[0]['risk_score']
                    risk_scores.append(score)
                    if score > highest_risk:
                        highest_risk = score
                        highest_risk_account = acc
        
        avg_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0
        
        network_id = f"MM-NET-{str(uuid.uuid4())[:8].upper()}"
        
        return {
            "network_id": network_id,
            "total_accounts": len(all_accounts),
            "accounts": list(all_accounts),
            "total_transactions": len(all_transactions),
            "total_amount": total_amount,
            "number_of_banks": len(all_banks),
            "banks": list(all_banks),
            "cross_bank_transactions": cross_bank_txns,
            "max_hops": max_hops, # Approx for structural depth
            "off_ramp_connections": len(off_ramps),
            "off_ramps": list(off_ramps),
            "highest_risk_account": highest_risk_account,
            "average_risk_score": avg_risk
        }
