from pydantic import BaseModel
from typing import List, Optional

class TransactionBase(BaseModel):
    transaction_id: str
    sender: str
    receiver: str
    amount: float
    timestamp: str
    sender_bank: str
    receiver_bank: str

class TransactionListResponse(BaseModel):
    transactions: List[TransactionBase]
    total: int
    page: int
    page_size: int

class TransactionDetailResponse(TransactionBase):
    pass
