from backend.app.core.database import neo4j_conn

query = """
MATCH path = (victim:Account)-[t1:TRANSFER]->(m1:Account)-[t2:TRANSFER]->(m2:Account)-[t3:TRANSFER]->(m3:Account)-[t4:TRANSFER]->(offramp:Account {account_type: 'OFF_RAMP'})
WHERE victim.bank_id <> offramp.bank_id
RETURN [n in nodes(path) | n.account_id] AS path_accounts,
       [n in nodes(path) | n.bank_id] AS banks,
       length(path) AS length
LIMIT 1
"""

try:
    results = neo4j_conn.query(query)
    for res in results:
        print(f"Path: {res['path_accounts']}")
        print(f"Banks: {res['banks']}")
except Exception as e:
    print(f"Error: {e}")
