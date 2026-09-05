# Mule Matrix - GNN Methodology

## Phase 8: GNN / Advanced Graph Intelligence

This document outlines the evaluation and architectural design regarding the experimental Graph Neural Network (GNN) implementation for Mule Matrix (Phase 8).

---

## 1. Objective and Status

The primary goal of Phase 8 was to implement an experimental Graph Neural Network (GNN) capable of identifying money mule accounts by leveraging multi-hop structural relationships in the transaction network. The model would learn from graph motifs, community density, cross-bank connectivity, and fund-splitting behaviors that standard tabular models (like the Random Forest from Phase 7) might miss.

**STATUS: EXPERIMENTAL / UNAVAILABLE**

During the system environmental check, it was determined that the deployment environment runs **Python 3.13 on a Windows architecture without native, stable PyTorch Geometric (PyG) binary extensions**.

As per the stringent failure-safety requirements of the Mule Matrix system ("*If the environment cannot reliably support PyTorch Geometric: STOP the GNN implementation and report the compatibility problem. Do NOT break the existing project just to force GNN support*"), the active GNN backend module has been disabled to prevent instability or crashes of the primary FastApi server.

The existing Rule Engine, Graph Risk Engine, and Phase 7 Random Forest ML remain the primary and highly reliable combined-risk baseline.

---

## 2. Intended Graph Representation

If successfully deployed in a compatible environment (e.g., Linux/Ubuntu with CUDA 11.8+ and stable PyTorch 2.x wheels), the graph representation would be constructed as follows:

### Node Definition
- **Nodes**: Bank Accounts (`account_id`).
- **Node Features**: The same 21 non-leaking behavioral statistics generated for Phase 7 (e.g., `pass_through_ratio`, `unique_counterparties`, `incoming_outgoing_ratio`, `cross_bank_transactions`). Explicit identifiers (`account_id`, `network_id`) are discarded.

### Edge Definition
- **Edges**: Directed financial transactions between accounts.
- **Edge Attributes**: Normalized `transaction_amount`, encoded `transaction_type`.
- **Structure**: Modeled in PyTorch Geometric using a directed `edge_index` tensor of shape `[2, num_edges]`.

---

## 3. Intended Model Architecture

The intended baseline architecture was a **Graph Convolutional Network (GCN)** (`GCNConv` layers from `torch_geometric.nn`):

1. **Input Layer**: Maps the 21-dimensional node features into a 64-dimensional hidden space.
2. **Message Passing (2-3 Hops)**: 2 to 3 `GCNConv` layers. This allows each node to aggregate financial flow statistics from its direct counterparties and the counterparties of its counterparties (capturing multi-hop mule behavior like structuring and integration).
3. **Activation**: ReLU activations with Dropout (0.5) to prevent overfitting on the synthetic graph.
4. **Classification Head**: A simple Linear layer outputting a single logit, passed through a Sigmoid to calculate the predicted `mule_probability`.

---

## 4. Comparison Methodology

The methodology for comparing the models relies on the stratified 80/20 train/test split. 
Since the GNN relies on message passing, the entire graph is passed into the model, but loss calculation and metric evaluation are strictly masked using `train_mask`, `val_mask`, and `test_mask`.

**Baseline Comparison (Tabular vs. Graph):**
Currently, the Phase 7 Random Forest achieves:
- **Precision**: ~94.1%
- **Recall**: ~94.1%
- **F1 Score**: ~94.1%
- **ROC-AUC**: ~99.9%

The expected advantage of the GNN is to increase **Recall** for highly complex, low-volume mule accounts that disguise their tabular metrics but are structurally embedded deep within a known suspicious network.

---

## 5. Limitations and Next Steps

**Why GNN is Optional:**
Graph Neural Networks introduce significant overhead:
1. **Computational Complexity**: Real-time inference requires extracting ego-graphs (k-hop neighborhoods) dynamically from Neo4j, which is an O(N^k) operation.
2. **Dependency Fragility**: PyTorch Geometric relies heavily on specific C++ bindings (`torch_sparse`, `torch_scatter`) that frequently break across OS and Python version updates.

**Future Work:**
To deploy the GNN safely:
1. Migrate the environment to an LTS Python version (e.g., 3.11) with stable PyG wheels.
2. Containerize the ML inference pipeline into an isolated microservice (e.g., a separate Docker container) that communicates with the main FastAPI server via gRPC, ensuring that deep learning dependency conflicts do not crash the core application logic.
