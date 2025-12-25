import json
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.order_repo import OrderRepository
from db.redis import redis_client
from db.kafka import producer

class OrderService:
    def __init__(self):
        self.repo = OrderRepository()

    async def create_order(self, order_data, session: AsyncSession):
        # 1. Save to DB
        order = await self.repo.create_order(order_data, session)
        await session.commit()

        # 2. Publish to Kafka
        if producer:
            event = {
                "event": "ORDER_PLACED",
                "order_id": order.id,
                "user_id": order.user_id,
                "item": order.item,
                "amount": str(order.amount),
                "status": order.status
            }
            await producer.send_and_wait("order.events", json.dumps(event).encode())

        # 3. Invalidate Redis cache
        await redis_client.delete(f"user:{order.user_id}:orders")

        return order

    async def get_user_orders(self, user_id: int, session: AsyncSession):
        cache_key = f"user:{user_id}:orders"

        # Try Redis first
        cached = await redis_client.get(cache_key)
        if cached:
            return json.loads(cached)

        # Fallback to DB
        orders = await self.repo.get_orders_by_user(user_id, session)
        order_dicts = [
            {
                "id": o.id,
                "user_id": o.user_id,
                "item": o.item,
                "amount": str(o.amount),
                "status": o.status
            }
            for o in orders
        ]

        # Cache result
        await redis_client.set(cache_key, json.dumps(order_dicts), ex=60)

        return order_dicts

    async def get_all_orders(self, session: AsyncSession):
        return await self.repo.get_all_orders(session)
