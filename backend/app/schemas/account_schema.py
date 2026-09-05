from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class AccountBase(BaseModel):
    account_id: str
    bank_id: str
    account_type: str

class AccountListResponse(BaseModel):
    accounts: List[AccountBase]
    total: int
    page: int
    page_size: int

class AccountDetailResponse(AccountBase):
    risk_score: float
    risk_level: str
    is_suspicious: bool
    triggered_rules: List[str]
    explanations: List[str]

class NeighborAccount(BaseModel):
    account_id: str
    bank_id: str
    account_type: str
    direction: str
    amount: float
    transaction_id: str

class AccountNeighborsResponse(BaseModel):
    account_id: str
    neighbors: List[NeighborAccount]

class MLPredictionResponse(BaseModel):
    account_id: str
    ml_prediction: str
    mule_probability: float
    model: str
    features: Dict[str, Any]
