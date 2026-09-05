# 🛡️ Mule Matrix

**Financial Crime Intelligence Platform — Hackathon Prototype**

---

## The Problem

Money mule networks are a primary mechanism for laundering illicit funds. They operate by recruiting individuals to receive and forward funds, obscuring the trail from origin to destination. Traditional transaction monitoring identifies individual suspicious transactions but **fails to detect the coordinated network structure** underlying modern mule operations.

## The Solution

Mule Matrix combines **behavioural detection**, **machine learning**, **Neo4j graph intelligence**, and an **investigator workspace** into a unified financial crime intelligence platform.

```
Detect → Score → Connect → Trace → Investigate → Explain
```

---

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Neo4j Community 5.x (or Docker)
- pip, npm

### 1. Start Neo4j
```bash
# Via Docker:
docker run -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:5
```

### 2. Start Backend
```bash
cd MULE-MATRIX
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload
```

### 3. Start Frontend
```bash
cd MULE-MATRIX/frontend
npm install
npm run dev
```

### 4. Open the App
```
http://localhost:5173
```

### 5. Click "Run Demo Investigation"
The button on the Dashboard launches the full demo scenario.

---

## Technology Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 18 + Vite + React Router |
| **Backend** | Python 3.x + FastAPI + Uvicorn |
| **Graph DB** | Neo4j 5 (Bolt/Cypher) |
| **ML** | scikit-learn (Random Forest) |
| **GNN** | PyTorch Geometric (optional, env-dependent) |
| **Data** | Synthetic labelled transaction dataset |
| **Visualization** | D3.js / Force-Directed Graph |

---

## System Architecture

```
Synthetic Dataset (1607 Accounts, 10077 Transactions)
         ↓
Feature Engineering (21 behavioural features)
         ↓
Rule Engine ────────────────────────────┐
  · HIGH_PASS_THROUGH                   │
  · MANY_COUNTERPARTIES                 ├→ Combined Risk Score
  · CROSS_BANK_MOVEMENT                 │   (Rule + ML + Graph)
  · FAN_IN / FAN_OUT                    │
  · FUND_SPLITTING                      │
  · OFF_RAMP_CONNECTION                 │
         ↓                              │
Random Forest ML ─────────────────────→┘
  · Precision: 94.1%                    
  · Recall:    94.1%                    
  · F1 Score:  94.1%                    
  · ROC-AUC:   99.9%                    
         ↓
Neo4j Transaction Graph
  · Network Reconstruction
  · Money Trail
  · Off-Ramp Detection
         ↓
FastAPI REST Backend
         ↓
React Dashboard
  · Dashboard → Alerts → Account Explorer
  · Network Explorer → Investigations → Analytics
```

---

## Features

### Dashboard
- Real-time aggregate statistics from Neo4j + detection engine
- Risk distribution visualization
- Recent critical alerts
- **RUN DEMO INVESTIGATION** — one-click deterministic demo flow

### Alerts
- Live suspicious account alerts sorted by severity (CRITICAL → HIGH → SUSPICIOUS)
- Rule trigger summary per alert
- Click-through to Account Explorer

### Account Explorer
- Search and browse 1,607 accounts
- Full risk profile (score, level, triggered rules, explanations)
- ML prediction signal (mule probability from Random Forest)
- Connected accounts / transaction neighborhood

### Network Explorer
- 10 detected mule networks
- D3.js force-directed graph (interactive, zoomable, pannable)
- Node color-coding by risk level
- Edge = transaction direction
- Money trail chain

### Investigation Workspace
- Three intelligence layers: Rule Engine + ML + Graph Intelligence
- Key evidence display (behavioural explanations)
- Reconstructed money trail
- Off-ramp identification
- Network navigation

### Analytics
- Risk distribution (CRITICAL / HIGH / SUSPICIOUS / NORMAL)
- Bank risk comparison (suspicious accounts per institution)
- Cross-bank volume, off-ramp count, mule network count
- ML model performance dashboard (Precision, Recall, F1, ROC-AUC)
- Model comparison table (Rule Engine vs Random Forest vs GNN)

---

## Data

All data is **synthetic** and does not represent real individuals, transactions, or financial institutions.

```
Accounts:               1,607
Transactions:           10,077
Banks:                  5 (BANK_A through BANK_E)
Mule Networks:          10
Cross-Bank Transactions: 8,044
Off-Ramp Accounts:      20
```

---

## Demo Scenario

**Operation Cross-Bank Mule Network**

| Field | Value |
|---|---|
| Target Account | CUS_7E3E2ACD |
| Bank | BANK_A |
| Risk Level | CRITICAL |
| Risk Score | 85 / 100 |
| Triggered Rules | 7 (all major mule behaviours) |
| Off-Ramp | OFF_NORM_6BD55AA4 (BANK_D) |
| Cross-Bank Transactions | 7 |
| Connected Accounts | 12 |
| Banks Involved | BANK_A, B, C, D, E |

---

## ML Performance

| Metric | Random Forest |
|---|---|
| Precision | 94.1% |
| Recall | 94.1% |
| F1 Score | 94.1% |
| ROC-AUC | 99.9% |
| Test Samples | 322 |

Top features: `total_transaction_count`, `unique_counterparties`, `unique_sending_accounts`, `cross_bank_transactions`

---

## ⚠️ Disclaimer

This is a **hackathon prototype** using **synthetic data only**.

- No real bank integration
- No real customer data
- No real CBDC integration
- Not a production AML system
- Demonstrates an investigative intelligence workflow

---

## Phase Summary

| Phase | Description | Status |
|---|---|---|
| 0–1 | Data generation + Neo4j loading | ✅ Complete |
| 2–3 | Rule-based detection + risk scoring | ✅ Complete |
| 4–5 | Network reconstruction + API | ✅ Complete |
| 6 | React frontend integration | ✅ Complete |
| 7 | Random Forest ML | ✅ Complete |
| 8 | GNN (Graph Neural Network) | ⚠️ Unavailable (Python 3.13 / Windows env) |
| 9 | Hackathon polish + demo | ✅ Complete |
