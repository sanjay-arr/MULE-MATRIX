// money_trail.cypher
// Traces money across multiple hops preserving chronological order
// Parameters: $start_account, $max_hops

MATCH p = (start:Account {account_id: $start_account})-[:TRANSFER*1..5]->(end:Account)
WHERE length(p) <= $max_hops
WITH p, nodes(p) AS accounts, relationships(p) AS transfers
// Ensure chronological order for a valid trail
WHERE all(i in range(0, size(transfers)-2) WHERE transfers[i].timestamp <= transfers[i+1].timestamp)
RETURN 
    [a in accounts | a.account_id] AS account_ids,
    [a in accounts | a.bank_id] AS bank_ids,
    [t in transfers | t.amount] AS amounts,
    [t in transfers | t.timestamp] AS timestamps,
    [t in transfers | t.transaction_id] AS transaction_ids,
    length(p) AS hop_number
ORDER BY hop_number DESC
LIMIT 100;
