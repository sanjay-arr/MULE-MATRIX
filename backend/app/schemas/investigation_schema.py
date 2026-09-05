from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class InvestigationCreate(BaseModel):
    account_id: Optional[str] = None
    network_id: Optional[str] = None

class InvestigationResponse(BaseModel):
    investigation_id: str
    account_id: str
    risk_score: float
    risk_level: str
    network_id: Optional[str]
    money_trail: List[Dict[str, Any]]
    connected_accounts: List[str]
    banks_involved: List[str]
    off_ramps: List[str]
    off_ramp_account: Optional[str] = None
    triggered_rules: List[str] = []
    evidence: List[str]

class InvestigationReportResponse(BaseModel):
    investigation_id: str
    summary: str
    risk_assessment: Dict[str, Any]
    network_analysis: Dict[str, Any]
    conclusion: str
