# Architecture
Placeholder document.

## 2. Core Architecture

The architecture is divided into clear functional phases:

### Phase 1: Synthetic Data
*   **Purpose:** Generates a deterministic, realistic financial environment avoiding real PII.
*   **Components:** Account generation, base transactions, and complex fraud scenario overlays (fan-in, fan-out, multi-bank layering).

### Phase 2: Behavioural Detection + Risk Engine
*   **Purpose:** Identifies suspicious behaviour at the individual account level.
*   **Components:** Feature engineering (velocity, pass-through), Rule Engine (heuristics), Risk Scoring (0-100 tiers). 
*   *Note: Phase 2 determines behavioural risk.*

### Phase 3: Neo4j Graph + Network Reconstruction
*   **Purpose:** Maps the structural relationships of money movement across the entire dataset.
*   **Components:** Neo4j driver, Cypher queries for multi-hop tracing, cross-bank analysis, and off-ramp detection.
*   *Note: Phase 3 determines structural/network relationships. Combined with Phase 2, they produce complete network-level fraud intelligence.*

### Phase 4: Machine Learning (Upcoming)
*   **Purpose:** Replaces static rules with predictive models (Random Forest, PyTorch GNN).

### Phase 5: UI & API (Upcoming)
*   **Purpose:** React/Vite dashboard and FastAPI presentation layer.
