# app/routes/orders.py
from fastapi import APIRouter
from schemas.order import OrderCreate, OrderOut
from services.order_service import OrderService

router = APIRouter()
service = OrderService()

@router.post("/", response_model=OrderOut)
async def create_order(order: OrderCreate):
    return await service.create_order(order)

@router.get("/user/{user_id}", response_model=list[OrderOut])
async def list_orders(user_id: int):
    return await service.get_user_orders(user_id)
