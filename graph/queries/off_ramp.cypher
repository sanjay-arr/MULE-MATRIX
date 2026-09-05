// off_ramp.cypher
// Identifies accounts connected directly or multi-hop to an off-ramp

MATCH p = (origin:Account)-[t:TRANSFER*1..5]->(offramp:Account)
WHERE offramp.account_type = 'OFF_RAMP'
// Chronological flow
WHERE all(i in range(0, size(t)-2) WHERE t[i].timestamp <= t[i+1].timestamp)
RETURN 
    origin.account_id AS origin_account,
    offramp.account_id AS off_ramp_account,
    length(p) AS hop_count,
    [rel in t | rel.amount] AS amounts,
    last(t).transaction_id AS final_transaction_id,
    [n in nodes(p) | n.account_id] AS path
ORDER BY hop_count ASC;
