import os
from backend.app.core.database import neo4j_conn

class GraphService:
    def __init__(self):
        self.conn = neo4j_conn

    def connect_to_neo4j(self):
        self.conn.connect()

    def clear_database(self):
        query = "MATCH (n) DETACH DELETE n"
        self.conn.query(query)

    def create_constraints(self):
        queries = [
            "CREATE CONSTRAINT account_id_unique IF NOT EXISTS FOR (a:Account) REQUIRE a.account_id IS UNIQUE;",
            "CREATE INDEX account_bank_id_idx IF NOT EXISTS FOR (a:Account) ON (a.bank_id);",
            "CREATE INDEX account_type_idx IF NOT EXISTS FOR (a:Account) ON (a.account_type);"
        ]
        for q in queries:
            self.conn.query(q)

    def load_accounts(self, accounts_df):
        query = """
        UNWIND $accounts AS acc
        MERGE (a:Account {account_id: acc.account_id})
        SET a.bank_id = acc.bank_id,
            a.account_type = acc.account_type,
            a.account_age_days = acc.account_age_days,
            a.is_mule_ground_truth = acc.is_mule
        """
        # Convert df to list of dicts for Neo4j Unwind
        accounts_list = accounts_df[['account_id', 'bank_id', 'account_type', 'account_age_days', 'is_mule']].to_dict('records')
        self.conn.query(query, parameters={"accounts": accounts_list})
        return len(accounts_list)

    def load_transactions(self, transactions_df):
        query = """
        UNWIND $transactions AS txn
        MATCH (sender:Account {account_id: txn.sender_account})
        MATCH (receiver:Account {account_id: txn.receiver_account})
        MERGE (sender)-[t:TRANSFER {transaction_id: txn.transaction_id}]->(receiver)
        SET t.amount = toFloat(txn.amount),
            t.timestamp = txn.timestamp,
            t.transaction_type = txn.transaction_type,
            t.sender_bank = txn.sender_bank,
            t.receiver_bank = txn.receiver_bank,
            t.is_suspicious_ground_truth = txn.is_suspicious
        """
        # Batch to avoid huge memory spikes, though 10k is fine for a single UNWIND.
        # We will cast datetime to string
        txns_copy = transactions_df.copy()
        txns_copy['timestamp'] = txns_copy['timestamp'].astype(str)
        # Keep relevant columns
        cols = ['transaction_id', 'sender_account', 'receiver_account', 'amount', 'timestamp', 'transaction_type', 'sender_bank', 'receiver_bank', 'is_suspicious']
        txns_list = txns_copy[cols].to_dict('records')
        
        batch_size = 2000
        for i in range(0, len(txns_list), batch_size):
            batch = txns_list[i:i+batch_size]
            self.conn.query(query, parameters={"transactions": batch})
            
        return len(txns_list)

    def get_account(self, account_id):
        query = "MATCH (a:Account {account_id: $account_id}) RETURN a"
        res = self.conn.query(query, parameters={"account_id": account_id})
        return res[0]['a'] if res else None

    def get_account_neighbors(self, account_id):
        query = """
        MATCH (a:Account {account_id: $account_id})-[r:TRANSFER]-(neighbor:Account)
        RETURN neighbor.account_id AS neighbor_id, type(r) AS rel_type, r.amount AS amount, startNode(r).account_id = a.account_id AS is_outgoing
        """
        return self.conn.query(query, parameters={"account_id": account_id})

    def get_transaction_path(self, start_account, end_account, max_hops=5):
        query = f"""
        MATCH p = (a:Account {{account_id: $start_account}})-[:TRANSFER*1..{max_hops}]->(b:Account {{account_id: $end_account}})
        RETURN [n in nodes(p) | n.account_id] AS path, [r in relationships(p) | r.amount] AS amounts
        """
        return self.conn.query(query, parameters={"start_account": start_account, "end_account": end_account})

    def get_multi_hop_paths(self, start_account, max_hops=5):
        query = f"""
        MATCH p = (a:Account {{account_id: $start_account}})-[:TRANSFER*2..{max_hops}]->(b:Account)
        RETURN p
        """
        return self.conn.query(query, parameters={"start_account": start_account})

    def get_cross_bank_connections(self):
        query = """
        MATCH (a:Account)-[t:TRANSFER]->(b:Account)
        WHERE a.bank_id <> b.bank_id
        RETURN a.account_id, b.account_id, a.bank_id, b.bank_id, t.amount
        """
        return self.conn.query(query)

    def get_off_ramp_paths(self, max_hops=5):
        query = f"""
        MATCH p = (start:Account)-[:TRANSFER*1..{max_hops}]->(offramp:Account)
        WHERE offramp.account_type = 'OFF_RAMP'
        RETURN start.account_id AS origin, [n in nodes(p) | n.account_id] AS path, [r in relationships(p) | r.amount] AS amounts, length(p) AS hop_count
        """
        return self.conn.query(query)

    def get_network_statistics(self):
        stats = {}
        res = self.conn.query("MATCH (a:Account) RETURN count(a) AS account_count")
        stats['accounts'] = res[0]['account_count'] if res else 0
        
        res = self.conn.query("MATCH ()-[t:TRANSFER]->() RETURN count(t) AS tx_count")
        stats['transactions'] = res[0]['tx_count'] if res else 0
        
        res = self.conn.query("MATCH (a:Account) RETURN count(distinct a.bank_id) AS bank_count")
        stats['banks'] = res[0]['bank_count'] if res else 0
        
        res = self.conn.query("MATCH ()-[t:TRANSFER]->() WHERE t.sender_bank <> t.receiver_bank RETURN count(t) AS cross_bank_count")
        stats['cross_bank_transactions'] = res[0]['cross_bank_count'] if res else 0
        
        res = self.conn.query("MATCH (a:Account {account_type: 'OFF_RAMP'}) RETURN count(a) AS off_ramp_count")
        stats['off_ramp_accounts'] = res[0]['off_ramp_count'] if res else 0
        
        return stats
