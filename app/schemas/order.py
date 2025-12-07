# app/schemas/order.py
from pydantic import BaseModel

class OrderCreate(BaseModel):
    user_id: int
    item: str
    amount: float

class OrderOut(BaseModel):
    id: int
    item: str
    amount: float

    class Config:
        from_attributes = True
