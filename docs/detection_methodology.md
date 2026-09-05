# Mule Matrix Detection Methodology

## Overview
This document outlines the behavioural detection architecture built during Phase 2. This represents the "brain" of the Mule Matrix prototype, using heuristics and synthetic behavioural signals to classify accounts into risk tiers.

> **IMPORTANT DISCLAIMER**
> This is a synthetic-data hackathon prototype. Risk scores are intended for demonstration and evaluation only and are not real-world financial decisions. No actual customer data or live banking APIs are utilized.

## 1. Feature Engineering
The system extracts account-level features from raw transaction graphs:
*   **Basic**: Volume and total value of transactions, age of account.
*   **Counterparty**: Number of unique senders/receivers.
*   **Velocity**: The delay between incoming and subsequent outgoing transactions. Short delays result in high "rapid transfer ratios".
*   **Pass-Through**: The ratio of funds sent out vs. funds received.
*   **Cross-Bank**: Number of distinct banks an account touches.
*   **Flow Patterns**: Fan-In (many-to-one) and Fan-Out (one-to-many) counters.
*   **Off-Ramp**: Connections to flagged pseudo-crypto/cash withdrawal entities.

## 2. Rule Engine
A deterministic rule engine evaluates the engineered features:
1.  **RAPID FUND MOVEMENT**: Flags accounts executing outgoing transfers shortly after an incoming transfer.
2.  **HIGH PASS-THROUGH**: Flags accounts that transfer out >85% of what they receive.
3.  **MANY COUNTERPARTIES**: Flags abnormal connectivity density.
4.  **CROSS-BANK MOVEMENT**: Flags accounts heavily bridging multiple banks.
5.  **FAN-IN / FAN-OUT**: Flags structural money aggregation/distribution.
6.  **FUND SPLITTING**: Flags high outgoing-to-incoming transaction count ratio.
7.  **OFF-RAMP CONNECTION**: Flags direct ties to liquidation nodes.
8.  **BURST ACTIVITY**: Flags high-frequency activity windows.

## 3. Risk Scoring
Each rule contributes a fixed weight (10-20 points) to an account's overall Risk Score.
*   **Capping**: The maximum score is capped at 100.
*   **Levels**:
    *   0–30: LOW
    *   31–60: MEDIUM
    *   61–80: HIGH
    *   81–100: CRITICAL

## 4. Explainability
To assist investigators, the system generates human-readable rationales based on triggered rules. Explanations correspond directly to the feature data, e.g., `"High pass-through behaviour: 95% of incoming funds were transferred out."`

## 5. Threshold Selection & Evaluation
A threshold sweep (30, 40, 50, 60, 70, 80) is executed against the synthetic ground truth labels. 
*   **Selected Threshold**: A score of **50** is generally established as the operating point for this synthetic environment to balance False Positives (preventing friction for normal users) and Recall (capturing mule networks).
*   **Metrics Tracked**: Accuracy, Precision, Recall, F1 Score, and False Positive Rate.

## Limitations
*   Features are derived purely from synthetic constraints.
*   Advanced graph-topological features (eigenvector centrality, PageRank) are deferred to the GNN implementation in future phases.
*   The static rule engine weights are arbitrarily defined for prototype purposes and would require empirical tuning in a real setting.
