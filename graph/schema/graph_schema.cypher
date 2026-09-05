// graph_schema.cypher

// 1. Account Constraints
CREATE CONSTRAINT account_id_unique IF NOT EXISTS FOR (a:Account) REQUIRE a.account_id IS UNIQUE;

// 2. Transaction Constraints (if transactions are modeled as nodes, though in this model they are relationships. For properties on relationships, indexes are supported in newer Neo4j versions, but let's stick to node indexes for now)

// 3. Bank Index for fast cross-bank lookups
CREATE INDEX account_bank_id_idx IF NOT EXISTS FOR (a:Account) ON (a.bank_id);
CREATE INDEX account_type_idx IF NOT EXISTS FOR (a:Account) ON (a.account_type);

// The conceptual model:
// (Account)-[t:TRANSFER {transaction_id: "...", amount: 500, timestamp: "...", sender_bank: "...", receiver_bank: "..."}]->(Account)
