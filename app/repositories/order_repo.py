# app/repositories/order_repo.py
from db.mysql import SessionLocal
from models.order import Order


class OrderRepository:
    async def create_order(self, data):
        async with SessionLocal() as session:
            order = Order(**data.dict())
            session.add(order)
            await session.commit()
            await session.refresh(order)
            return order

    async def get_orders_by_user(self, user_id: int):
        async with SessionLocal() as session:
            result = await session.execute(
                select(Order).where(Order.user_id == user_id)
            )
            return result.scalars().all()
