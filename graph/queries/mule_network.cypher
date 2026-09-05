// mule_network.cypher
// Identifies candidate mule networks by traversing connections 
// Note: We are simulating that Risk >= $min_risk acts as a filter

MATCH (mule:Account)
WHERE mule.account_type <> 'OFF_RAMP'
// We can use a property or pass a list of suspicious accounts to start the network.
// In this prototype, we'll start with known suspicious nodes from Phase 2
WITH mule
MATCH p = (mule)-[:TRANSFER*1..3]-(connected:Account)
// Ensure they are also in our suspicious list (passed as parameter if needed) or just find the raw structural cluster
RETURN 
    mule.account_id AS origin, 
    collect(distinct connected.account_id) AS network_accounts,
    count(distinct connected) AS size
ORDER BY size DESC;
