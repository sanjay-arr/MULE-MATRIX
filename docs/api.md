# API Documentation

The FastAPI backend exposes the Mule Matrix intelligence through several REST APIs.

## Architecture
- **FastAPI**: Serves the REST API endpoints.
- **Neo4j Driver**: Connects to the graph database to reconstruct networks and trace money trails.
- **In-Memory Store**: Caches data from `data/processed` for quick serving.

## Running the API
```bash
uvicorn backend.main:app --reload
```
Swagger UI is available at `http://127.0.0.1:8000/docs`

## Endpoints

### 1. Health
- `GET /api/health` - Check API health.
- `GET /api/health/neo4j` - Check Neo4j connection.

### 2. Accounts
- `GET /api/accounts` - List accounts (supports pagination, filtering).
- `GET /api/accounts/{account_id}` - Get detailed account information including risk score and rules.
- `GET /api/accounts/{account_id}/neighbors` - Get directly connected accounts.

### 3. Transactions
- `GET /api/transactions` - List transactions.
- `GET /api/transactions/{transaction_id}` - Get transaction details.

### 4. Networks
- `GET /api/networks` - List all reconstructed suspicious networks.
- `GET /api/networks/{network_id}` - Get network details.
- `GET /api/networks/{network_id}/graph` - Get node and edge data for frontend visualization.
- `GET /api/networks/{network_id}/money-trail` - Trace the money flow through the network.
- `GET /api/networks/{network_id}/off-ramps` - Get paths to known off-ramp accounts.

### 5. Investigations
- `POST /api/investigations` - Generate an investigation for a suspicious account.
- `GET /api/investigations/{investigation_id}` - Retrieve an investigation.
- `GET /api/investigations/{investigation_id}/report` - Get a structured report.

### 6. Analytics
- `GET /api/analytics/overview` - Get platform-wide statistics.
- `GET /api/analytics/risk-distribution` - Get distribution of risk levels.
- `GET /api/analytics/bank-risk` - Get risk statistics grouped by bank.

## Error Handling
Standard HTTP status codes are used:
- `400`: Invalid request
- `404`: Resource not found
- `500`: Internal server error
- `503`: Service unavailable (e.g., Neo4j connection failed)
