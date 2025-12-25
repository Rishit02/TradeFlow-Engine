from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from db.mysql import get_session
from services.order_service import OrderService
from schemas.order import OrderCreate, OrderOut

router = APIRouter(prefix="/orders", tags=["orders"])
service = OrderService()


@router.post("/", response_model=OrderOut)
async def create_order(
    order: OrderCreate, session: AsyncSession = Depends(get_session)
):
    """Create a new order"""
    try:
        result = await service.create_order(order, session)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/user/{user_id}", response_model=list)
async def get_user_orders(user_id: int, session: AsyncSession = Depends(get_session)):
    """Get all open orders for a user (cached)"""
    return await service.get_user_orders(user_id, session)


@router.get("/", response_model=list[OrderOut])
async def get_all_orders(session: AsyncSession = Depends(get_session)):
    """Get all orders"""
    orders = await service.get_all_orders(session)
    return orders


@router.get("/{order_id}", response_model=OrderOut)
async def get_order(order_id: int, session: AsyncSession = Depends(get_session)):
    """Get specific order"""
    repo = service.repo
    order = await repo.get_order_by_id(order_id, session)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
