from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import Order

class OrderRepository:
    async def create_order(self, data, session: AsyncSession):
        order = Order(**data.model_dump())
        session.add(order)
        await session.flush()
        await session.refresh(order)
        return order

    async def get_order_by_id(self, order_id: int, session: AsyncSession):
        stmt = select(Order).where(Order.id == order_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_orders_by_user(self, user_id: int, session: AsyncSession):
        stmt = select(Order).where(Order.user_id == user_id, Order.status == "OPEN")
        result = await session.execute(stmt)
        return result.scalars().all()

    async def update_order_status(self, order_id: int, status: str, session: AsyncSession):
        order = await self.get_order_by_id(order_id, session)
        if order:
            order.status = status
            await session.flush()
            await session.refresh(order)
        return order

    async def get_all_orders(self, session: AsyncSession):
        stmt = select(Order)
        result = await session.execute(stmt)
        return result.scalars().all()
