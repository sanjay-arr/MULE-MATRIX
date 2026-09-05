// cross_bank.cypher
// Detects structural networks that span across multiple banks

MATCH p = (a:Account)-[t:TRANSFER]->(b:Account)
WHERE a.bank_id <> b.bank_id
RETURN 
    a.account_id AS sender, 
    b.account_id AS receiver, 
    a.bank_id AS sender_bank, 
    b.bank_id AS receiver_bank, 
    t.amount AS amount,
    t.transaction_id AS transaction_id
ORDER BY amount DESC;
