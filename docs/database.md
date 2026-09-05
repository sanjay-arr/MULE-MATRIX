# Mule Matrix - Graph Database Documentation

## 1. Neo4j Setup
Mule Matrix utilizes Neo4j as the core engine for structural money-laundering detection. 
The database is containerized via Docker Compose.
*   **URI:** `bolt://localhost:7687`
*   **Auth:** Configured via `.env` (default: `neo4j` / `password`)

## 2. Node Model
The primary entity is the `Account`.
**Properties:**
*   `account_id`: String (Unique constraint)
*   `bank_id`: String (Indexed)
*   `account_type`: Enum ('NORMAL', 'MULE', 'OFF_RAMP', etc.) (Indexed)
*   `account_age_days`: Integer

## 3. Relationship Model
Money movement is modeled as a directed relationship: `(Account)-[:TRANSFER]->(Account)`
**Properties:**
*   `transaction_id`: String
*   `amount`: Float
*   `timestamp`: Datetime String
*   `transaction_type`: String
*   `sender_bank`: String
*   `receiver_bank`: String

## 4. Constraints & Indexes
*   **Constraints:** Unique constraint on `Account.account_id` ensures no duplication during batch loading.
*   **Indexes:** Indexes on `bank_id` and `account_type` accelerate cross-bank and off-ramp traversal queries.

## 5. Important Cypher Queries
All operational queries are stored in `graph/queries/`.
*   **Multi-hop tracing (`money_trail.cypher`):** Utilizes variable-length paths `[:TRANSFER*1..5]` constrained by chronological timestamp validation to trace actual money flow.
*   **Cross-bank analysis (`cross_bank.cypher`):** Detects structural networks that span across multiple synthetic banks by validating `sender_bank <> receiver_bank`.
*   **Off-ramp detection (`off_ramp.cypher`):** Finds the shortest paths from suspicious accounts directly to defined 'OFF_RAMP' nodes.
