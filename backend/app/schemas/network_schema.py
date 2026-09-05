from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class NetworkSummary(BaseModel):
    network_id: str
    risk_level: str
    accounts: int
    banks: int
    total_amount: float
    max_hops: int
    off_ramps: int

class NetworkListResponse(BaseModel):
    networks: List[NetworkSummary]
    total: int

class NetworkDetailResponse(BaseModel):
    network_id: str
    risk_level: str
    nodes: List[str]
    edges: int
    total_amount: float
    banks_involved: List[str]
    off_ramps: List[str]

class GraphNode(BaseModel):
    id: str
    label: str
    bank_id: str
    risk_score: float
    account_type: Optional[str] = 'CUSTOMER'

class GraphEdge(BaseModel):
    source: str
    target: str
    amount: float
    timestamp: str

class GraphResponse(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]

class MoneyTrailHop(BaseModel):
    hop: int
    account_id: str
    bank_id: str
    amount: float
    timestamp: str
    transaction_id: str

class MoneyTrailResponse(BaseModel):
    network_id: str
    trail: List[MoneyTrailHop]

class OffRampDetail(BaseModel):
    off_ramp_account: str
    hop_count: int
    amount: float
    path: List[str]
    final_transaction_id: str

class OffRampResponse(BaseModel):
    network_id: str
    off_ramps: List[OffRampDetail]
