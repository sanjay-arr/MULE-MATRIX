// seed.cypher
// Deterministic development example for manual testing

MERGE (v:Account {account_id: 'VICTIM_001'}) SET v.account_type = 'NORMAL', v.bank_id = 'BANK_A'
MERGE (m1:Account {account_id: 'MULE_A'}) SET m1.account_type = 'MULE', m1.bank_id = 'BANK_A'
MERGE (m2:Account {account_id: 'MULE_B'}) SET m2.account_type = 'MULE', m2.bank_id = 'BANK_B'
MERGE (m3:Account {account_id: 'MULE_C'}) SET m3.account_type = 'MULE', m3.bank_id = 'BANK_C'
MERGE (o:Account {account_id: 'OFFRAMP_001'}) SET o.account_type = 'OFF_RAMP', o.bank_id = 'EXCHANGE_X'

MERGE (v)-[:TRANSFER {transaction_id: 'TX1', amount: 50000, timestamp: '2023-01-01T10:00:00'}]->(m1)
MERGE (m1)-[:TRANSFER {transaction_id: 'TX2', amount: 48500, timestamp: '2023-01-01T10:05:00'}]->(m2)
MERGE (m2)-[:TRANSFER {transaction_id: 'TX3', amount: 47500, timestamp: '2023-01-01T10:30:00'}]->(m3)
MERGE (m3)-[:TRANSFER {transaction_id: 'TX4', amount: 47000, timestamp: '2023-01-01T11:00:00'}]->(o)
