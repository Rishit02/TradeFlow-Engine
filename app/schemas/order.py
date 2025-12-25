from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal

class OrderCreate(BaseModel):
    user_id: int = Field(..., gt=0)
    item: str = Field(..., min_length=1, max_length=255)
    amount: Decimal = Field(..., gt=0)

class OrderUpdate(BaseModel):
    status: str = Field(...)

class OrderOut(BaseModel):
    id: int
    user_id: int
    item: str
    amount: Decimal
    status: str

    model_config = {"from_attributes": True}
