from fastapi import APIRouter, HTTPException
from typing import List

from backend.app.schemas.network_schema import (
    NetworkListResponse, NetworkDetailResponse, GraphResponse, 
    MoneyTrailResponse, OffRampResponse
)
from backend.app.core.database import neo4j_conn
from backend.app.services.graph_service import GraphService
from backend.app.services.network_service import NetworkService
from backend.app.core.data import data_store

router = APIRouter()

gs = GraphService()
# We initialize NetworkService with detection_results DataFrame for risk info
ns = NetworkService(graph_service=gs, risk_results_df=data_store.detection_df)

# Global cache to avoid reconstructing everything on every request
_network_cache = {}
_networks_list = []

def _ensure_networks():
    global _networks_list
    if not _networks_list:
        if data_store.detection_df is None:
            return
            
        suspicious = data_store.detection_df[data_store.detection_df['is_suspicious'] == True]
        # Get suspicious accounts sorted by risk to seed networks
        seeds = suspicious.sort_values(by='risk_score', ascending=False)['account_id'].tolist()
        
        seen_accounts = set()
        for seed in seeds:
            if seed in seen_accounts:
                continue
            
            net = ns.reconstruct_network(seed, max_hops=3)
            if net and len(net['accounts']) > 1:
                _networks_list.append(net)
                _network_cache[net['network_id']] = net
                seen_accounts.update(net['accounts'])
                
            # Stop once we have found the 10 distinct networks
            if len(_networks_list) >= 10:
                break

@router.get("", response_model=NetworkListResponse)
def get_networks():
    _ensure_networks()
    
    summaries = []
    for net in _networks_list:
        summaries.append({
            "network_id": net["network_id"],
            "risk_level": "CRITICAL" if net["average_risk_score"] > 80 else ("HIGH" if net["average_risk_score"] > 60 else "MEDIUM"),
            "accounts": net["total_accounts"],
            "banks": net["number_of_banks"],
            "total_amount": net["total_amount"],
            "max_hops": net["max_hops"],
            "off_ramps": net["off_ramp_connections"]
        })
        
    return {
        "networks": summaries,
        "total": len(summaries)
    }

@router.get("/{network_id}", response_model=NetworkDetailResponse)
def get_network(network_id: str):
    _ensure_networks()
    net = _network_cache.get(network_id)
    if not net:
        raise HTTPException(status_code=404, detail="Network not found")
        
    return {
        "network_id": net["network_id"],
        "risk_level": "CRITICAL" if net["average_risk_score"] > 80 else ("HIGH" if net["average_risk_score"] > 60 else "MEDIUM"),
        "nodes": net["accounts"],
        "edges": net["total_transactions"],
        "total_amount": net["total_amount"],
        "banks_involved": net["banks"],
        "off_ramps": net["off_ramps"]
    }

@router.get("/{network_id}/graph", response_model=GraphResponse)
def get_network_graph(network_id: str, limit: int = 50):
    _ensure_networks()
    net = _network_cache.get(network_id)
    if not net:
        raise HTTPException(status_code=404, detail="Network not found")

    df = data_store.detection_df
    all_account_ids = net["accounts"]

    # Limit to top N accounts by risk score for render performance
    if len(all_account_ids) > limit:
        if df is not None and not df.empty:
            relevant = df[df['account_id'].isin(all_account_ids)].sort_values('risk_score', ascending=False)
            account_ids = relevant.head(limit)['account_id'].tolist()
        else:
            account_ids = all_account_ids[:limit]
    else:
        account_ids = all_account_ids

    # Precompute risk map for O(1) lookup
    risk_map = {}
    type_map = {}
    if df is not None and not df.empty:
        relevant_df = df[df['account_id'].isin(account_ids)]
        risk_map = dict(zip(relevant_df['account_id'], relevant_df['risk_score']))

    # Get account types from accounts_df
    acc_df = data_store.accounts_df
    if acc_df is not None:
        acc_subset = acc_df[acc_df['account_id'].isin(account_ids)]
        type_map = dict(zip(acc_subset['account_id'], acc_subset['account_type'].astype(str)))

    nodes = []
    edges = []
    added_nodes = set()

    query = """
    MATCH (a:Account)-[r:TRANSFER]->(b:Account)
    WHERE a.account_id IN $accounts AND b.account_id IN $accounts
    RETURN a.account_id AS source, b.account_id AS target,
           r.amount AS amount, r.timestamp AS timestamp,
           a.bank_id AS source_bank, b.bank_id AS target_bank
    LIMIT 500
    """
    results = gs.conn.query(query, {"accounts": account_ids})

    def get_risk(acc_id):
        return float(risk_map.get(acc_id, 0))

    def get_type(acc_id):
        return type_map.get(acc_id, 'CUSTOMER')

    def add_node(acc_id, bank_id):
        if acc_id not in added_nodes:
            nodes.append({
                "id": acc_id,
                "label": acc_id,
                "bank_id": bank_id,
                "risk_score": get_risk(acc_id),
                "account_type": get_type(acc_id)
            })
            added_nodes.add(acc_id)

    for res in results:
        add_node(res["source"], res["source_bank"])
        add_node(res["target"], res["target_bank"])
        edges.append({
            "source": res["source"],
            "target": res["target"],
            "amount": float(res["amount"]),
            "timestamp": str(res["timestamp"])
        })

    return {
        "nodes": nodes,
        "edges": edges
    }

@router.get("/{network_id}/money-trail", response_model=MoneyTrailResponse)
def get_network_money_trail(network_id: str, max_hops: int = 5):
    _ensure_networks()
    net = _network_cache.get(network_id)
    if not net:
        raise HTTPException(status_code=404, detail="Network not found")
        
    start_account = net["highest_risk_account"]
    
    # Use Phase 3 graph queries - get paths starting from highest risk account
    query = f"""
    MATCH p = (a:Account {{account_id: $start_account}})-[r:TRANSFER*1..{max_hops}]->(b:Account)
    RETURN p
    ORDER BY length(p) DESC
    LIMIT 1
    """
    results = gs.conn.query(query, {"start_account": start_account})
    
    trail = []
    if results:
        path = results[0]["p"]
        # path in neo4j driver is a Path object with nodes and relationships
        # We need to construct the trail
        nodes = path.nodes
        rels = path.relationships
        
        for i, rel in enumerate(rels):
            node = nodes[i+1] # The receiver of this hop
            trail.append({
                "hop": i,
                "account_id": node["account_id"],
                "bank_id": node.get("bank_id", ""),
                "amount": float(rel["amount"]),
                "timestamp": str(rel["timestamp"]),
                "transaction_id": rel.get("transaction_id", "")
            })
            
    return {
        "network_id": network_id,
        "trail": trail
    }

@router.get("/{network_id}/off-ramps", response_model=OffRampResponse)
def get_network_off_ramps(network_id: str):
    _ensure_networks()
    net = _network_cache.get(network_id)
    if not net:
        raise HTTPException(status_code=404, detail="Network not found")
        
    start_account = net["highest_risk_account"]
    
    # Use Phase 3 graph queries to find paths to off-ramps
    query = """
    MATCH p = (start:Account {account_id: $start_account})-[:TRANSFER*1..5]->(offramp:Account)
    WHERE offramp.account_type = 'OFF_RAMP'
    RETURN offramp.account_id AS off_ramp_account,
           [n in nodes(p) | n.account_id] AS path,
           [r in relationships(p) | r.amount] AS amounts,
           last(relationships(p)).transaction_id AS final_transaction_id,
           length(p) AS hop_count
    ORDER BY hop_count ASC
    LIMIT 10
    """
    results = gs.conn.query(query, {"start_account": start_account})
    
    off_ramps = []
    for res in results:
        off_ramps.append({
            "off_ramp_account": res["off_ramp_account"],
            "hop_count": res["hop_count"],
            "amount": sum(res["amounts"]) if res["amounts"] else 0.0,
            "path": res["path"],
            "final_transaction_id": res["final_transaction_id"]
        })
        
    return {
        "network_id": network_id,
        "off_ramps": off_ramps
    }
