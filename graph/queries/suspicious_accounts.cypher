// suspicious_accounts.cypher
// Returns accounts flagged with high structural anomaly (e.g. high degree centrality combined with risk)

MATCH (a:Account)
WHERE a.account_type <> 'OFF_RAMP'
WITH a
MATCH (a)-[r:TRANSFER]-()
WITH a, count(r) AS degree
ORDER BY degree DESC
LIMIT 50
RETURN 
    a.account_id AS account_id, 
    a.bank_id AS bank, 
    degree AS connection_count;
