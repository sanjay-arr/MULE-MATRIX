# Demo Scenario — Operation Cross-Bank Mule Network

## Overview

This document defines the **deterministic demo scenario** for the Mule Matrix hackathon presentation. The scenario is pre-selected from the actual synthetic Neo4j dataset and will produce consistent results across every run.

## Scenario Identity

| Field | Value |
|---|---|
| **Operation Name** | Operation Cross-Bank Mule Network |
| **Target Account** | `CUS_7E3E2ACD` |
| **Bank** | BANK_A |
| **Account Type** | CUSTOMER |
| **Risk Score** | 85 / 100 |
| **Risk Level** | CRITICAL |
| **Triggered Rules** | 7 |
| **Off-Ramp Account** | `OFF_NORM_6BD55AA4` (BANK_D) |
| **Cross-Bank Transactions** | 7 |
| **Connected Accounts** | 12 |
| **Banks Involved** | BANK_A, BANK_B, BANK_C, BANK_D, BANK_E |

## Behavioural Evidence

| Rule | Description |
|---|---|
| `HIGH_PASS_THROUGH` | 256% of incoming funds were transferred out (near-zero retention) |
| `MANY_COUNTERPARTIES` | 12 unique counterparties detected |
| `CROSS_BANK_MOVEMENT` | Transactions crossed 5 distinct banks |
| `FAN_IN` | Received funds from 4 distinct sources |
| `FAN_OUT` | Sent funds to 8 distinct destinations |
| `FUND_SPLITTING` | High ratio of outgoing to incoming transactions (2.0×) |
| `OFF_RAMP_CONNECTION` | Direct connection to off-ramp account |

## Network Structure

```
[Multiple Sources] (BANK_B, BANK_C, BANK_E)
         ↓
 CUS_7E3E2ACD  ← TARGET MULE ACCOUNT (BANK_A)
         ↓              (receives and immediately disperses)
[Multiple Intermediaries]
         ↓
 OFF_NORM_6BD55AA4  ← OFF-RAMP (BANK_D)
```

## ML Intelligence

| Signal | Value |
|---|---|
| **Model** | Random Forest Classifier |
| **Prediction** | MULE |
| **Mule Probability** | Live inference from saved model |

## Demo Navigation Flow

```
Dashboard
    → Click "RUN DEMO INVESTIGATION"
    → Account Explorer (CUS_7E3E2ACD auto-selected)
        → Risk Assessment (Score 85, CRITICAL)
        → Triggered Rules (7 rules)
        → ML Signal (mule probability)
        → "Start Investigation"
    → Investigation Workspace
        → Three Intelligence Layers (Rule / ML / Graph)
        → Key Evidence
        → Money Trail
        → Off-Ramp identified
        → "View Network Graph"
    → Network Explorer
        → Graph visualization
        → Node/edge relationships
    → Analytics
        → Risk distribution
        → Bank comparison
        → ML performance
```

## API Endpoint

```
GET /api/demo/scenario
```

Returns the full scenario metadata deterministically. No randomness.

## Reliability

- The demo account `CUS_7E3E2ACD` is fixed in `backend/app/api/routes/demo.py`
- All values are sourced from the actual Neo4j + detection pipeline
- No values are hardcoded in the frontend
- The scenario produces identical results on every run
